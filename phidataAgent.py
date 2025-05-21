import os
import base64
import json
from typing import List, Dict, Any, Optional
from email.mime.text import MIMEText

from dotenv import load_dotenv
from phi.tools import Toolkit, tool
from phi.tools import tool_registry
from phi.assistant import Assistant
from phi.llm.openai import OpenAIChat

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# === Load API Keys ===
load_dotenv()
OPENAI_KEY = os.getenv("OPENAI_KEY")
SCOPES = ['https://mail.google.com/']

# === Gmail Auth ===
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

# === Gmail Tools for Phi ===
class GmailTools(Toolkit):
    def __init__(self, service):
        super().__init__()
        self.service = service
        self.current_emails = []  # Cache for emails
        # Explicit registration of each tool method
        self.register(self.get_unread_emails)
        self.register(self.read_email_body)
        self.register(self.send_email)
        self.register(self.reply_to_email)
        

    # @tool
    def get_unread_emails(self, max_results: int = 5) -> str:
        """
        Fetch unread, non-promotional emails and return them as a formatted string.
        This should be the first function called in most interactions.
        
        Args:
            max_results: Maximum number of emails to retrieve (default: 5)
            
        Returns:
            A formatted string with email information
        """
        results = self.service.users().messages().list(
            userId='me',
            labelIds=['UNREAD'],
            q='-category:promotions',
            maxResults=max_results
        ).execute()
        
        messages = results.get('messages', [])
        if not messages:
            self.current_emails = []
            return "No unread emails found."
            
        emails = []
        for idx, msg in enumerate(messages, 1):
            msg_data = self.service.users().messages().get(userId='me', id=msg['id'], format='full').execute()
            headers = msg_data['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '')
            sender = next((h['value'] for h in headers if h['name'] == 'From'), '')
            snippet = msg_data.get('snippet', '')
            
            # Extract email body
            body = ""
            parts = msg_data['payload'].get('parts', [])
            if parts:
                for part in parts:
                    if part['mimeType'] == 'text/plain' and 'data' in part.get('body', {}):
                        body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8', errors='ignore')
                        break
            
            email_info = {
                'index': idx,
                'id': msg['id'],
                'from': sender,
                'subject': subject,
                'summary': snippet,
                'body': body
            }
            emails.append(email_info)
        
        # Cache the emails
        self.current_emails = emails
        
        # Create formatted output for display
        formatted_output = "📥 Unread Emails:\n\n"
        for email in emails:
            formatted_output += f"Email #{email['index']}:\n"
            formatted_output += f"From: {email['from']}\n"
            formatted_output += f"Subject: {email['subject']}\n"
            formatted_output += f"Preview: {email['summary'][:100]}...\n\n"
        
        return formatted_output

    # @tool
    def read_email_body(self, email_index: int) -> str:
        """
        Get the full content of an email by its index.
        
        Args:
            email_index: The index number of the email (as shown in the list)
            
        Returns:
            The full email content
        """
        # Check if emails have been loaded
        if not self.current_emails:
            return "No emails loaded. Please use get_unread_emails first."
        
        # Find the email by index
        email = next((e for e in self.current_emails if e['index'] == email_index), None)
        if not email:
            return f"Email #{email_index} not found. Valid indices are {[e['index'] for e in self.current_emails]}"
        
        # Format the full email content
        full_content = f"📧 Email #{email_index} Full Content:\n\n"
        full_content += f"From: {email['from']}\n"
        full_content += f"Subject: {email['subject']}\n"
        full_content += f"Body:\n{email['body']}\n"
        
        return full_content

    # @tool
    def send_email(self, to: str, subject: str, body: str) -> str:
        """
        Send a new email.
        
        Args:
            to: Recipient email address
            subject: Email subject
            body: Email content
            
        Returns:
            Confirmation message
        """
        message = MIMEText(body)
        message['To'] = to
        message['Subject'] = subject
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        body = {'raw': raw}
        self.service.users().messages().send(userId='me', body=body).execute()
        return f"✅ Email sent to {to}"

    # @tool
    def reply_to_email(self, email_index: int, reply_text: str) -> str:
        """
        Reply to an email using its index number.
        
        Args:
            email_index: The index number of the email to reply to
            reply_text: The content of your reply
            
        Returns:
            Confirmation message
        """
        # Check if emails have been loaded
        if not self.current_emails:
            return "No emails loaded. Please use get_unread_emails first."
        
        # Find the email by index
        email = next((e for e in self.current_emails if e['index'] == email_index), None)
        if not email:
            return f"Email #{email_index} not found. Valid indices are {[e['index'] for e in self.current_emails]}"
        
        # Create the reply
        try:
            # Get the original message to properly create a reply
            original_msg = self.service.users().messages().get(userId='me', id=email['id']).execute()
            
            # Create the reply message
            reply = MIMEText(reply_text)
            reply['To'] = email['from']
            reply['Subject'] = f"Re: {email['subject']}"
            reply['References'] = email['id']
            reply['In-Reply-To'] = email['id']
            
            # Convert to raw format
            raw = base64.urlsafe_b64encode(reply.as_bytes()).decode()
            
            # Include the threadId from the original message
            message = {
                'raw': raw,
                'threadId': original_msg.get('threadId', email['id'])
            }
            
            # Send the reply
            self.service.users().messages().send(userId='me', body=message).execute()
            return f"✅ Reply sent to email #{email_index}"
            
        except Exception as e:
            return f"❌ Error sending reply: {str(e)}"


# === Main Agent Setup ===
def main():
    print("📬 Gmail Assistant (Phi) is starting...")

    gmail_service = get_gmail_service()
    tools = GmailTools(service=gmail_service)
    print(tools)

    # More detailed instructions that explain when and how to use the tools
    instructions = """
    You are an AI email assistant using Gmail. Follow these guidelines:
    
    1. call get_unread_emails() to fetch the latest emails if needed by user
    2. When user wants to read an email, use read_email_body(email_index)
    3. When user wants to reply to an email, use reply_to_email(email_index, reply_text)
    4. When user wants to send a new email, use send_email(to, subject, body)
    
    IMPORTANT:
    - Always use the tools when appropriate - do not simulate email content
    - Email indices start from 1, not 0
    - Show the user when you're calling functions and their results
    - Make decisions about which emails to interact with based on user requests
    
    Example interactions:
    - "Check my emails" → call get_unread_emails()
    - "Read email 2" → call read_email_body(2)
    - "Reply to email 3 saying I'll call them tomorrow" → call reply_to_email(3, "I'll give you a call tomorrow...")
    """

    assistant = Assistant(
        tools=[tools],
        llm=OpenAIChat(
            model="gpt-4o-mini", 
            api_key=OPENAI_KEY,
        ),
        instructions=[instructions],
        show_tool_calls=True,  # Show the tool calls to the user
        markdown=True
    )


    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in ['exit', 'quit']:
            print("👋 Exiting.")
            break
            
        # Process user input
        try:
            assistant.print_response(
                user_input, 
                stream=True
            )
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            print("Retrying with simpler approach...")
            # Fallback approach for older versions
            result = ""
            for item in assistant.run(user_input):
                if isinstance(item, str):
                    result = item
                    print(item, end="", flush=True)
            print("\n")


if __name__ == '__main__':
    main()