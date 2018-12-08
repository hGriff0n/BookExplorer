
import anyconfig
import requests
import xmltodict

class GoodreadsBook:
    def __init__(self, goodreads_book):
        self._book_info = goodreads_book
        # odict_keys(['id', 'isbn', 'isbn13', 'text_reviews_count', 'uri', 'title', 'title_without_series', 'image_url', 'small_image_url', 'large_image_url', 'link', 'num_pages', 'format', 'edition_information', 'publisher', 'publication_day', 'publication_year', 'publication_month', 'average_rating', 'ratings_count', 'description', 'authors', 'published', 'work'])

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
    for book in res['book']:
        yield GoodreadsBook(book)

    current_page = 1
    num_pages_in_list = int(res['@numpages'])
    while current_page < num_pages_in_list:
        current_page += 1
        resp = requests.get(list_url_format.format(shelf_id, current_page), params=api_params)
        for book in xmltodict.parse(resp.content)['GoodreadsResponse']['books']['book']:
            yield GoodreadsBook(book)

def generate_book_filter(filter_list):
    """
    Produces the filter function to remove specific books from the goodreads feed
    """
    books = list(entry['title'] for entry in filter_list if ('title' in entry))

    def _book_filter(book):
        book_found_in_filter_list = book.title in books
        return not book_found_in_filter_list
    return _book_filter


conf = anyconfig.load("conf.yaml")
api_key = conf.get('api_key')

filter_list = conf.get('filter', [])
shelves = conf.get('shelves', [])

with open("book_list.txt", 'w') as f:
    book_filter = generate_book_filter(filter_list)

    for shelf in shelves:
        for book in filter(book_filter, list_books_in_shelf(shelf, api_key)):
            f.write("{}\n  {}\n".format(book.title, book.url))


# TODO: Figure out how to filter shelves (ie. don't include any books that appear on this shelf)
# TODO: Improve filtering to allow for removing individual books based on author, etc.
