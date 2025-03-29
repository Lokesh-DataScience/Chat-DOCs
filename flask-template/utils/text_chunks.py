from PyPDF2 import PdfReader
import docx
from langchain.text_splitter import CharacterTextSplitter

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

    # Return filenames instead of setting session here
    return text, filenames

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