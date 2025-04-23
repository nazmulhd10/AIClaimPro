import os
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OpenAIEmbeddings

def generate_and_save_vector(document_instance):
    pdf_path = document_instance.contract_documents.path
    loader = PyMuPDFLoader(pdf_path)
    pages = loader.load()

    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_documents(pages, embeddings)

    vector_dir = f'vectors/{document_instance.id}/'
    os.makedirs(vector_dir, exist_ok=True)
    vectorstore.save_local(vector_dir)
