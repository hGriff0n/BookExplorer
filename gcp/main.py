from flask import Flask
import logging

# TODO: Move the "gcloud" setup to a gcloud.py file (or something like that)
# Setup the stackdriver logging agent
import google.cloud.logging
stackdriver_logging_client = google.cloud.logging.Client()

# Connects the logger to the root logging handler; by default this captures
# all logs at INFO level and higher
stackdriver_logging_client.setup_logging()

# Setup the stackdriver error reporting agent
from google.cloud import error_reporting
stackdriver_error_client = error_reporting.Client()

# Setup the stackdriver debugger agent
try:
    import googleclouddebugger
    googleclouddebugger.enable()

except ImportError as exc:
    stackdriver_error_client.report_exception()

# Setup the stackdriver profiler agent
try:
    import googlecloudprofiler
    googlecloudprofiler.start(verbose=3)

except (ValueError, NotImplementedError) as exc:
    stackdriver_error_client.report_exception()

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
logging.info("Goodreads api: {} - {}".format(GOODREADS_API_KEY, GOODREADS_SECRET_VALUE))

# Initialize the goodreads client
import goodreads_api as goodreads
gc = goodreads.Client(GOODREADS_API_KEY, GOODREADS_SECRET_VALUE)

@app.route('/')
def hello():
    # stackdriver_error_client.report("An error has occurred")
    # return str(gc.book(isbn='978-0241351574'))
    return '<br>'.join(str(book) for book in gc.get_list(81192485))

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
