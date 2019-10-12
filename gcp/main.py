from flask import Flask
import logging

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

# Specify the server
app = Flask(__name__)

@app.route('/')
def hello():
    # stackdriver_error_client.report("An error has occurred")
    return 'Hello World2'

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
