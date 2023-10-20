import os
import sys
import time
import json
import pytz
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv
import pymongo
from apscheduler.schedulers.background import BackgroundScheduler

import google.cloud.logging
from google.oauth2.service_account import Credentials
from langchain.schema import Document
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores.chroma import Chroma


load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv('OPEN_KEY')

sys.path.append('../Credit_All_In_One/')
from my_configuration import _get_mongodb

# Advanced Python Scheduler
scheduler = BackgroundScheduler()

# GCP logging
gcp_key = json.load(open(os.getenv("KEY")))
credentials = Credentials.from_service_account_info(gcp_key)
client = google.cloud.logging.Client(credentials=credentials)
client.setup_logging()

mongo_db = _get_mongodb()
mongo_collection = mongo_db["official_website"]
persist_directory = './chroma_db'
embedding = OpenAIEmbeddings() # default: "text-davinci-003", try to find replacable embedding function


# datetime
taiwanTz = pytz.timezone("Asia/Taipei") 
now = datetime.now(taiwanTz)
today_date = now.date()
today = now.strftime('%Y-%m-%d')
yesterday = (today_date-timedelta(days=1)).strftime('%Y-%m-%d')


# create a logger
dev_logger = logging.getLogger("data_pipeline:credit_docs_transformation:docs_comparing_and_embedding")

def _docs_refactoring(data: list) -> list:
    """
    Compare the difference in card_content between yesterday and today.
    :param data: The data between these 2 days. For example: [{'_id': ObjectId('651bd25a646a02fa2d4205b1'), 'source': ..., 'create_dt': '2023-10-03'}, ...]
    """
    if data: 
        # fetch card_content between yesterday and today
        compare = dict()
        for i in range(len(data)):
            # For example: {'2023-10-03': card_content_1, {'2023-10-02': card_content_2}
            compare[data[i]['create_dt']] = data[i]['card_content']

        # build the Document when data is newest information today, or do nothing
        if len(compare) == 2:
            if compare[today] != compare[yesterday]:
                for index, content in enumerate(data):
                    if content['create_dt'] == today:
                        docs = [Document(
                            page_content=content['card_name']+':'+content['card_content']+'。'+content['card_link'],
                            metadata={'bank': content['bank_name'], 'card_name': content['card_name']},
                        )]
                        dev_logger.info(json.dumps({'msg':'Build a new Document and ready for ChromaDB: {}'.format(content['card_name'])}))
                        return docs
            else:
                dev_logger.info(json.dumps({'msg':'The card_content is the same. Do nothing!: {}'.format(data[0]['card_name'])}))
        elif len(compare) == 1:
            if data[0]['create_dt'] == today:
                docs = [Document(
                    page_content=data[0]['card_name']+':'+data[0]['card_content']+'。'+data[0]['card_link'],
                    metadata={'bank': data[0]['bank_name'], 'card_name': data[0]['card_name']},
                )]
                dev_logger.info(json.dumps({'msg':'Build a new Document and ready for ChromaDB: {}'.format(data[0]['card_name'])}))
                return docs
            else:
                dev_logger.info(json.dumps({'msg':'The card_content is depreciated. Do nothing!: {}'.format(data[0]['card_name'])}))
    else:
        dev_logger.warning(json.dumps({'msg':'No data.'}))
        

def _insert_into_chroma(card_name, docs, persist_directory=persist_directory):
    """
    Docs embedding and converting into vectors
    :param card_name: data source of the card name, 
    :param docs: card content
    """
    vectordb = Chroma.from_documents(documents=docs, embedding=embedding, 
                                     persist_directory=persist_directory) 
    vectordb.persist()
    vectordb = None
    dev_logger.info(json.dumps({'msg':'Finish inserting into ChromaDB {}.'.format(card_name)}))


def docs_comparing_and_embedding(*manual):
    distinct_card_names = sorted(mongo_collection.distinct('card_name'))
    
    if manual:
        max_create_dt = mongo_collection.find_one(sort=[('create_dt', pymongo.DESCENDING)])['create_dt']
        dev_logger.info(json.dumps({'msg':'Manually fetch docs at {}...'.format(max_create_dt)}))
        # print(max_create_dt) 
        
        for card in distinct_card_names:
            cursor = mongo_collection.find({
                "$and": [
                    {'card_name': card}, 
                    {'create_dt':max_create_dt}
                ]
            })
            data_latest = list(cursor)
            # print(data_latest) 

            for index, content in enumerate(data_latest):
                new_docs = [Document(
                    page_content=content['card_name']+':'+content['card_content']+'。'+content['card_link'],
                    metadata={'bank': content['bank_name'], 'card_name': content['card_name']},
                )]
                dev_logger.info(json.dumps({'msg':'Build a new Document and ready for ChromaDB: {}'.format(content['card_name'])}))
                # print(new_docs)
                # print('-----')
                if new_docs:
                    _insert_into_chroma(card, new_docs, persist_directory=persist_directory)
                    # print('-----')

    else:
        dev_logger.info(json.dumps({'msg':'Schedulely fetch docs...'}))
        for card in distinct_card_names:
            cursor = mongo_collection.find({
                "$and": [
                    {'card_name': card}, 
                    {'create_dt': {'$gte': yesterday, '$lte': today}}
                ]
            })
            data_comparision = list(cursor) 
            # print(data_comparision)
            # print('-----')

            new_docs = _docs_refactoring(data_comparision)
            if new_docs:
                _insert_into_chroma(card, new_docs)
                # print('-----')


def test_scheduler():
    print('hello from credit_docs_transformation')


#scheduler.add_job(test_scheduler, "interval", seconds=5)
#scheduler.add_job(docs_comparing_and_embedding, "interval", minutes=5)
scheduler.add_job(
    docs_comparing_and_embedding,
    trigger="cron",
    hour="0, 4, 8, 12, 16, 20",
    minute=0,
    timezone=pytz.timezone("Asia/Taipei"),
)

scheduler.start()
dev_logger.info(json.dumps({'msg':'Scheduler started ...'}))


while True:
    time.sleep(5)
