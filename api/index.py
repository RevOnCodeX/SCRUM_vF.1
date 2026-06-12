import os
import sys

# For Vercel, the only writable directory is /tmp
# We MUST set this environment variable BEFORE calling create_app()
# so that the internal init_db() doesn't try to write to the read-only /var/task/data folder!
os.environ["TEAM_TRACKER_DB_PATH"] = "/tmp/team_tracker.db"

# Ensure the parent directory is explicitly in the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from firestore_sync import init_sync_engine

app = create_app()

init_sync_engine("/tmp/team_tracker.db")
