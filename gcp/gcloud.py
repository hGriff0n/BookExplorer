
# Setup the stackdriver logging agent
import google.cloud.logging
logging_client = google.cloud.logging.Client()

# Connects the logger to the root logging handler; by default this captures
# all logs at INFO level and higher
# NOTE: There's a bit of a delay before log messages become visible in the logs viewer
logging_client.setup_logging()


# Setup the stackdriver error reporting agent
from google.cloud import error_reporting
error_client = error_reporting.Client()


# Setup the stackdriver debugger agent
# TODO: Is this actually working? Breakpoints and logpoints don't seem to be hit
try:
    import googleclouddebugger
    googleclouddebugger.enable()

except ImportError as exc:
    error_client.report_exception()


# Setup the stackdriver profiler agent
# TODO: Is `verbose=3` the right setting?
try:
    import googlecloudprofiler
    googlecloudprofiler.start(verbose=3)

except (ValueError, NotImplementedError):
    error_client.report_exception()