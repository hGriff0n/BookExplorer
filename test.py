
import anyconfig
import requests
import xmltodict

class GoodreadsBook:
    def __init__(self, goodreads_book):
        self._book_info = goodreads_book

    @property
    def isbn(self):
        return self._book_info['isbn']

    @property
    def isbn13(self):
        return self._book_info['isbn13']

    @property
    def title(self):
        return self._book_info['title_without_series']

    @property
    def url(self):
        return self._book_info['link']

    @property
    def author(self):
        return self._book_info['authors']

    @property
    def description(self):
        return self._book_info['description']

    def get_internal_representation(self):
        return self._book_info

def list_books_in_shelf(shelf_id, api_key):
    """
    Generator to lazily return all books in a given shelf (by id)

    TODO: Should probably wrap the returned books in a 'Book' object
    """
    list_url_format = r"https://goodreads.com/review/list/{}/?page={}&format=xml"
    api_params = {'key': api_key}

    resp = requests.get(list_url_format.format(shelf_id, 1), params=api_params)
    res = xmltodict.parse(resp.content)['GoodreadsResponse']['books']

    current_page = 1
    num_pages_in_list = int(res['@numpages'])
    print(res['book'][0].keys())
    for book in res['book']:
        yield GoodreadsBook(book)

    while current_page < num_pages_in_list:
        current_page += 1
        resp = requests.get(list_url_format.format(shelf_id, current_page), params=api_params)
        for book in xmltodict.parse(resp.content)['GoodreadsResponse']['books']['book']:
            yield GoodreadsBook(book)


conf = anyconfig.load("conf.yaml")
api_key = conf.get('api_key')

with open("book_list.txt", 'w') as f:
    for shelf in conf.get('shelves', []):
        for book in list_books_in_shelf(shelf, api_key):
            f.write("{}\n  {}\n".format(book.title, book.url))

# TODO: Add "filter list" to config file (books goodreads lists as owned, but should not be considered as owned)
    # Should be able to filter specific books, or give a shelf id and filter any books that appear on the shelf
