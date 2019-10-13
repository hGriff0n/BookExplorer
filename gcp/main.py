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
api_keys = config.document('api_keys').get()

api_keys = api_keys.to_dict()
GOODREADS_API_KEY = api_keys['GOODREADS_API_KEY']
GOODREADS_SECRET_VALUE = api_keys['GOODREADS_API_SECRET']

# Initialize the goodreads client
import goodreads_api as goodreads
gc = goodreads.Client(GOODREADS_API_KEY, GOODREADS_SECRET_VALUE)

try:
    open('../choices.csv')
except Exception:
    gcloud.error_client.report_exception()

@app.route('/')
def hello():
    # gcloud.error_client.report("An error has occurred")
    # return str(gc.book(isbn='978-0241351574'))
    return '<br>'.join(str(book) for book in gc.get_list(81192485))

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
