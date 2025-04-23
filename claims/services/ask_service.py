import chromadb
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

# Setting the environment
DATA_PATH = r"media/contract_documents/"
CHROMA_PATH = r"chroma_db"

chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)

def get_answer_from_query(user_query):
    """Process the user query and return the response."""
    collection = chroma_client.get_or_create_collection(name="contract_documents")

    # Query the ChromaDB collection
    results = collection.query(
        query_texts=[user_query],
        n_results=4
    )

    # Extract documents and metadata
    documents = results['documents']
    metadatas = results['metadatas']

    # Prepare the system prompt
    system_prompt = f"""
    You are a helpful assistant. You answer questions about Claims on insurance company in the world. 
    But you only answer based on knowledge I'm providing you. You don't use your internal 
    knowledge and you don't make things up. If you don't know the answer, just say: I don't know.

    Always format your response in a clean, organized, professional layout using:
    - Headings and subheadings where applicable
    - Numbered or bulleted lists for clear breakdowns
    - Proper spacing and alignment for readability
    - Use Markdown-like styling (e.g. bold, italic, dividers)
    - Use horizontal lines (---) to separate sections

    --------------------
    The data:
    {str(documents)}
    """

    # OpenAI client
    client = OpenAI()

    # Generate response
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_query}
        ]
    )

    # Return the response and metadata
    return {
        "answer": response.choices[0].message.content,
        "documents": documents,
        "metadatas": metadatas
    }