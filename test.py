
import anyconfig
import datetime
import json
import re

from goodreads_frontend.api import BookShelf

class GoodreadsClient:
    def __init__(self, api_key):
        self._params = {'key': api_key}

    def shelf(self, shelf_id):
        return BookShelf(self, shelf_id)

    @property
    def params(self):
        return self._params.copy()


def generate_book_filter(filter_list):
    """
    Produces the filter function to remove specific books from the goodreads feed
    """
    filtered_titles = list(entry['title'] for entry in filter_list if ('title' in entry))

    def _book_filter(book):
        book_has_no_description = book.description is None
        book_filtered_by_title = book.title in filtered_titles
        return not (book_filtered_by_title or book_has_no_description)

    return _book_filter


def delete_nulls_from_dict(d):
    for key in list(d.keys()):
        if d[key] is None:
            del d[key]

def delete_keys_from_dict(d, *args):
    for k in args:
        if k in d:
            del d[k]

def default_encoder(obj):
    if isinstance(obj, datetime.date):
        return obj.isoformat()
    return str(obj)


def produce_test_data(out, client, shelf_list, filter_list):
    book_filter = generate_book_filter(filter_list)
    all_books = []

    num_seen_books = 0
    html_stripper = re.compile('<.*?>')
    series_stripper = re.compile(r' *((\()|\)|((, *)?#\d+(-\d+)?)) *')
    # url_stripper = re.compile('https?:\/\/\S+')

    def _augment_book(book):
        delete_nulls_from_dict(book)
        delete_keys_from_dict(book, 'small_image_url', 'average_rating', 'uri', 'work', 'ratings_count', 'text_reviews_count')
        book['description'] = re.sub(html_stripper, '', book['description'])

        isbn = book['isbn']
        if not (isinstance(isbn, str) or (isinstance(isbn, dict) and not isbn.get('@nil', False))):
            del book['isbn']

        isbn = book['isbn13']
        if not (isinstance(isbn, str) or (isinstance(isbn, dict) and not isbn.get('@nil', False))):
            del book['isbn13']

        book['num_pages'] = int(book.get('num_pages', -1))

        bid = book['id']
        if bid['@type'] == 'integer':
            book['id'] = bid['#text']

        if len(book['authors'].keys()) == 1:
            author = book['authors']['author']
            delete_nulls_from_dict(author)
            delete_keys_from_dict(author, 'small_image_url', 'id', 'average_rating', 'ratings_count', 'text_reviews_count')

            img = author['image_url']
            if img['@nophoto'] == 'false':
                author['image_url'] = img['#text']
            else:
                del author['image_url']

            book['author'] = author
            del book['authors']

        if book['title'] != book['title_without_series']:
            book['series'] = book['title'].replace(book['title_without_series'], '', 1)
            book['series'] = re.sub(series_stripper, '', book['series'])
            book['title'] = book['title_without_series']
        del book['title_without_series']

        if 'published' in book:
            book['published'] = datetime.date(
                year=int(book['publication_year']),
                month=int(book.get('publication_month', 1)),
                day=int(book.get('publication_day', 1))
            )
            delete_keys_from_dict(book, 'publication_year', 'publication_month', 'publication_day')

        nonlocal num_seen_books
        book['index'] = num_seen_books
        num_seen_books += 1

        return book

    for shelf_id in shelf_list:
        all_books.extend(_augment_book(book.get_ir()) for book in filter(book_filter, client.shelf(shelf_id)))

    # TODO: Filter out fiction and non-fiction by a config dictionary
    def _produce_data_sets(all_books):
        return { 'all_books': all_books }

    out.write(json.dumps(_produce_data_sets(all_books), sort_keys=True, indent=4, default=default_encoder))


# TODO: Clean up the code a bit more
# TODO: Might want to remove the goodreads api wrappers (don't use them at all)
# TODO: Add in fiction sorting through a config list for now
conf = anyconfig.load("conf.yaml")
filter_list = conf.get('filter', [])
shelves = conf.get('shelves', [])

gc = GoodreadsClient(conf.get('api_key'))

import os
book_list = os.path.join("test_data", "goodreads_books.json")
if not os.path.exists("test_data"):
    os.mkdir("test_data")
with open(book_list, 'w') as f:
    produce_test_data(f, gc, shelves, filter_list)



# NOTE: These aren't necessary for me and the development purposes, but would be necessary for any general use case
# TODO: Figure out how to filter shelves (ie. don't include any books that appear on this shelf)
# TODO: Improve filtering to allow for removing individual books based on author, etc.
