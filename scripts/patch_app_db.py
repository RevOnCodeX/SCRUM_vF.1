import sys
import os

app_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'app.py')

with open(app_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace get_db
old_get_db = """def get_db(app: Flask) -> sqlite3.Connection:
    if "db" not in g:
        g.db = sqlite3.connect(app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
    conn = g.db"""

new_get_db = """def get_db(app: Flask) -> sqlite3.Connection:
    if "db" not in g:
        db_path = app.config["DATABASE"]
        g.db = sqlite3.connect(db_path)
        g.db.row_factory = sqlite3.Row
        try:
            from firestore_sync import init_sync_engine
            init_sync_engine(db_path)
        except Exception as e:
            print(f"Failed to init Firestore sync: {e}")
    conn = g.db"""

if old_get_db in content:
    content = content.replace(old_get_db, new_get_db)
    print("Replaced get_db")
else:
    print("Warning: Could not find old_get_db snippet in app.py")

# Replace close_db
old_close_db = """def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()"""

new_close_db = """def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        try:
            from firestore_sync import get_sync_engine
            engine = get_sync_engine()
            if engine:
                engine.process_queue()
        except Exception as ex:
            print(f"Error processing Firestore queue: {ex}")
        db.close()"""

if old_close_db in content:
    content = content.replace(old_close_db, new_close_db)
    print("Replaced close_db")
else:
    print("Warning: Could not find old_close_db snippet in app.py")

with open(app_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Patch applied successfully.")
