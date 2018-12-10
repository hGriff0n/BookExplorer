
import anyconfig
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


def produce_test_data(out, client, shelf_list, filter_list):
    book_filter = generate_book_filter(filter_list)
    all_books = []

    html_stripper = re.compile('<.*?>')
    # url_stripper = re.compile('https?:\/\/\S+')

    def _to_json(book):
        isbn = book.isbn
        desc = re.sub(html_stripper, '', book.description)

        json_dict =  {'title': book.title, 'author': book.author, 'desc': desc, 'url': book.url, 'id': book.id}
        if isinstance(isbn, str) or (isinstance(isbn, dict) and not isbn.get('@nil', False)):
            json_dict['isbn'] = isbn

        return json_dict

    for shelf_id in shelf_list:
        all_books.extend(_to_json(book) for book in filter(book_filter, client.shelf(shelf_id)))

    out.write(json.dumps(all_books, sort_keys=True, indent=4))


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
