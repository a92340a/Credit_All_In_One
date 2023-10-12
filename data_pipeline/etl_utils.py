import os
import sys
import time
from datetime import datetime
from dotenv import load_dotenv

from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores.chroma import Chroma

load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv('OPEN_KEY')

sys.path.append('../Credit_All_In_One/')
import my_logger
from my_configuration import _get_mongodb

persist_directory = './chroma_db'
embedding = OpenAIEmbeddings() # default: "text-davinci-003", try to find replacable embedding function


# datetime
now = datetime.now()
today_date = now.date()
today = now.strftime('%Y-%m-%d')

# create a logger
dev_logger = my_logger.MyLogger('etl')
dev_logger.console_handler()
dev_logger.file_handler(today)


def count_mongo_docs():
    mongo_db = _get_mongodb()
    mongo_collection = mongo_db["official_website"]
    return mongo_collection.count_documents({})
    

def get_chroma_content():
    vectordb = Chroma(persist_directory=persist_directory)
    # dev_logger.info(f'keys: {vectordb.get().keys()}')
    dev_logger.info(f'num of split contents:{len(vectordb.get()["ids"])}') 
    print(vectordb.get(include=["embeddings","documents", "metadatas"])) 


def truncate_chroma():
    vectordb = Chroma(persist_directory=persist_directory)
    vectordb.delete_collection()
    vectordb.persist()
    vectordb = None
    dev_logger.info('Truncate chromaDB collection.')
