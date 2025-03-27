from flask import Flask, request, render_template, jsonify
from flask_restful import Api, Resource
from dotenv import load_dotenv
from PyPDF2 import PdfReader
import docx
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
app = Flask(__name__)
api = Api(app)

conversation = None  # Global variable for storing the conversation chain

# 📌 Helper functions
def get_doc_text(documents):
    """Extracts text from PDF, DOCX, and TXT files."""
    text = ""
    for doc in documents:
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

        if "documents" not in request.files:
            return {"error": "No documents uploaded"}, 400

        documents = request.files.getlist("documents")
        raw_text = get_doc_text(documents)

        if not raw_text:
            return {"error": "No text extracted from documents"}, 400

        text_chunks = get_text_chunks(raw_text)
        vector_store = get_vectorstore(text_chunks)
        conversation = get_conversation_chain(vector_store)

        return {"message": "Documents processed successfully!"}

class AskQuestion(Resource):
    def post(self):
        """Handles question asking and returns the chat history."""
        global conversation

        if not conversation:
            return {"error": "No conversation initialized. Please process documents first."}, 400

        # Handle form and JSON-based requests
        if request.content_type == "application/json":
            data = request.get_json()
            question = data.get("question")
        else:
            question = request.form.get("question")

        if not question:
            return {"error": "No question provided"}, 400

        response = conversation({'question': question})
        chat_history = response['chat_history']

        return {
            "response": chat_history[-1].content,
            "chat_history": [
                {"user": msg.content} if i % 2 == 0 else {"bot": msg.content}
                for i, msg in enumerate(chat_history)
            ]
        }

# 🌐 HTML Page Routes
@app.route("/")
def home():
    return render_template("home.html")

@app.route("/about")
def about():
    return render_template("about.html")

# ✅ Register RESTful API Endpoints
api.add_resource(ProcessDocuments, '/api/process-docs')
api.add_resource(AskQuestion, '/api/ask')

if __name__ == "__main__":
    load_dotenv()
    app.run(debug=True)
