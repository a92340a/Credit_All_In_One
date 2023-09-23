import os
from dotenv import load_dotenv

from langchain.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma


persist_directory = './chroma_db'
embedding = OpenAIEmbeddings() # default: “text-davinci-003”


def insert_data(url, chunk_size=500, chunk_overlap=100):
    """
    Params:
    url: target url for crawler
    chunk_size: the token size of text splitter
    chunk_overlap: the token size of overlapping text split 
    """
    # 1. loading input(crawler)
    loader = WebBaseLoader(url)
    web_text = loader.load()

    # 2. split text
    text_splitter = RecursiveCharacterTextSplitter(        
        chunk_size = chunk_size,
        chunk_overlap = chunk_overlap,
    )
    split_texts = text_splitter.split_documents(web_text)

    # 3. Initialize PersistentClient and collection
    vectordb = Chroma.from_documents(documents=split_texts, embedding=embedding, 
                                     persist_directory=persist_directory, metadatas=[{"source": "ts_agogo"} for i in range(len(split_texts))])
    vectordb.persist()
    vectordb = None