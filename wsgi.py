"""WSGI entry for Gunicorn / production hosts: `gunicorn wsgi:app`."""
import os
import sys

# Ensure the app directory is explicitly in the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app import create_app
from firestore_sync import init_sync_engine

app = create_app()

db_path = app.config.get("DB_PATH", "data/team_tracker.db")
init_sync_engine(str(db_path))
