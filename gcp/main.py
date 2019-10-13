from flask import Flask
import gcloud
import logging

# Setup the database client
from google.cloud import firestore
db = firestore.Client()

# Specify the server
app = Flask(__name__)

# Read configuration from the databasae
config = db.collection('configuration')
# TODO: Is there a better way of accesing this?
api_keys = config.document('api_keys').get().to_dict()

GOODREADS_API_KEY = api_keys['goodreads']['API_KEY']
GOODREADS_SECRET_VALUE = api_keys['goodreads']['SECRET']

# Initialize the goodreads client
import goodreads_api as goodreads
gc = goodreads.Client(GOODREADS_API_KEY, GOODREADS_SECRET_VALUE)

# Get the selection set that we are choosing from
# TODO: Allow for per-user lists
selections = [gc.book(isbn=isbn) for isbn in config.document('choices').get().to_dict()['isbn']]
# For developing the algorithm use the above line, for "production" use the above line
# selecctions = []

@app.route('/')
def hello():
    # gcloud.error_client.report("An error has occurred")
    # return str(gc.book(isbn='978-0241351574'))
    # return '<br>'.join(str(book) for book in gc.get_list(81192485))
    return '<br>'.join(str(book) for book in choices)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
