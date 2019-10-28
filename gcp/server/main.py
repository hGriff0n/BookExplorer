from flask import Flask
import gcloud
import goodreads_api as goodreads
from google.cloud import firestore
import logging
# import tensorflow as tf
# import tensorflow_hub as tf_hub

# Cause "noqa" is apparently disabled
assert gcloud
assert logging

# Setup the database client
db = firestore.Client()

# Specify the server
app = Flask(__name__)

# Install the tensorflow module
# embed_module = tf_hub.Module("https://tfhub.dev/google/universal-sentence-encoder/2")
# placeholder = tf.placeholder(dtype=tf.string)
# embed = embed_module(placeholder)
# session = tf.Session()
# session.run([tf.global_variables_initializer(), tf.tables_initializer()])

# Read configuration from the database
# TODO: Is there a better way of accesing this?
config = db.collection('configuration')
api_keys = config.document('api_keys').get().to_dict()

GOODREADS_API_KEY = api_keys['goodreads']['API_KEY']
GOODREADS_SECRET_VALUE = api_keys['goodreads']['SECRET']

# Initialize the goodreads client
gc = goodreads.Client(GOODREADS_API_KEY, GOODREADS_SECRET_VALUE)

# Get the selection set that we are choosing from
# TODO: Allow for per-user lists
# selections = config.document('choices').get().to_dict()['isbn']
# For developing the algorithm use the below line, for "production" - above
selections = config.document('tests').get().to_dict()['items']
selections = [gc.book(isbn=isbn) for isbn in selections]


# TODO: Move this development to a local script (don't have to worry about timeout)
# Doesn't work on:
#  AppEngine Standard: TF is a native library, not allowed on standard instances
#  
# TODO: Try producing an embedding from the url (might have to custom timeout)
# TODO: Try loading from gcs to improve speed (might have to custom timeout)
@app.route('/')
def hello():
    # return str(session.run(tf.constant('Hello World')))
    # return str(session.run(embed, feed_dict={placeholder: "Hello, Tensorflow"}))
    # return '<br>'.join(compute_embedding(gc.book(isbn='978-0241351574')))
    # gcloud.error_client.report("An error has occurred")
    return str(gc.book(isbn='978-0241351574'))
    # return '<br>'.join(str(book) for book in gc.get_list(81192485))
    # return '<br>'.join(str(book) for book in selections)


@app.route("/readiness_check")
def ready():
    return 'Ready'


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
