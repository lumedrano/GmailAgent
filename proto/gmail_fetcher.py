import os
import base64
import openai
import re

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

# === CONFIG ===
SCOPES = ['https://mail.google.com/']
openai.api_key = os.getenv('OPENAI_KEY')

# === GMAIL AUTH ===
def get_gmail_service():
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

# === FETCH UNREAD EMAILS ===
def get_unread_emails(service, max_results=5):
    results = service.users().messages().list(
        userId='me',
        labelIds=['UNREAD'],
        q='-category:promotions',
        maxResults=max_results
    ).execute()
    messages = results.get('messages', [])

    email_list = []
    for msg in messages:
        msg_data = service.users().messages().get(userId='me', id=msg['id'], format='full').execute()
        headers = msg_data['payload']['headers']
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '')
        sender = next((h['value'] for h in headers if h['name'] == 'From'), '')
        snippet = msg_data.get('snippet', '')

        body = ""
        parts = msg_data['payload'].get('parts', [])
        for part in parts:
            if part['mimeType'] == 'text/plain':
                body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8', errors='ignore')
                break

        email_list.append({
            'id': msg['id'],
            'from': sender,
            'subject': subject,
            'summary': snippet,
            'body': body
        })

    return email_list

# === LLM INTERACTION ===
def prompt_llm_with_emails(user_query, emails):
    prompt = (
        "You are an AI email assistant. Help the user by giving clear commands like:\n"
        "- show_email(1)\n"
        "- reply_email(2, 'Your message here')\n"
        "- send_email('recipient@example.com', 'Subject line', 'Message body')\n\n"
        "Here are the unread emails:\n"
    )

    for i, email in enumerate(emails, 1):
        prompt += f"\nEmail {i}:\nFrom: {email['from']}\nSubject: {email['subject']}\nSummary: {email['summary']}\n"

    prompt += f"\nUser query: {user_query}"

    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an intelligent email assistant."},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content

# === DRAFT REPLY GENERATOR ===
def draft_email_reply(email, user_message):
    prompt = (
        f"Write a professional and friendly email reply.\n\n"
        f"Original email:\nFrom: {email['from']}\nSubject: {email['subject']}\nBody:\n{email['body']}\n\n"
        f"User wants to say: {user_message}\n\n"
    )
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an expert email assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content.strip()

# === SEND EMAIL FUNCTIONS ===
def send_reply(original_email, message_text, service):
    reply = MIMEText(message_text)
    reply['To'] = original_email['from']
    reply['Subject'] = "Re: " + original_email['subject']
    raw = base64.urlsafe_b64encode(reply.as_bytes()).decode()
    message = {'raw': raw}
    service.users().messages().send(userId='me', body=message).execute()
    print("✅ Reply sent.")

def send_email(to, subject, message_text, service):
    message = MIMEText(message_text)
    message['To'] = to
    message['Subject'] = subject
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    body = {'raw': raw}
    service.users().messages().send(userId='me', body=body).execute()
    print(f"✅ Email sent to {to}.")

# === GLOBAL STATE ===
draft_reply = None
reply_email_index = None

# === EXECUTE COMMANDS ===
def parse_and_execute(response, emails, service):
    global draft_reply, reply_email_index

    if match := re.search(r'show_email\((\d+)\)', response):
        idx = int(match.group(1)) - 1
        if 0 <= idx < len(emails):
            email = emails[idx]
            print(f"\n📧 From: {email['from']}\nSubject: {email['subject']}\n\n{email['body']}\n")
        else:
            print("❌ Invalid email index.")

    elif match := re.search(r"reply_email\((\d+),\s*['\"](.+?)['\"]\)", response, re.DOTALL):
        idx = int(match.group(1)) - 1
        user_msg = match.group(2)
        if 0 <= idx < len(emails):
            email = emails[idx]
            draft_reply = draft_email_reply(email, user_msg)
            reply_email_index = idx
            print(f"\n📝 Drafted Reply:\n{draft_reply}\n")
        else:
            print("❌ Invalid email index.")

    elif match := re.search(r"send_email\(['\"](.+?)['\"],\s*['\"](.+?)['\"],\s*['\"](.+?)['\"]\)", response, re.DOTALL):
        to = match.group(1)
        subject = match.group(2)
        message = match.group(3)
        send_email(to, subject, message, service)

    elif response.strip().lower() == 'send':
        if draft_reply is not None and reply_email_index is not None:
            send_reply(emails[reply_email_index], draft_reply, service)
            draft_reply = None
            reply_email_index = None
        else:
            print("❌ No drafted reply to send.")

    elif response.strip().lower() == 'cancel' and draft_reply:
        print("❌ Reply canceled.\n")
        draft_reply = None
        reply_email_index = None

    elif draft_reply:
        draft_reply = response
        print("\n✅ Draft updated. Type 'send' to send or 'cancel' to discard.\n")
        print(draft_reply)

    else:
        print("🤖 I didn't understand. Try again with a supported command.")

# === MAIN LOOP ===
# def main():
#     service = get_gmail_service()
#     print("📬 Gmail Agent ready. Type 'exit' to quit.\n")

#     while True:
#         emails = get_unread_emails(service)
#         if not emails:
#             print("📭 No unread emails.")
#             break

#         user_input = input("You: ")
#         if user_input.lower() in ['exit', 'quit']:
#             break

#         llm_response = prompt_llm_with_emails(user_input, emails)
#         print(f"\n🤖 Agent:\n{llm_response}\n")

#         parse_and_execute(llm_response, emails, service)

def main():
    service = get_gmail_service()
    print("📬 Gmail Agent ready. Type 'exit' to quit.\n")

    draft_mode = False  # Track if we're editing a draft

    while True:
        emails = get_unread_emails(service)
        if not emails:
            print("📭 No unread emails.")
            break

        user_input = input("You: ")

        if user_input.lower() in ['exit', 'quit']:
            break

        if draft_mode:
            # When editing a draft or in "send/cancel" mode,
            # parse the user input directly without calling LLM
            parse_and_execute(user_input, emails, service)

            # If draft cleared (sent or canceled), exit draft mode
            if draft_reply is None:
                draft_mode = False
        else:
            # Normal mode: send user input to LLM
            llm_response = prompt_llm_with_emails(user_input, emails)
            print(f"\n🤖 Agent:\n{llm_response}\n")

            parse_and_execute(llm_response, emails, service)

            # If a draft reply is generated, enter draft mode
            if draft_reply is not None:
                draft_mode = True


if __name__ == '__main__':
    main()
