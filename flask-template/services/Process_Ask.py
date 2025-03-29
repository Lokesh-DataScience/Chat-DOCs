from flask import request, jsonify
from flask_restful import Resource
from utils.text_chunks import get_doc_text, get_text_chunks
from utils.vector_db import get_vectorstore
from utils.conversation_chains import get_conversation_chain

# Global variable for conversation chain
conversation = None

class ProcessDocuments(Resource):
    def post(self):
        """Processes uploaded documents and creates a conversation chain."""
        global conversation

        # Check if files are uploaded
        if "documents" not in request.files:
            return jsonify({"error": "No documents uploaded"}), 400

        documents = request.files.getlist("documents")
        raw_text, filenames = get_doc_text(documents)

        if not raw_text:
            return jsonify({"error": "No text extracted from documents"}), 400

        # Create text chunks and vector store
        text_chunks = get_text_chunks(raw_text)
        vector_store = get_vectorstore(text_chunks)
        conversation = get_conversation_chain(vector_store)

        return jsonify({
            "message": "Documents processed successfully",
            "files": filenames
        }), 200


class AskQuestion(Resource):
    def post(self):
        """Handles question asking and returns the chat history."""
        global conversation

        if not conversation:
            return jsonify({"error": "No documents processed yet"}), 400

        # Handle both JSON and form data inputs
        if request.content_type == "application/json":
            data = request.get_json()
            question = data.get("question")
        else:
            question = request.form.get("question")

        if not question:
            return jsonify({"error": "No question provided"}), 400

        # Get response from conversation chain
        response = conversation({'question': question})
        chat_history = response['chat_history']

        return jsonify({
            "question": question,
            "response": chat_history[-1].content
        }), 200
