
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import anyconfig
import json
import goodreads
import goodreads.book
import goodreads.client
import re

import warnings
with warnings.catch_warnings():
    warnings.filterwarnings("ignore",category=FutureWarning)
    import tensorflow as tf
    import tensorflow_hub as tf_hub


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


conf = anyconfig.load("conf.yaml")
GOODREADS_API_KEY = conf.get('api_key')
GOODREADS_SECRET = conf.get('api_secret')

gc = Client(GOODREADS_API_KEY, GOODREADS_SECRET)

# TODO: How to reduce logging from tensorflow?
tf.logging.set_verbosity(tf.logging.ERROR)
embed_module = tf_hub.Module("https://tfhub.dev/google/universal-sentence-encoder/2")
print("downloaded module")

placeholder = tf.placeholder(dtype=tf.string)
embed = embed_module([placeholder])
print("construct module with placeholder")

# Get all the book information
# NOTE: This has to be run before the tf Session because an SSLError occurs otherwise (why? IDK)
# TODO: Should probably cache all of this information
strip_html = re.compile(r'<.*?>')
books = {}
for book in gc.get_list(81192485):
    if book.title == 'Confucius And The Chinese Way':
        continue
    try:
        books[book.isbn13.replace('-', '')] = (book.title, strip_html.sub('', book.description))
    except Exception as e:
        print("error on book: {} ({})".format(book.title, e))

# Produce the samples for testing
# TODO: readlines has '\n' on it
with open('data/samples.csv') as f:
    samples = [isbn[:-1].replace('-', '') for isbn in f]

# Produce data for the choices
choices = {}
with open('data/choices.csv') as f:
    for isbn in f:
        book = gc.book(isbn=isbn[:-1].replace('-', ''))
        try:
            choices[book.isbn13.replace('-', '')] = (book.title, strip_html.sub('', book.description))
        except Exception as e:
            print("error on book: {} ({})".format(book.title, e))
print("downloaded book corpus")

session = tf.Session()
session.run([tf.global_variables_initializer(), tf.tables_initializer()])
print("setup tf session")

# Produce the embeddings
for isbn in books:
    books[isbn] = (books[isbn][0], session.run(embed, feed_dict={placeholder: books[isbn][1]}))
for isbn in choices:
    choices[isbn] = (choices[isbn][0], session.run(embed, feed_dict={placeholder: choices[isbn][1]}))

import numpy
from numpy.linalg import norm

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, numpy.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)

with open('data/cache.json', 'w') as f:
    json.dump({'books': books, 'choices': choices}, f, cls=NumpyEncoder)


def cosine_similarity(a, b):
    a = numpy.array(a)
    b = numpy.array(b)
    return numpy.inner(a, b)/(norm(a)*norm(b))

book1 = books[samples[0]]
book2 = books[samples[1]]
print("{} v {} = {}".format(book1[0], book2[0], cosine_similarity(book1[1], book2[1])))
