import os.path
import base64
import email
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from transformers import pipeline

# Only read access
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def get_service():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)

def get_unread_emails(max_results=5):
    service = get_service()
    results = service.users().messages().list(userId='me', labelIds=['UNREAD'], maxResults=max_results).execute()
    messages = results.get('messages', [])

    emails = []
    for msg in messages:
        msg_data = service.users().messages().get(userId='me', id=msg['id']).execute()
        headers = msg_data['payload']['headers']
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '(No Subject)')
        sender = next((h['value'] for h in headers if h['name'] == 'From'), '(No Sender)')

        try:
            part = msg_data['payload']['parts'][0]
            data = part['body'].get('data') or msg_data['payload']['body'].get('data')
        except (KeyError, IndexError):
            data = msg_data['payload']['body'].get('data')

        if data:
            decoded_body = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
        else:
            decoded_body = "(No content)"

        emails.append({
            'from': sender,
            'subject': subject,
            'body': decoded_body
        })

    return emails


# Load the summarizer once
summarizer = pipeline("summarization", model="t5-small")

def summarize_email_body(email_body):
    # T5-small can only handle ~512 tokens, so trim the input
    trimmed_body = email_body[:1000]
    summary = summarizer(trimmed_body, max_length=100, min_length=25, do_sample=False)
    return summary[0]['summary_text']

def classify_email(summary):
    summary = summary.lower()
    if any(word in summary for word in ['urgent', 'immediately', 'asap', 'important']):
        return "Urgent"
    elif any(word in summary for word in ['meeting', 'invoice', 'update', 'deadline']):
        return "Important"
    elif any(word in summary for word in ['unsubscribe', 'promo', 'sale', 'deal']):
        return "Spam"
    else:
        return "Neutral"



if __name__ == '__main__':
    unread_emails = get_unread_emails()
    for i, email in enumerate(unread_emails, 1):
        print(f"\nEmail {i}")
        print(f"From: {email['from']}")
        print(f"Subject: {email['subject']}")
        summary = summarize_email_body(email['body'])
        print(f"Summary: {summary}")
        print("-" * 80)
        classification = classify_email(summary)
        print(f"Classification: {classification}")


