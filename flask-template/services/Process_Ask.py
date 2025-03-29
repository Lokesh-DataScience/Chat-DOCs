from flask import request, session, redirect, url_for, flash
from flask_restful import Resource
from utils.text_chunks import get_doc_text, get_text_chunks
from utils.vector_db import get_vectorstore
from utils.conversation_chains import get_conversation_chain
conversation = None 
class ProcessDocuments(Resource):
    def post(self):
        """Processes uploaded documents and creates a conversation chain."""
        global conversation

        session.permanent = True 
        if "documents" not in request.files:
            flash("No documents uploaded", "error")
            return redirect(url_for("home"))

        documents = request.files.getlist("documents")
        raw_text, filenames = get_doc_text(documents) 

        if not raw_text:
            flash("No text extracted from documents", "error")
            return redirect(url_for("home"))

        text_chunks = get_text_chunks(raw_text)
        vector_store = get_vectorstore(text_chunks)
        conversation = get_conversation_chain(vector_store)

        session['uploaded_files'] = filenames
        session['chat_history'] = []

        flash("Documents processed", "success")
        return redirect(url_for("home"))
    
class AskQuestion(Resource):
    def post(self):
        """Handles question asking and returns the chat history."""
        global conversation

        session.permanent = True 
        if not conversation:
            flash("No documents processed yet", "error")
            return redirect(url_for("home")) 

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