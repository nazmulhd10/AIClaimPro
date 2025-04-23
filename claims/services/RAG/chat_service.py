from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

# Step 1: Load the vector store
def load_vector_store(doc_id):
    return FAISS.load_local(f'vectors/{doc_id}', embeddings=OpenAIEmbeddings())

# Step 2: Create QA chain with a custom system prompt
def create_qa_chain(vector_store):
    system_prompt = """
    You are a helpful assistant. You answer questions about Claims on insurance company in the world. 
    But you only answer based on knowledge I'm providing you. You don't use your internal knowledge 
    and you don't make things up. If you don't know the answer, just say: I don't know.

    Always format your response in a clean, organized, professional layout using:
    - Headings and subheadings where applicable
    - Numbered or bulleted lists for clear breakdowns
    - Proper spacing and alignment for readability
    - Use Markdown-like styling (e.g. bold, italic, dividers)
    - Use horizontal lines (---) to separate sections
    """

    prompt = PromptTemplate(
        input_variables=["context", "question"],
        template="""
        {system_prompt}

        Context:
        {context}

        Question:
        {question}
        """.strip()
    )

    llm = ChatOpenAI(
        model="gpt-4",
        temperature=0.75,
    )

    return RetrievalQA.from_chain_type(
        llm=llm,
        retriever=vector_store.as_retriever(),
        chain_type="stuff",
        chain_type_kwargs={"prompt": prompt.partial(system_prompt=system_prompt)}
    )

# Step 3: Ask a question
def get_answer(query, qa_chain):
    return qa_chain.run(query)
