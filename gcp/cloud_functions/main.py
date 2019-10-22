# import base64
# import json
import collections
import goodreads_api as goodreads
from google.cloud import firestore
from google.cloud import pubsub_v1
import json
import re
import tensorflow as tf
import tensorflow_hub as tf_hub

# Start the caching of the tensorflow data set
embed_module = tf_hub.Module("https://tfhub.dev/google/universal-sentence-encoder/2")

# Initialize the firestore and goodreads clients
db = firestore.Client()
config = db.collection('configuration')
api_keys = config.document('api_keys').get().to_dict()
tests = config.document('tests').get().to_dict()
choices = config.document('choices').get().to_dict()

# Initialize the goodreads client
GOODREADS_API_KEY = api_keys['goodreads']['API_KEY']
GOODREADS_SECRET_VALUE = api_keys['goodreads']['SECRET']
gc = goodreads.Client(GOODREADS_API_KEY, GOODREADS_SECRET_VALUE)

# Initialize the pubsub publisher
publisher = pubsub_v1.PublisherClient()
pubsub_futures = {}


def get_pubsub_failure_callback(f, data):
    def callback(f):
        try:
            print(f.result())
            pubsub_futures.pop(data.keys()[0])
        except:  # noqa
            print('Please handle {} for {}.'.format(f.exception(), data))

    return callback


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


def publish(message, topic_path):
    future = publisher.publish(topic_path, data=json.dumps(message).encode('utf-8'))
    future.add_done_callback(get_pubsub_failure_callback(future, message))
    return future


# Prepare the tensorflow embedding flow
placeholder = tf.placeholder(dtype=tf.string)
embed = embed_module(placeholder)


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
    # topic_path = publisher.topic_path('bookexplorer', 'precompute-embeddings-queue')
    session = tf.Session()
    session.run([tf.global_variables_initializer(), tf.tables_initializer()])
    for isbn, desc in filter(lambda n: n is not None, isbns):
        # pubsub_futures[isbn] = publish({isbn: sanitize_desc(desc)}, topic_path)
        descript = sanitize_desc(desc)
        # config.document('all').set({isbn: descript}, merge=True)
        config.document('embed').set({
            isbn: session.run(embed, feed_dict={placeholder: descript})
        })
