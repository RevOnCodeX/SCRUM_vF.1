import firebase_admin
from firebase_admin import credentials, firestore, auth
import os

def initialize_firebase():
    if not firebase_admin._apps:
        import json
        env_cred = os.environ.get('FIREBASE_CREDENTIALS')
        cred_path = os.path.join(os.path.dirname(__file__), 'firebase-adminsdk.json')
        
        if env_cred:
            cred_dict = json.loads(env_cred)
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred)
        elif os.path.exists(cred_path):
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
        else:
            # Fallback for Google Cloud environments (Cloud Functions / Cloud Run)
            # which automatically inject default service accounts.
            print("Using default application credentials for Firebase.")
            try:
                firebase_admin.initialize_app()
            except Exception as e:
                print(f"Failed to initialize Firebase Admin SDK: {e}")

def get_db():
    initialize_firebase()
    return firestore.client()

def get_auth():
    initialize_firebase()
    return auth
