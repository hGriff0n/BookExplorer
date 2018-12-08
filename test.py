
# TODO: Roll custom goodreads api
    # Books: isbn/isbn13, uri/id, title/title_without_series, author, description
# TODO: Make list configurable (allow for appending/filtering other lists)
import anyconfig
import requests
import xmltodict

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
    for book in res['book']:
        yield book

    while current_page < num_pages_in_list:
        current_page += 1
        resp = requests.get(list_url_format.format(shelf_id, current_page), params=api_params)
        for book in xmltodict.parse(resp.content)['GoodreadsResponse']['books']['book']:
            yield book


conf = anyconfig.load("conf.yaml")
api_key = conf.get('api_key')

with open("book_list.txt", 'w') as f:
    for shelf in conf.get('shelves', []):
        for book in list_books_in_shelf(shelf, api_key):
            f.write(book['title_without_series'] + '\n')

# TODO: Add "filter list" to config file (books goodreads lists as owned, but should not be considered as owned)


# resp = requests.get("https://www.goodreads.com/review/list/81192485?page=2&format=xml", params={'key': API_KEY})

# res = xmltodict.parse(resp.content)['GoodreadsResponse']['books']
# books = res['book']
# print(list(book['title'] for book in books))
# TODO: Goodreads may not be an effective method for producing recommendations
# It's perfect for mapping what I already have, but for what I don't know, it's very difficult to get topics
