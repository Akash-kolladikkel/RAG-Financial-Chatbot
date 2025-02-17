__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import os
import streamlit as st
import chromadb
from uuid import uuid4
from langchain_chroma import Chroma
from langchain_groq import ChatGroq
from langchain_experimental.text_splitter import SemanticChunker
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_huggingface import HuggingFaceEmbeddings
from llama_parse import LlamaParse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
LLAMA_CLOUD_API_KEY = os.getenv('LLAMA_CLOUD_API_KEY')

# Function to parse and process PDF
def process_pdf(file):
    with open("temp.pdf", "wb") as f:
        f.write(file.getbuffer())
    
    instruction = """ The provided document contains Condensed Consolidated Financial Statements of Infosys"""
    document = LlamaParse(api_key=LLAMA_CLOUD_API_KEY, result_type="markdown", complemental_formatting_instruction=instruction).load_data("temp.pdf")
    document_text = "\n".join([doc.text for doc in document])
    return document_text

# Function to split text and store embeddings
def store_embeddings(text):
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    splitter = RecursiveCharacterTextSplitter(chunk_size=3000,chunk_overlap=500,separators=["\n\n", "\n", " ", ""])

    chunks, ids = [], []
    for chunk in splitter.split_text(text):
        chunks.append(chunk)
        ids.append(str(uuid4()))

    vectors = embeddings.embed_documents(chunks)

    # Persistent Chroma client
    client = chromadb.PersistentClient(path="chroma_db")
    collection = client.get_or_create_collection(name="Financial_DB")
    collection.add(documents=chunks, embeddings=vectors, ids=ids)
    
    return client, embeddings

# Function to create the chatbot chain
def create_chain(client, embeddings):
    vectorstore = Chroma(client=client, collection_name="Financial_DB", embedding_function=embeddings)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
    
    llm = ChatGroq(temperature=0.5, model_name="llama-3.1-8b-instant", groq_api_key=GROQ_API_KEY)
    prompt_template = """
    You are a financial analyst assistant trained to answer questions based on Profit & Loss (P&L) tables and financial statements. Follow these instructions carefully:

    1. **Contextual Understanding**: Read the context thoroughly before answering. Pay attention to financial terms, dates, and numerical values.
    2. **Detail-Oriented**: Provide a detailed and accurate answer that directly addresses the user's question. Include specific numbers, percentages, or trends where applicable.
    3. **Proactive Responses**: If you cannot find a specific answer in the context, try to provide a related answer or explain why the information is unavailable. Use phrases like:
    - "🤔 Hmm, I cannot find the exact information in the P&L tables."
    - "Based on the available data, here’s what I can tell you..."
    4. **Comparisons and Trends**: If the question involves comparisons (e.g., revenue vs. expenses) or trends (e.g., growth over time), analyze the data and provide a clear explanation.
    5. **Source Attribution**: Always specify the source of the data (e.g., "According to the Q1 2023 P&L table...").
    6. **Clarity and Formatting**: Use bullet points, tables, or clear paragraphs to present your answer. Ensure the response is easy to read and understand.

    ---

    Context:
    {context}

    ---

    Question:
    {question}

    ---

    Answer:
    """
    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])

    chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    return chain

# Response generation function
def get_response(chain, question):
    response = chain.invoke(question)
    return response

# Streamlit frontend functionality
def main():
    st.set_page_config(
        page_title="Financial Document Assistant",
        page_icon="💼",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    st.title("💼 Financial Document Assistant")
    st.write("Upload a financial document and get instant insights!")

    # Sidebar for file upload
    with st.sidebar:
        st.header("📄 Document Upload")
        uploaded_file = st.file_uploader("Choose a PDF file", type="pdf", help="Upload a financial PDF document")
        
        with st.expander("🤔 How to Use"):
            st.markdown("""
            ### Getting Started
            1. Upload your financial PDF
            2. Wait for processing confirmation
            3. Ask detailed questions about the document
                        
            ### Example Questions
            - "What are the total expenses for Q2 2023?"
            - "Show the operating margin for the past 6 months"
            - "Compare revenue growth between different quarters"
            """)

    # Check if a file is uploaded
    if uploaded_file:
        if 'processed_data' not in st.session_state:
            with st.spinner("Processing PDF..."):
                # Process and store embeddings only once
                document_text = process_pdf(uploaded_file)
                client, embeddings = store_embeddings(document_text)
                chain = create_chain(client, embeddings)
                
                # Save to session state
                st.session_state.processed_data = {
                    "chain": chain,
                    "document_text": document_text,
                }
            st.success("Document processed successfully!")
        else:
            st.info("Document already processed. Ready for questions!")

        # Chat interface
        st.subheader("💬 Financial Analysis Chat")
        if 'messages' not in st.session_state:
            st.session_state.messages = []

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # User input
        if prompt := st.chat_input("Ask a financial question"):
            st.session_state.messages.append({"role": "user", "content": prompt})

            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                with st.spinner("Generating analysis..."):
                    chain = st.session_state.processed_data["chain"]
                    response = get_response(chain, prompt)
                    st.markdown(response)

            st.session_state.messages.append({"role": "assistant", "content": response})
    else:
        st.info("Please upload a financial PDF document to begin analysis.")

if __name__ == "__main__":
    main()
