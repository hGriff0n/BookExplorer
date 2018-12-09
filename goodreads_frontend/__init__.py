
import requests
import xmltodict

class ShelvedBook:
    """
    All keys available in the internal representation:
    'id', 'isbn', 'isbn13', 'text_reviews_count', 'uri', 'title', 'title_without_series', 'image_url', 'small_image_url', 'large_image_url', 'link', 'num_pages', 'format',
    'edition_information', 'publisher', 'publication_day', 'publication_year', 'publication_month', 'average_rating', 'ratings_count', 'description', 'authors', 'published', 'work'
    """
    def __init__(self, goodreads_book):
        self._book_info = goodreads_book

    @property
    def id(self):
        return self._book_info['id']['#text']

    @property
    def isbn(self):
        # NOTE: This may not be a string
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
        return self._book_info['authors']['author']['name']

    @property
    def description(self):
        return self._book_info['description']

    def get_internal_representation(self):
        return self._book_info


# TODO: Improve this class to optimize network usage
# TODO: The "requesting" should probably be handled by a single `Communicator` object
class BookShelf:
    def __init__(self, client, shelf_id):
        self._client = client
        self._url_format_str = "https://goodreads.com/review/list/{}/?page={{}}&format=xml".format(shelf_id)

    def __iter__(self):
        """
        Lazily query the goodreads api to extract the information about all books in this shelf
        """
        current_page = 1
        resp = requests.get(self._url_format_str.format(current_page), params=self._client.params)
        res = xmltodict.parse(resp.content)['GoodreadsResponse']['books']
        for book in res['book']:
            yield ShelvedBook(book)

        num_pages_in_shelf_list = int(res['@numpages'])
        while current_page < num_pages_in_shelf_list:
            current_page += 1
            resp = requests.get(self._url_format_str.format(current_page), params=self._client._params)
            for book in xmltodict.parse(resp.content)['GoodreadsResponse']['books']['book']:
                yield ShelvedBook(book)
