from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
# from phi.assistant import Assistant
# from phi.llm.openai import OpenAIChat
from phi.agent import Agent, RunResponse
from phi.model.ollama import Ollama 
from phidataAgent import get_gmail_service, GmailTools
from auth_service import get_user_credentials, revoke_user_credentials
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
import os

# Load environment variables
load_dotenv()
OPENAI_KEY = os.getenv("OPENAI_KEY")
CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")

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
#####Using chatgpt api
# assistant = Assistant(
#     tools=[tools],
#     llm=OpenAIChat(model="gpt-4o-mini", api_key=OPENAI_KEY),
#     instructions=[instructions],
#     show_tool_calls=False,
#     markdown=True
# )

##using ollama
assistant = Agent(
    tools=[tools],
    # model = Ollama(id="custom-model", base_url="http://ollama:11434"),
    model = Ollama(id="gmail-assistant"),
    show_tool_calls=False,
    markdown=True
)

# @app.route('/chat', methods=['POST'])
# def chat():
#     data = request.get_json()
#     user_input = data.get("message", "")
#     try:
#         full_response = ""
#         for item in assistant.run(user_input):
#             if isinstance(item, str):
#                 print(item)
#                 full_response += item
#         return jsonify({"response": full_response})
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500



@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    id_token_str = data.get("id_token")

    if not id_token_str:
        return jsonify({"error": "ID token is required"}), 400

    try:
        # Verify the ID token
        idinfo = id_token.verify_oauth2_token(id_token_str, google_requests.Request(), CLIENT_ID)

        user_email = idinfo['email']
        user_name = idinfo.get('name', '')  # you can extract more like picture, etc.

        # Now get/store Gmail credentials for this user
        creds = get_user_credentials(user_email)

        return jsonify({"message": f"Authenticated for {user_email}", "email": user_email, "name": user_name})

    except ValueError as e:
        return jsonify({"error": "Invalid token"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/logout', methods=['POST'])
def logout():
    data = request.get_json()
    user_email = data.get("user_email")

    if not user_email:
        return jsonify({"error": "User email is required"}), 400
    
    try:
        revoke_user_credentials(user_email)
        return jsonify({"message": f"Logged out {user_email}"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_input = data.get("message", "")
    try:
        full_response = ""
        run: RunResponse = assistant.run(user_input)
        for item in run.content:
            if isinstance(item, str):
                full_response += item
        return jsonify({"response": full_response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
    # app.run(host="0.0.0.0", port=5050) #TODO: runs for XCode


