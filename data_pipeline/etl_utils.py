import os
import sys
import time
import pytz
import json
from datetime import datetime
from dotenv import load_dotenv

from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores.chroma import Chroma

load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv('OPEN_KEY')

sys.path.append('../Credit_All_In_One/')
import my_logger
from my_configuration import _get_mongodb, _get_redis


persist_directory = './chroma_db'
embedding = OpenAIEmbeddings() # default: "text-davinci-003", try to find replacable embedding function



# datetime
taiwanTz = pytz.timezone("Asia/Taipei") 
now = datetime.now(taiwanTz)
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
    # print(vectordb.get(include=["embeddings","documents", "metadatas"])) 


def truncate_chroma():
    vectordb = Chroma(persist_directory=persist_directory)
    vectordb.delete_collection()
    vectordb.persist()
    vectordb = None
    dev_logger.info('Truncate chromaDB collection.')


def insert_into_redis(logger, pipeline:str, redis_key:str, redis_value:dict, max_retries:int = 5, delay:int = 2):
    redis_conn = _get_redis()
    for trying in range(1, max_retries + 1):
        try:
            redis_conn.set(redis_key, json.dumps(redis_value))
            logger.info(json.dumps({'msg':f'Finish inserting {pipeline} into Redis'}))
            break
        except Exception as e:
            logger.warning(
                json.dumps({'msg':
                    f"Failed to set value of {pipeline} in Redis: {e}"
                    f"Attempt {trying + 1} of {max_retries}. Retrying in {delay} seconds."})
            )
            if trying == max_retries:
                logger.error(json.dumps({'msg':f"Failed to set value of {pipeline} in {max_retries} attempts"}))
            time.sleep(delay)


if __name__ == '__main__':
    get_chroma_content()