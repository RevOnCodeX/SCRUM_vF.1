import os
import sys

# Ensure the parent directory is explicitly in the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from firestore_sync import init_sync_engine

app = create_app()

# For Vercel, the only writable directory is /tmp
db_path = "/tmp/team_tracker.db"
app.config["DB_PATH"] = db_path
init_sync_engine(db_path)
