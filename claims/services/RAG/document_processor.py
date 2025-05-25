import mimetypes
import os
import fitz  # PyMuPDF
from langchain.text_splitter import CharacterTextSplitter
import requests


def extract_text_from_pdf(file_path):
    print(f"Extracting text from================================= {file_path}")
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def extract_text_from_n8n(full_path):
    file_name = os.path.basename(full_path)
    mime_type, _ = mimetypes.guess_type(full_path)

    webhook_url = "http://localhost:5678/webhook-test/83483438-c3a0-4a35-ba55-5f9b38ead927"

    with open(full_path, 'rb') as f:
        files = {
            'contract_documents': (file_name, f, mime_type)  # ✅ Correct 3-tuple
        }

        data = {
            'formMode': 'test',  # Keep form mode as test
            'mimeType': mime_type,  # MIME type from request.FILES
        }

        response = requests.post(webhook_url, data=data, files=files)
        print("✅ Webhook Response:", response.status_code, response.text)
        return ""

def chunk_text(text):
    splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    return splitter.split_text(text)
