from flask import Flask
from flask_restful import Api
from datetime import timedelta
from dotenv import load_dotenv
import warnings
import os
from services.Process_Ask import ProcessDocuments, AskQuestion

load_dotenv()

warnings.filterwarnings("ignore")

SERVICE_ACCOUNT_PATH = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "./chat-docs-432213-1d571c2cb42f.json")
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = SERVICE_ACCOUNT_PATH


app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev_secret_key')
api = Api(app)
app.permanent_session_lifetime = timedelta(hours=2)

@app.route('/api/process-docs', methods=['POST'])
def process():
    return ProcessDocuments().post()

@app.route('/api/ask', methods=['POST'])
def ask():
    return AskQuestion().post()


api.add_resource(ProcessDocuments, '/api/process-docs')
api.add_resource(AskQuestion, '/api/ask')


if __name__ == "__main__":
    from waitress import serve
    print("Starting server with waitress...")
    serve(app, host="0.0.0.0", port=5000)