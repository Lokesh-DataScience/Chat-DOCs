from flask import Flask, request, render_template, session, redirect, url_for, flash, jsonify
from flask_restful import Api, Resource
from datetime import timedelta
from PyPDF2 import PdfReader
import docx
from dotenv import load_dotenv
from langchain.text_splitter import CharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.memory.buffer import ConversationBufferMemory
from langchain.chains.conversational_retrieval.base import ConversationalRetrievalChain
from langchain_google_genai import (
    ChatGoogleGenerativeAI,
    HarmBlockThreshold,
    HarmCategory,
)
import warnings
warnings.filterwarnings("ignore")
import os
from google.auth import exceptions
from google.cloud import storage

# Use environment variable for service account path
SERVICE_ACCOUNT_PATH = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", ".\chat-docs-432213-1d571c2cb42f.json")

# Verify the file exists
if not os.path.exists(SERVICE_ACCOUNT_PATH):
    print("Service account file not found!")

# Set the credentials path
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = SERVICE_ACCOUNT_PATH

# Example: Initialize Google Cloud Storage client
try:
    storage_client = storage.Client()
    print("Google Cloud authenticated successfully!")
except exceptions.DefaultCredentialsError as e:
    print(f"Failed to authenticate: {e}")

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY','dev_secret_key')
api = Api(app)
app.permanent_session_lifetime = timedelta(hours=2)

conversation = None 

# 📌 Helper functions
def get_doc_text(documents):
    """Extracts text from PDF, DOCX, and TXT files."""
    text = ""
    filenames = []

    for doc in documents:
        filenames.append(doc.filename)
        if doc.filename.endswith('.pdf'):
            doc_reader = PdfReader(doc)
            for page in doc_reader.pages:
                text += page.extract_text() or ""
        elif doc.filename.endswith('.docx'):
            docx_reader = docx.Document(doc)
            for para in docx_reader.paragraphs:
                text += para.text + "\n"
        elif doc.filename.endswith('.txt'):
            text += doc.read().decode("utf-8")

    session['uploaded_files'] = filenames
    return text

def get_text_chunks(text):
    """Splits the text into manageable chunks."""
    text_splitter = CharacterTextSplitter(
        separator="\n\n",
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        is_separator_regex=False,
    )
    return text_splitter.split_text(text)

def get_vectorstore(text_chunks):
    """Creates a FAISS vector store from text chunks."""
    model_name = "sentence-transformers/all-mpnet-base-v2"
    hf = HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': False}
    )
    return FAISS.from_texts(text_chunks, hf)

def get_conversation_chain(vectorstore):
    """Initializes the conversation chain."""
    memory = ConversationBufferMemory(memory_key='chat_history', return_messages=True)
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-pro",
        safety_settings={HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE},
    )
    return ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(),
        memory=memory
    )

# 🌐 RESTful API Endpoints
class ProcessDocuments(Resource):
    def post(self):
        """Processes uploaded documents and creates a conversation chain."""
        global conversation

        session.permanent = True 
        if "documents" not in request.files:
            flash("No documents uploaded", "error")
            return redirect(url_for("home"))

        documents = request.files.getlist("documents")
        raw_text = get_doc_text(documents)

        if not raw_text:
            flash("No text extracted from documents", "error")
            return redirect(url_for("home"))

        text_chunks = get_text_chunks(raw_text)
        vector_store = get_vectorstore(text_chunks)
        conversation = get_conversation_chain(vector_store)
        session['chat_history'] = []

        flash("Documents processed successfully.", "success")
        return redirect(url_for("home"))

class AskQuestion(Resource):
    def post(self):
        """Handles question asking and returns the chat history."""
        global conversation

        session.permanent = True 
        if not conversation:
            return {"error": "No conversation initialized. Please process documents first."}, 400

        if request.content_type == "application/json":
            data = request.get_json()
            question = data.get("question")
        else:
            question = request.form.get("question")

        if not question:
            return {"error": "No question provided"}, 400

        response = conversation({'question': question})
        chat_history = response['chat_history']

        if 'chat_history' not in session:
            session['chat_history'] = []

        session['chat_history'].append({'user': question, 'bot': chat_history[-1].content})
        return redirect(url_for("home"))

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

