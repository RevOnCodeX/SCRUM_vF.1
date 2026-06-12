import os
from firebase_functions import https_fn
from firebase_admin import initialize_app

# The Firebase SDK might already be initialized by firebase_setup,
# but Firebase Functions requires it to be cleanly initialized in the runtime.
try:
    initialize_app()
except ValueError:
    pass # Already initialized

# Set environment variables for serverless execution before importing app
os.environ["TEAM_TRACKER_DB_PATH"] = "/tmp/team_tracker.db"
os.environ["TEAM_TRACKER_PRODUCTION"] = "1"

# Import the Flask app factory
from app import create_app
from firestore_sync import init_sync_engine

# Initialize Flask
flask_app = create_app()

# Initialize sync engine for the temporary serverless storage
init_sync_engine("/tmp/team_tracker.db")

@https_fn.on_request()
def scrum_board(req: https_fn.Request) -> https_fn.Response:
    with flask_app.request_context(req.environ):
        return flask_app.full_dispatch_request()
