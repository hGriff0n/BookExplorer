
import anyconfig
import json

from goodreads_frontend import BookShelf

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
        book_filtered_by_title = book.title in filtered_titles
        return not book_filtered_by_title
    return _book_filter


def produce_test_data(out, client, shelf_list, filter_list):
    book_filter = generate_book_filter(filter_list)
    all_books = []

    def _to_json(book):
        return {'title': book.title, 'author': book.author, 'desc': book.description, 'url': book.url, 'isbn': book.isbn, 'id': book.id}

    for shelf_id in shelf_list:
        all_books.extend(_to_json(book) for book in filter(book_filter, client.shelf(shelf_id)))

    out.write(json.dumps(all_books, sort_keys=True, indent=4))


conf = anyconfig.load("conf.yaml")
filter_list = conf.get('filter', [])
shelves = conf.get('shelves', [])

gc = GoodreadsClient(conf.get('api_key'))

import os
book_list = os.path.join("test_data", "books.json")
if not os.path.exists("test_data"):
    os.mkdir("test_data")
with open(book_list, 'w') as f:
    produce_test_data(f, gc, shelves, filter_list)

# NOTE: These aren't necessary for me and the development purposes, but would be necessary for any general use case
# TODO: Figure out how to filter shelves (ie. don't include any books that appear on this shelf)
# TODO: Improve filtering to allow for removing individual books based on author, etc.
