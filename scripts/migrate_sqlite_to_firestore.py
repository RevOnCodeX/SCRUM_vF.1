import sqlite3
import os
import sys

# Add the parent directory to the path so we can import firebase_setup
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from firebase_setup import get_db

def migrate():
    # 1. Connect to SQLite
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'team_tracker.db')
    if not os.path.exists(db_path):
        print(f"Error: Database not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # 2. Get Firestore client
    firestore_db = get_db()
    if not firestore_db:
        print("Error: Could not connect to Firestore.")
        return

    # 3. Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row['name'] for row in cursor.fetchall() if row['name'] != 'sqlite_sequence']

    print(f"Found tables: {tables}")

    for table in tables:
        print(f"Migrating table: {table}...")
        cursor.execute(f"SELECT * FROM {table}")
        rows = cursor.fetchall()

        # Batch writer for faster uploads
        batch = firestore_db.batch()
        count = 0

        for row in rows:
            row_dict = dict(row)
            
            # Determine document ID (use 'id' if it exists, else auto-generate)
            doc_id = str(row_dict.get('id')) if 'id' in row_dict else None
            
            # Create a document reference
            if doc_id:
                doc_ref = firestore_db.collection(table).document(doc_id)
            else:
                doc_ref = firestore_db.collection(table).document()
            
            batch.set(doc_ref, row_dict)
            count += 1
            
            # Firestore batches support up to 500 operations
            if count % 400 == 0:
                batch.commit()
                batch = firestore_db.batch()
                print(f"  ...committed {count} records for {table}")
                
        # Commit any remaining records in the batch
        if count % 400 != 0:
            batch.commit()
        
        print(f"Finished migrating {count} records to collection '{table}'.")

    conn.close()
    print("Migration complete!")

if __name__ == "__main__":
    migrate()
