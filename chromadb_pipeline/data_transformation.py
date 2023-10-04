import os
import sys
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv

from langchain.schema import Document
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma


load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv('OPEN_KEY')

sys.path.append('../Credit_All_In_One/')
import my_logger
from my_configuration import _get_mongodb


mongo_db = _get_mongodb()
mongo_collection = mongo_db["official_website"]
persist_directory = './chroma_db'
embedding = OpenAIEmbeddings() # default: "text-davinci-003", try to find replacable embedding function


# datetime
now = datetime.now()
today_date = now.date()
today = now.strftime('%Y-%m-%d')
yesterday = (today_date-timedelta(days=1)).strftime('%Y-%m-%d')


# create a logger
dev_logger = my_logger.MyLogger('data_transforamtion')
dev_logger.console_handler()
dev_logger.file_handler(today)



def get_distinct_source_and_link():
    """
    Getting distinct source and link
    """
    pipeline = [{"$group": {"_id": {"source": "$source", "card_link": "$card_link"}}}]
    result = mongo_collection.aggregate(pipeline)
    
    source_list = {}
    for doc in result:
        source = doc['_id']['source']
        card_link = doc['_id']['card_link']
        
        if source in source_list:
            source_list[source].append(card_link)
        else:
            source_list[source] = [card_link]
    return source_list


def data_comparing_and_rebuilding(data):
    """
    Compare the difference in card_content between yesterday and today.
    :param:data: The data between these 2 days. For example: [{'_id': ObjectId('651bd25a646a02fa2d4205b1'), 'source': ..., 'create_dt': '2023-10-03'}, ...]
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
                            page_content=content['card_content'],
                            metadata={'bank': content['bank_name'], 'card_name': content['card_name'], 'url': content['card_link']},
                        )]
                        dev_logger.info('Build a new Document and ready for ChromaDB: {}'.format(content['card_name']))
                        return docs
            else:
                dev_logger.info('The card_content is the same. Do nothing!: {}'.format(data[0]['card_name']))
        elif len(compare) == 1:
            if data[0]['create_dt'] == today:
                docs = [Document(
                    page_content=data[0]['card_content'],
                    metadata={'bank': data[0]['bank_name'], 'card_name': data[0]['card_name'], 'url': data[0]['card_link']},
                )]
                dev_logger.info('Build a new Document and ready for ChromaDB: {}'.format(data[0]['card_name']))
                return docs
            else:
                dev_logger.info('The card_content is depreciated. Do nothing!: {}'.format(data[0]['card_name']))
    else:
        dev_logger.info('No data.')
        

def insert_into_chroma(bank_name, card_link, text):
    """
    Split text and convert to vectors into ChromaDB
    :param:bank_name: data source of the bank crawled,
    :param:card_link: data source of the bank's url, 
    :param:text: card content
    """
    vectordb = Chroma.from_documents(documents=text, embedding=embedding, 
                                     persist_directory=persist_directory) 
    vectordb.persist()
    vectordb = None
    dev_logger.info(f'Finish inserting into ChromaDB {bank_name}, \n {card_link}.')


if __name__ == '__main__':
    # fetch distinct data from MongoDB
    src_list = get_distinct_source_and_link()

    # loop for comparision and insert into ChromaDB
    for bank, links in src_list.items():
        for link in links:
            cursor = mongo_collection.find({
                "$and": [
                    {'card_link': link}, 
                    {'create_dt': {'$gte': yesterday, '$lte': today}}
                ]
            })
            data_comparision = list(cursor) 
            print(data_comparision)
            print('-----')

            new_docs = data_comparing_and_rebuilding(data_comparision)
            insert_into_chroma(bank, link, new_docs)
