import goodreads
import goodreads.book
import goodreads.client
import goodreads.request


class BookShelf:
    def __init__(self, client, shelf_id):
        self._client = client
        self._path = "review/list/{}/?page={{}}".format(shelf_id)

    def __iter__(self):
        """
        Lazily query the goodreads api to extract all information about books in this shelf
        """
        current_page = 0
        max_pages = 1
        while current_page < max_pages:
            current_page += 1
            shelf = self._client.request(self._path.format(current_page), self._client.query_dict)['books']

            for book in shelf['book']:
                yield goodreads.book.GoodreadsBook(book, self._client)

            max_pages = int(shelf['@numpages'])

class GoodreadsClient(goodreads.client.GoodreadsClient):

    def get_list(self, shelf_id):
        return BookShelf(self, shelf_id)

gc = GoodreadsClient('<api_key>', '<api_secret>')
# gc.authenticate(<access_Token>, <access_token_secret>)

book = gc.book(isbn='978-0241351574')
print(book)

shelf_id = 0
shelf = iter(gc.get_list(shelf_id))
print(next(shelf))
