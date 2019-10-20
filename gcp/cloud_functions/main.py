# import base64
# import json
import collections
import goodreads_api as goodreads
from google.cloud import firestore

# Initialize the firestore and goodreads clients
db = firestore.Client()
config = db.collection('configuration')
api_keys = config.document('api_keys').get().to_dict()
tests = config.document('tests').get().to_dict()
choices = config.document('choices').get().to_dict()

GOODREADS_API_KEY = api_keys['goodreads']['API_KEY']
GOODREADS_SECRET_VALUE = api_keys['goodreads']['SECRET']
gc = goodreads.Client(GOODREADS_API_KEY, GOODREADS_SECRET_VALUE)


def sanitize_isbn(isbn, title):
    if isinstance(isbn, collections.OrderedDict):
        print("Sanitizing isbn for book `{}` as it is an ordered dict".format(title))
        return None
    return str(isbn)

def sanitize_desc(desc):
    if desc is None:
        return desc

    cleanr = re.compile('<.*?>')
    return re.sub(cleanr, '', desc)


def precompute_sampler(_event, _context):
    """
    Sample the data which needs to be precomputed and push it to the precompute function
    """
    isbns = [(sanitize_isbn(book.isbn, book.title), book.description) for book in gc.get_list(81192485)]
    for isbn in tests['items']:
        book = gc.book(isbn=isbn)
        isbn = sanitize_isbn(isbn, book.title)
        isbns.append((isbn, book.description))
    for isbn in choices['isbn']:
        book = gc.book(isbn=isbn)
        isbn = sanitize_isbn(isbn, book.title)
        isbns.append((isbn, book.description))

    # Write the data to firestore to see that it's working
    # TODO(eventually): Write to pubsub topic instead
    for isbn, desc in filter(lambda n: n is not None, isbns):
        config.document('all').set({isbn: sanitize_desc(desc)}, merge=True)
