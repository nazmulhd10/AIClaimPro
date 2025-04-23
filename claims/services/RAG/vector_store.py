from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS

embeddings = OpenAIEmbeddings()

def create_vector_store(chunks):
    """Create a FAISS vector store from text chunks."""
    if not chunks:
        pass
        # raise ValueError("No chunks found to create vector store. Please check your document loading process.")

    embeddings = OpenAIEmbeddings()
    return FAISS.from_texts(chunks, embedding=embeddings)

def update_vector_store(vs, new_chunks):
    vs.add_texts(new_chunks)
