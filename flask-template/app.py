from flask import Flask, render_template, session
from flask_restful import Api
from datetime import timedelta
from dotenv import load_dotenv
import warnings
warnings.filterwarnings("ignore")
import os
from services.Process_Ask import ProcessDocuments, AskQuestion


SERVICE_ACCOUNT_PATH = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", ".\chat-docs-432213-1d571c2cb42f.json")
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = SERVICE_ACCOUNT_PATH


app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY','dev_secret_key')
api = Api(app)
app.permanent_session_lifetime = timedelta(hours=2)

@app.route("/")
def home():
    session.permanent = True
    uploaded_files = session.get("uploaded_files", [])
    chat_history = session.get("chat_history", [])
    return render_template("home.html", uploaded_files=uploaded_files, chat_history=chat_history)

@app.route("/about")
def about():
    return render_template("about.html")

@app.route('/api/process-docs', methods=['POST'])
def process():
    return ProcessDocuments().post()

@app.route('/api/ask', methods=['POST'])
def ask():
    return AskQuestion().post()

api.add_resource(ProcessDocuments, '/api/process-docs')
api.add_resource(AskQuestion, '/api/ask')

if __name__ == '__main__':
    load_dotenv()
    app.run(host='0.0.0.0', port=5000, debug=True)

