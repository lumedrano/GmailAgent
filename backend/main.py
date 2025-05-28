from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from phi.assistant import Assistant
from phi.llm.openai import OpenAIChat
from phidataAgent import get_gmail_service, GmailTools

import os

# Load environment variables
load_dotenv()
OPENAI_KEY = os.getenv("OPENAI_KEY")

# Flask setup
app = Flask(__name__)
# CORS(app) #regular running or used for XCode
CORS(app, origins=["http://localhost:3000", "http://127.0.0.1:3000"]) #TODO: change if using react front end


# Initialize the Gmail assistant
gmail_service = get_gmail_service()
tools = GmailTools(service=gmail_service)

instructions = """
You are an AI email assistant using Gmail. Follow these guidelines:

1. Call get_unread_emails() to fetch the latest emails if needed by user.
2. When user wants to read an email, use read_email_body(email_index).
3. When user wants to reply to an email, use reply_to_email(email_index, reply_text).
4. When user wants to send a new email, use send_email(to, subject, body).

IMPORTANT:
- Always use the tools when appropriate - do not simulate email content.
- Email indices start from 1, not 0.
- Show the user when you're calling functions and their results.
- Make decisions about which emails to interact with based on user requests.
- Format your responses in markdown so they are easy to read.
"""

assistant = Assistant(
    tools=[tools],
    llm=OpenAIChat(model="gpt-4o-mini", api_key=OPENAI_KEY),
    instructions=[instructions],
    show_tool_calls=False,
    markdown=True
)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_input = data.get("message", "")
    try:
        full_response = ""
        for item in assistant.run(user_input):
            if isinstance(item, str):
                full_response += item
        return jsonify({"response": full_response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
    # app.run(host="0.0.0.0", port=5050) #TODO: runs for XCode


