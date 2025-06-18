import os
import json
from pymongo import MongoClient
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

load_dotenv()
SCOPES = ['https://mail.google.com/']  # Full Gmail access
MONGO_URI = os.getenv("CONNECTION_STRING")

client = MongoClient(MONGO_URI)
db = client['Tokens']
tokens_collection = db['user_tokens']

def get_user_credentials(user_email: str) -> Credentials:
    user_token = tokens_collection.find_one({"user_email": user_email})
    creds = None

    if user_token:
        creds = Credentials.from_authorized_user_info(user_token['token'], SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=8081)


        tokens_collection.update_one(
            {"user_email": user_email},
            {"$set": {"token": json.loads(creds.to_json())}},
            upsert=True
        )
    return creds

def revoke_user_credentials(user_email: str):
    tokens_collection.delete_one({"user_email": user_email})
