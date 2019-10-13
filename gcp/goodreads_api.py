
import goodreads
import goodreads.book
import goodreads.client


class GoodreadsList:
    def __init__(self, client, shelf_id):
        self._client = client
        self._api_path = "review/list/{}/?page={{}}".format(shelf_id)
    
    def __iter__(self):
        """
        Lazily query the goodreads api to extract all information about books in this shelf
        """
        current_page = 0
        max_pages = 1
        while current_page < max_pages:
            current_page += 1
            shelf = self._client.request(self._api_path.format(current_page), self._client.query_dict)['books']

            for book in shelf['book']:
                yield goodreads.book.GoodreadsBook(book, self._client)
            
            max_pages = int(shelf['@numpages'])


class Client(goodreads.client.GoodreadsClient):

    def get_list(self, shelf_id):
        return GoodreadsList(self, shelf_id)