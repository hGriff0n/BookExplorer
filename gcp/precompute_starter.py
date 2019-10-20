# import base64
# import json
import goodreads_api as goodreads
from google.cloud import firestore

# Initialize the firestore and goodreads clients
db = firestore.Client()
config = db.collection('configuration')
api_keys = config.document('api_keys').get().to_dict()
tests = config.document('tests').get().to_dict()

GOODREADS_API_KEY = api_keys['goodreads']['API_KEY']
GOODREADS_SECRET_VALUE = api_keys['goodreads']['SECRET']
gc = goodreads.Client(GOODREADS_API_KEY, GOODREADS_SECRET_VALUE)


def hello_pubsub(_event, _context):
    """Triggered from a message on a Cloud Pub/Sub topic.
    Args:
         event (dict): Event payload.
         context (google.cloud.functions.Context): Metadata for the event.
    """
    isbns = [(book.isbn, book.description) for book in gc.get_list(81192485)]
    isbns.extend(
        (isbn, gc.book(isbn=isbn).description) for isbn in tests['items']
    )

    # Write the data to firestore to see that it's working
    # TODO(eventually): Write to pubsub topic instead
    for isbn, desc in isbns.items():
        config.document('all').set({isbn: desc}, merge=True)
