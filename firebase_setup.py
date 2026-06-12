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
            print("WARNING: firebase-adminsdk.json not found and FIREBASE_CREDENTIALS not set. Firebase Admin SDK not initialized.")

def get_db():
    initialize_firebase()
    return firestore.client()

def get_auth():
    initialize_firebase()
    return auth
