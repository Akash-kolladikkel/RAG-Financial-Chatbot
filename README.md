# RAG-Based Financial Chatbot 💼  

A financial document assistant that uses Retrieval-Augmented Generation (RAG) to analyze and extract insights from financial PDFs. This chatbot leverages advanced AI models for embeddings, document parsing, and conversational responses, providing precise answers to user queries.

---

## 🚀 Features  

- **PDF Parsing**: Extract text from financial documents with high accuracy.  
- **Embeddings Storage**: Efficiently store semantic embeddings using ChromaDB.  
- **Financial Insights**: Generate detailed responses to queries about Profit & Loss (P&L) statements and other financial data.  
- **Interactive UI**: Simple and intuitive Streamlit interface for uploading documents and asking questions.  
- **Streamlit Deployment**: Easily deploy and access the app on the Streamlit Community Cloud.

---

## 🌐 Access the Web App  

The financial document assistant is deployed and accessible on Streamlit Cloud. You can access the web app here:  

[**Financial Document Assistant - Web App**](https://rag-financial-chatbot-ak.streamlit.app/)
![ss](https://github.com/Akash-kolladikkel/RAG-Financial-Chatbot/blob/d8ea1671f2ae1ccdd20552a0881f25d328513c83/rag2.png)

---

## 🛠️ Tech Stack  

- **Frameworks & Libraries**:  
  - Streamlit  
  - LangChain  
  - ChromaDB  
  - Hugging Face Embeddings  
  - Llama Cloud for PDF parsing  

- **APIs**:  
  - Groq API for conversational AI  
  - Llama Cloud API for document parsing  

---

## 🧠 How It Works  

1. **Upload a PDF**: Upload a financial document.  
2. **Data Processing**: The system parses the document and stores semantic embeddings in a ChromaDB instance.  
3. **Question & Answer**: Ask financial questions, and the chatbot provides detailed responses using retrieval-augmented generation.  

---

## 🐳 Run Locally Using Docker  

You can also run the financial chatbot locally using Docker. Follow these steps:

### Prerequisites  
1. **Docker** installed on your machine.  
2. **API Keys** for Groq and Llama Cloud.  

### Steps to Run  
1. Clone this repository:  
   ```bash
   git clone https://github.com/Akash-kolladikkel/RAG-Financial-Chatbot.git
   cd RAG-Financial-Chatbot 
2. Rename .env.example to .env and add your API keys:
   - GROQ_API_KEY=your_groq_api_key_here
   - LLAMA_CLOUD_API_KEY=your_llama_cloud_api_key_here
3. Build the Docker image:
   ```bash
   docker build -t financial-chatbot .
4. Run the Docker container:
   ```bash
    docker run -p 8501:8501 --env-file .env financial-chatbot
5. Open your browser and navigate to http://localhost:8501.
   
