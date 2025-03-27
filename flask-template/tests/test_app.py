import pytest
from app import app as flask_app
from io import BytesIO

@pytest.fixture
def client():
    """ Create a test client for the Flask app """
    with flask_app.test_client() as client:
        yield client


# ✅ Test Home and About Routes
def test_home(client):
    """ Test the home route """
    response = client.get("/")
    assert response.status_code == 200
    assert b"Document Processing and Q&A" in response.data


def test_about(client):
    """ Test the about route """
    response = client.get("/about")
    assert response.status_code == 200
    assert b"About This App" in response.data


# ✅ Test Document Processing
def test_process_documents_success(client):
    """ Test document processing with valid PDF upload """
    data = {
        "documents": (BytesIO(b"PDF test content"), "test.pdf")
    }
    response = client.post("/process", data=data, content_type='multipart/form-data')
    assert response.status_code == 200
    assert b"Documents processed successfully" in response.data


def test_process_documents_invalid_file(client):
    """ Test document processing with an invalid file type """
    data = {
        "documents": (BytesIO(b"Invalid file content"), "invalid.exe")
    }
    response = client.post("/process", data=data, content_type='multipart/form-data')
    assert response.status_code == 400
    assert b"No readable content found" in response.data


def test_process_documents_no_file(client):
    """ Test document processing without file upload """
    response = client.post("/process", content_type='multipart/form-data')
    assert response.status_code == 400
    assert b"No documents uploaded" in response.data


# ✅ Test Question Asking
def test_ask_question_no_conversation(client):
    """ Test asking a question without a conversation initialized """
    response = client.post("/ask", data={"question": "What is AI?"})
    assert response.status_code == 400
    assert b"No conversation initialized" in response.data


def test_ask_question_missing_field(client):
    """ Test asking without providing a question """
    response = client.post("/ask", data={})
    assert response.status_code == 400
    assert b"No question provided" in response.data


def test_ask_question_with_conversation(client):
    """ Test asking a question after processing a document """
    # Simulate document processing
    client.post("/process", data={
        "documents": (BytesIO(b"Sample document content"), "test.txt")
    }, content_type='multipart/form-data')

    # Ask a question
    response = client.post("/ask", data={"question": "What is AI?"})
    assert response.status_code == 200
    assert b"response" in response.data  # Ensure response key is present in JSON response
