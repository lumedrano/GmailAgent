# import os
# import base64
# import json
# from typing import List, Dict, Any, Optional
# from email.mime.text import MIMEText

# from dotenv import load_dotenv
# from phi.tools import Toolkit, tool
# from phi.tools import tool_registry
# # from phi.assistant import Assistant
# # from phi.llm.openai import OpenAIChat
# from phi.agent import Agent, RunResponse
# from phi.model.ollama import Ollama 

# from google.auth.transport.requests import Request
# from google.oauth2.credentials import Credentials
# from google_auth_oauthlib.flow import InstalledAppFlow
# from googleapiclient.discovery import build

# # === Load API Keys ===
# load_dotenv()
# SCOPES = ['https://mail.google.com/']

# # === Gmail Auth ===
# def get_gmail_service():
#     creds = None
#     if os.path.exists('token.json'):
#         creds = Credentials.from_authorized_user_file('token.json', SCOPES)
#     if not creds or not creds.valid:
#         if creds and creds.expired and creds.refresh_token:
#             creds.refresh(Request())
#         else:
#             flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
#             # creds = flow.run_local_server(port=0)
#             creds = flow.run_local_server(port=8080)
#         with open('token.json', 'w') as token:
#             token.write(creds.to_json())
#     return build('gmail', 'v1', credentials=creds)

# # === Gmail Tools for Phi ===
# class GmailTools(Toolkit):
#     def __init__(self, service):
#         super().__init__()
#         self.service = service
#         self.current_emails = []  # Cache for emails
#         # Explicit registration of each tool method
#         self.register(self.get_unread_emails)
#         self.register(self.read_email_body)
#         self.register(self.send_email)
#         self.register(self.reply_to_email)
        

#     # @tool
#     def get_unread_emails(self, max_results: int = 5) -> str:
#         """
#         Fetch unread, non-promotional emails and return them as a formatted string.
#         This should be the first function called in most interactions.
        
#         Args:
#             max_results: Maximum number of emails to retrieve (default: 5)
            
#         Returns:
#             A formatted string with email information
#         """
#         results = self.service.users().messages().list(
#             userId='me',
#             labelIds=['UNREAD'],
#             q='-category:promotions -category:social',
#             maxResults=max_results
#         ).execute()
        
#         messages = results.get('messages', [])
#         if not messages:
#             self.current_emails = []
#             return "No unread emails found."
            
#         emails = []
#         for idx, msg in enumerate(messages, 1):
#             msg_data = self.service.users().messages().get(userId='me', id=msg['id'], format='full').execute()
#             headers = msg_data['payload']['headers']
#             subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '')
#             sender = next((h['value'] for h in headers if h['name'] == 'From'), '')
#             snippet = msg_data.get('snippet', '')
            
#             # Extract email body
#             body = ""
#             parts = msg_data['payload'].get('parts', [])
#             if parts:
#                 for part in parts:
#                     if part['mimeType'] == 'text/plain' and 'data' in part.get('body', {}):
#                         body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8', errors='ignore')
#                         break
            
#             email_info = {
#                 'index': idx,
#                 'id': msg['id'],
#                 'from': sender,
#                 'subject': subject,
#                 'summary': snippet,
#                 'body': body
#             }
#             emails.append(email_info)
        
#         # Cache the emails
#         self.current_emails = emails
        
#         # Create formatted output for display
#         formatted_output = "📥 Unread Emails:\n\n"
#         for email in emails:
#             formatted_output += f"Email #{email['index']}:\n"
#             formatted_output += f"From: {email['from']}\n"
#             formatted_output += f"Subject: {email['subject']}\n"
#             formatted_output += f"Preview: {email['summary'][:100]}...\n\n"
        
#         return formatted_output

#     # @tool
#     def read_email_body(self, email_index: int) -> str:
#         """
#         Get the full content of an email by its index.
        
#         Args:
#             email_index: The index number of the email (as shown in the list)
            
#         Returns:
#             The full email content
#         """
#         # Check if emails have been loaded
#         if not self.current_emails:
#             return "No emails loaded. Please use get_unread_emails first."
        
#         # Find the email by index
#         email = next((e for e in self.current_emails if e['index'] == email_index), None)
#         if not email:
#             return f"Email #{email_index} not found. Valid indices are {[e['index'] for e in self.current_emails]}"
        
#         # Format the full email content
#         full_content = f"📧 Email #{email_index} Full Content:\n\n"
#         full_content += f"From: {email['from']}\n"
#         full_content += f"Subject: {email['subject']}\n"
#         full_content += f"Body:\n{email['body']}\n"
        
#         return full_content

#     # @tool
#     def send_email(self, to: str, subject: str, body: str) -> str:
#         """
#         Send a new email.
        
#         Args:
#             to: Recipient email address
#             subject: Email subject
#             body: Email content
            
#         Returns:
#             Confirmation message
#         """
#         message = MIMEText(body)
#         message['To'] = to
#         message['Subject'] = subject
#         raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
#         body = {'raw': raw}
#         self.service.users().messages().send(userId='me', body=body).execute()
#         return f"✅ Email sent to {to}"

#     # @tool
#     def reply_to_email(self, email_index: int, reply_text: str) -> str:
#         """
#         Reply to an email using its index number.
        
#         Args:
#             email_index: The index number of the email to reply to
#             reply_text: The content of your reply
            
#         Returns:
#             Confirmation message
#         """
#         # Check if emails have been loaded
#         if not self.current_emails:
#             return "No emails loaded. Please use get_unread_emails first."
        
#         # Find the email by index
#         email = next((e for e in self.current_emails if e['index'] == email_index), None)
#         if not email:
#             return f"Email #{email_index} not found. Valid indices are {[e['index'] for e in self.current_emails]}"
        
#         # Create the reply
#         try:
#             # Get the original message to properly create a reply
#             original_msg = self.service.users().messages().get(userId='me', id=email['id']).execute()
            
#             # Create the reply message
#             reply = MIMEText(reply_text)
#             reply['To'] = email['from']
#             reply['Subject'] = f"Re: {email['subject']}"
#             reply['References'] = email['id']
#             reply['In-Reply-To'] = email['id']
            
#             # Convert to raw format
#             raw = base64.urlsafe_b64encode(reply.as_bytes()).decode()
            
#             # Include the threadId from the original message
#             message = {
#                 'raw': raw,
#                 'threadId': original_msg.get('threadId', email['id'])
#             }
            
#             # Send the reply
#             self.service.users().messages().send(userId='me', body=message).execute()
#             return f"✅ Reply sent to email #{email_index}"
            
#         except Exception as e:
#             return f"❌ Error sending reply: {str(e)}"



# gmail_tools.py - Updated to use unified auth
import os
import base64
import json
from typing import List, Dict, Any, Optional
from email.mime.text import MIMEText

from dotenv import load_dotenv
from phi.tools import Toolkit, tool
from phi.tools import tool_registry
from phi.agent import Agent, RunResponse
from phi.model.ollama import Ollama 

# Import the unified auth function
from google_services import get_gmail_service

# === Load API Keys ===
load_dotenv()

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
            q='-category:promotions -category:social',
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


# Test function
if __name__ == "__main__":
    try:
        gmail_service = get_gmail_service()
        gmail_tools = GmailTools(service=gmail_service)
        
        # Test the tools
        print(gmail_tools.get_unread_emails(max_results=3))
        
    except Exception as e:
        print(f"Error: {e}")
