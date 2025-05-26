
import os
import pandas as pd
from langchain_community.document_loaders import DataFrameLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain_core.runnables import Runnable


import os
from dotenv import load_dotenv

# ✅ Load environment variables
load_dotenv()

# ✅ Access your Gemini API key
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")


def build_chatbot(df: pd.DataFrame) -> Runnable:
    """Creates a QA chatbot using Gemini + FAISS vector store from Tesla trading data."""
    df['row_summary'] = df.apply(lambda row: row.to_string(), axis=1)
    print( df['row_summary'],"-----")
    # Step 1: Load dataframe into LangChain documents
    loader = DataFrameLoader(df, page_content_column="row_summary") 
     # You can use 'summary' column too if you have
    documents = loader.load()

    # Step 2: Split documents into manageable chunks
    splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = splitter.split_documents(documents)

    # Step 3: Embed chunks using Gemini embeddings
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

    # Step 4: Store in FAISS vector store
    vectorstore = FAISS.from_documents(chunks, embeddings)


    # Step 5: Create retriever-based QA chain with Gemini LLM
    llm = ChatGoogleGenerativeAI(model="models/gemini-1.5-flash")
    retriever = vectorstore.as_retriever()
    qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)

    return qa_chain
