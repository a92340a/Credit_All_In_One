import os
import sys
import time
import random
from datetime import datetime
from dotenv import load_dotenv
from fastapi.encoders import jsonable_encoder
import pymongo

from langchain.document_loaders import WebBaseLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma

load_dotenv()

sys.path.append('../Credit_All_In_One/')
import my_logger

persist_directory = './chroma_db'
embedding = OpenAIEmbeddings() # default: "text-davinci-003", try to find replacable embedding function


# datetime
now = datetime.now()
today_date = now.date()
today = now.strftime('%Y-%m-%d')

# create a logger
dev_logger = my_logger.MyLogger('crawl')
dev_logger.console_handler()
dev_logger.file_handler(today)


def _get_mongodb():
    """ connect to mongodb database: credit """
    MONGO_CONFIG = f"mongodb://{os.getenv('MONGO_USERNAME')}:{os.getenv('MONGO_PASSWORD')}@{os.getenv('MONGO_HOST')}:{os.getenv('MONGO_PORT')}/credit?authMechanism={os.getenv('MONGO_AUTHMECHANISM')}"
    client = pymongo.MongoClient(MONGO_CONFIG) 
    return client['credit']


# ========= data loading, embedding ========= 

def list_target_url(BANK):
    """
    List the credit card introduction url between banks
    """
    page_list_all = []
    for bk in BANK:
        page_list_bk = []
        for i in range(len(bk['url'])):
            try:
                page = bk['function'](bk['url'][i])
                page_list_bk.extend(list(set(page)))
                page_list_bk = list(set(page_list_bk))
            except Exception as e:
                dev_logger.warning(e)
                dev_logger.warning('Fail to listing the {} from {}.'.format(bk['url'][i], bk['function'].__name__))
        page_list_all.append({'bank':bk['function'].__name__, 'urls':page_list_bk})
        dev_logger.info('Finish listing {}.'.format(bk['function'].__name__))
    return page_list_all    


def load_data(url):
    """
    Use LangChain loader(crawling) to fetch html content
    """
    time.sleep(random.randint(3,5))
    try:
        if 'pdf' in url:
            loader = PyPDFLoader(url)
            text = loader.load_and_split()
        else:
            loader = WebBaseLoader(url)
            text = loader.load()
        dev_logger.info(f'Finish loading {url}.')
    except Exception as e:
        dev_logger.warning(e)
        dev_logger.warning(f'Fail to loading the data from {url}.')    
    return text


def insert_into_mongo(bank, url, text):
    """ 
    Save into MongoDB to routine schedule and HA purpose
    """
    upload_data = {'source':bank, 
                   'url': url,
                   'content':jsonable_encoder(text), # fastapi.encoders.jsonable_encoder()
                   'create_date':today,
                   'create_timestamp':int(time.time())
                   }
    
    mongo_db = _get_mongodb()
    mongo_collection = mongo_db["official_web"]
    mongo_collection.insert_one(upload_data)
    dev_logger.info(f'Finish inserting into MongoDB {bank}, \n {url}.')


def insert_into_chroma(bank, url, text, chunk_size=200, chunk_overlap=40):
    """
    Split text and convert to vectors into ChromaDB
    """
    # 3. split text
    text_splitter = RecursiveCharacterTextSplitter(        
        chunk_size = chunk_size,
        chunk_overlap = chunk_overlap,
    )
    split_texts = text_splitter.split_documents(text) # create_documents(text)?

    # 4. Initialize PersistentClient and collection
    vectordb = Chroma.from_documents(documents=split_texts, embedding=embedding, 
                                     persist_directory=persist_directory) 
    vectordb.persist()
    vectordb = None
    dev_logger.info(f'Finish inserting into ChromaDB {bank}, \n {url}.')


def check_data_updated(url, text):
    text_json = jsonable_encoder(text)
    mongo_db = _get_mongodb()
    mongo_collection = mongo_db["official_web"]
    pipeline = [{'$match': {'url': url}},
                {'$group': {'_id': '$url', 'max_timestamp': {'$max': '$create_timestamp'}}}]
    result = list(mongo_collection.aggregate(pipeline))

    if result:
        max_timestamp = result[0]['max_timestamp']
        query = {'create_timestamp': max_timestamp}
        document = mongo_collection.find_one(query)
        if document['content'][0]['page_content'] == text_json[0]['page_content']:
            dev_logger.info('The content loaded today is the same as the newest content in MongoDB!')
            return False
    else:
        return True


# ========== healthy check ===========
def select_mongo_schema():
    mongo_db = _get_mongodb()
    mongo_collection = mongo_db["official_web"]
    return mongo_collection.count_documents({})
    

def get_chroma_schema():
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
    

