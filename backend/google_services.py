# google_auth.py - Unified authentication for both Gmail and Calendar
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Combined scopes for both Gmail and Calendar
SCOPES = [
    'https://mail.google.com/',  # Gmail access
    'https://www.googleapis.com/auth/calendar',  # Calendar access
    'https://www.googleapis.com/auth/calendar.events'  # Calendar events
]

def get_google_service(service_name, version='v1', creds_file='credentials.json', token_file='unified_token.json'):
    """
    Get authenticated Google service for Gmail or Calendar
    
    Args:
        service_name: 'gmail' or 'calendar'
        version: API version ('v1' for Gmail, 'v3' for Calendar)
        creds_file: Path to credentials.json file
        token_file: Path to token file (unified for both services)
    
    Returns:
        Authenticated Google service object
    """
    creds = None

    # Load existing token if it exists
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)

    # Check if credentials are valid
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"Failed to refresh token: {e}")
                # Remove invalid token file
                if os.path.exists(token_file):
                    os.remove(token_file)
                creds = None
        
        # If no valid credentials, run OAuth flow
        if not creds:
            if not os.path.exists(creds_file):
                raise FileNotFoundError(f"Credentials file '{creds_file}' not found.")
            
            flow = InstalledAppFlow.from_client_secrets_file(creds_file, SCOPES)
            creds = flow.run_local_server(port=8080)

            # Save credentials for future use
            with open(token_file, 'w') as token:
                token.write(creds.to_json())

    return build(service_name, version, credentials=creds)

def get_gmail_service():
    """Get authenticated Gmail service"""
    return get_google_service('gmail', 'v1')

def get_calendar_service():
    """Get authenticated Calendar service"""
    return get_google_service('calendar', 'v3')