import sqlite3
import threading
import time
from firebase_setup import get_db

class FirestoreSyncEngine:
    def __init__(self, db_path='data/team_tracker.db'):
        self.db_path = db_path
        self.firestore_db = get_db()
        self.sync_lock = threading.Lock()
        
    def setup_triggers(self):
        """Create a sync queue table and triggers for all user tables."""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        
        # Create sync queue
        cur.execute('''
            CREATE TABLE IF NOT EXISTS _sync_queue (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                table_name TEXT,
                row_id TEXT,
                operation TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Get all tables
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' AND name != '_sync_queue'")
        tables = [r[0] for r in cur.fetchall()]
        
        # Create triggers for each table
        for table in tables:
            # We need to know the primary key to sync correctly.
            # In this app, almost all tables have an 'id' column.
            cur.execute(f"PRAGMA table_info({table})")
            columns = [c[1] for c in cur.fetchall()]
            
            if 'id' not in columns:
                continue # Skip tables without an id column for now
                
            # INSERT TRIGGER
            cur.execute(f'''
                CREATE TRIGGER IF NOT EXISTS sync_{table}_insert 
                AFTER INSERT ON {table}
                BEGIN
                    INSERT INTO _sync_queue (table_name, row_id, operation) VALUES ('{table}', NEW.id, 'INSERT');
                END;
            ''')
            
            # UPDATE TRIGGER
            cur.execute(f'''
                CREATE TRIGGER IF NOT EXISTS sync_{table}_update 
                AFTER UPDATE ON {table}
                BEGIN
                    INSERT INTO _sync_queue (table_name, row_id, operation) VALUES ('{table}', NEW.id, 'UPDATE');
                END;
            ''')
            
            # DELETE TRIGGER
            cur.execute(f'''
                CREATE TRIGGER IF NOT EXISTS sync_{table}_delete 
                AFTER DELETE ON {table}
                BEGIN
                    INSERT INTO _sync_queue (table_name, row_id, operation) VALUES ('{table}', OLD.id, 'DELETE');
                END;
            ''')
            
        conn.commit()
        conn.close()

    def bootstrap_from_firestore(self):
        """If SQLite is empty, populate it from Firestore."""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' AND name != '_sync_queue'")
        tables = [r[0] for r in cur.fetchall()]
        
        for table in tables:
            cur.execute(f"SELECT COUNT(*) FROM {table}")
            count = cur.fetchone()[0]
            if count == 0:
                print(f"Bootstrapping {table} from Firestore...")
                docs = self.firestore_db.collection(table).stream()
                for doc in docs:
                    data = doc.to_dict()
                    if not data: continue
                    # Insert into sqlite
                    columns = ', '.join(data.keys())
                    placeholders = ', '.join(['?'] * len(data))
                    values = tuple(data.values())
                    try:
                        cur.execute(f"INSERT OR REPLACE INTO {table} ({columns}) VALUES ({placeholders})", values)
                    except Exception as e:
                        print(f"Failed to bootstrap doc {doc.id} in {table}: {e}")
        conn.commit()
        conn.close()

    def process_queue(self):
        """Process the sync queue and push changes to Firestore."""
        if not self.sync_lock.acquire(blocking=False):
            return # Already syncing
            
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            
            cur.execute("SELECT * FROM _sync_queue ORDER BY id ASC")
            events = cur.fetchall()
            
            if not events:
                return
                
            batch = self.firestore_db.batch()
            processed_ids = []
            
            for event in events:
                table = event['table_name']
                row_id = event['row_id']
                op = event['operation']
                
                doc_ref = self.firestore_db.collection(table).document(str(row_id))
                
                if op == 'DELETE':
                    batch.delete(doc_ref)
                else:
                    # For INSERT/UPDATE, fetch the latest state from SQLite
                    cur.execute(f"SELECT * FROM {table} WHERE id = ?", (row_id,))
                    row = cur.fetchone()
                    if row:
                        batch.set(doc_ref, dict(row))
                
                processed_ids.append(str(event['id']))
            
            if processed_ids:
                batch.commit()
                # Delete processed events
                ph = ",".join("?" * len(processed_ids))
                cur.execute(f"DELETE FROM _sync_queue WHERE id IN ({ph})", processed_ids)
                conn.commit()
                print(f"Synced {len(processed_ids)} events to Firestore.")
                
            conn.close()
        except Exception as e:
            print(f"Firestore Sync Error: {e}")
        finally:
            self.sync_lock.release()

# Global sync engine instance
sync_engine = None

def init_sync_engine(db_path):
    global sync_engine
    if sync_engine is None:
        sync_engine = FirestoreSyncEngine(db_path)
        sync_engine.setup_triggers()
        sync_engine.bootstrap_from_firestore()
        
def get_sync_engine():
    return sync_engine
