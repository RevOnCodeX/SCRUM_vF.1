import sys
import os

app_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'app.py')

with open(app_path, 'r', encoding='utf-8') as f:
    content = f.read()

old_get_db = """def get_db(app: Flask) -> sqlite3.Connection:
    p = _db_path(app)
    p.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(p)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn"""

new_get_db = """def get_db(app: Flask) -> sqlite3.Connection:
    p = _db_path(app)
    p.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        from firestore_sync import init_sync_engine
        init_sync_engine(str(p))
    except Exception as e:
        print(f"Firestore Sync Init Error: {e}")
        
    conn = sqlite3.connect(p)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn"""

old_flask = "    app = Flask(__name__)"
new_flask = """    app = Flask(__name__)

    @app.after_request
    def process_firestore_sync(response):
        try:
            from firestore_sync import get_sync_engine
            engine = get_sync_engine()
            if engine:
                engine.process_queue()
        except Exception as e:
            pass
        return response"""

if old_get_db in content:
    content = content.replace(old_get_db, new_get_db)
    print("Patched get_db")
else:
    print("Could not find get_db")

if old_flask in content:
    content = content.replace(old_flask, new_flask)
    print("Patched Flask setup")
else:
    print("Could not find Flask setup")

with open(app_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Done patching.")
