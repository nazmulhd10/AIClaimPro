import os
from django.conf import settings  # Django settings import করা হয়েছে

from claims.services.RAG.document_processor import chunk_text, extract_text_from_n8n, extract_text_from_pdf
from claims.services.RAG.vector_store import create_vector_store

CONTRACT_DIR = os.path.join(settings.MEDIA_ROOT, 'contract_documents')  # Absolute path

def build_initial_vector_store():
    all_chunks = []

    # Check if the directory exists
    if not os.path.exists(CONTRACT_DIR):
        print(f"Directory '{CONTRACT_DIR}' not found. Skipping vector store creation.")
        return create_vector_store([])  # Return an empty vector store

    for file in os.listdir(CONTRACT_DIR):
        if file.endswith(".pdf"):
            full_path = os.path.join(CONTRACT_DIR, file)
            text = extract_text_from_pdf(full_path)
            # text = extract_text_from_n8n(full_path)
            chunks = chunk_text(text)
            all_chunks.extend(chunks)

    return create_vector_store(all_chunks)
