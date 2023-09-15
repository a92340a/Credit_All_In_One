import os
import sys
import time
from datetime import datetime
from dotenv import load_dotenv

import pymongo
from py2neo import Node, Relationship, Graph, NodeMatcher, RelationshipMatcher


load_dotenv()

sys.path.append('../Credit_All_In_One/')
import my_logger

# datetime
now = datetime.now()
today_date = now.date()
today = now.strftime('%Y-%m-%d')
year = now.strftime('%Y')

# create a logger
dev_logger = my_logger.MyLogger('crawl')
dev_logger.console_handler()
dev_logger.file_handler(today)


def _get_mongodb():
    # connect to mongodb database: credit
    MONGO_CONFIG = f"mongodb://{os.getenv('MONGO_USERNAME')}:{os.getenv('MONGO_PASSWORD')}@{os.getenv('MONGO_HOST')}:{os.getenv('MONGO_PORT')}/credit?authMechanism={os.getenv('MONGO_AUTHMECHANISM')}"
    client = pymongo.MongoClient(MONGO_CONFIG) 
    return client['credit']


def _get_neo4j():
    # connect to neo4j database
    NEO4J_CONFIG = f"bolt://{os.getenv('NEO_HOST')}:{os.getenv('NEO_PORT')}"
    client = Graph(NEO4J_CONFIG, auth=(os.getenv('NEO_USER'), os.getenv('NEO_PASSWD')))
    return client


def tranforming():
    mongo_db = _get_mongodb()
    mongo_collection = mongo_db["blogs"]
    cursor_mongo = mongo_collection.find()
    record = []
    for data in cursor_mongo:
        record.append(data)
    dev_logger.info(f"Total records from mongodb['blogs']:{len(record)}. \n Show the first record:{record[0]}")
    
    neo4j_db = _get_neo4j()
    
    for i in record:
        if i['topic'] == '海外':
            neo_script = """
            UNWIND $content as content \
            MERGE (n1:銀行{發行銀行:content.bank}) \
            MERGE (n2:信用卡{信用卡名稱:content.card}) \
            MERGE (n3:海外消費{類型:$topic, 回饋率:content.reward_rate, 回饋上限:content.reward_limit, 生效期間:$valid_year ,標題:$page_title, 網址:$page_path}) \
            MERGE (n1)-[:發行]->(n2) \
            MERGE (n2)-[:提供權益]->(n3) \
            RETURN *;
            """
        if i['topic'] == '外送':
            neo_script = """
            UNWIND $content as content \
            MERGE (n1:銀行{發行銀行:content.bank}) \
            MERGE (n2:信用卡{信用卡名稱:content.card}) \
            MERGE (n3:外送優惠{類型:$topic, 回饋率:content.reward_rate, 回饋上限:content.reward_limit, 生效期間:$valid_year ,標題:$page_title, 網址:$page_path}) \
            MERGE (n1)-[:發行]->(n2) \
            MERGE (n2)-[:提供權益]->(n3) \
            RETURN *;
            """

        neo4j_db.run(neo_script, content=i['content'], topic=i['topic'], valid_year=i['valid_year'], page_title=i['page_title'], page_path=i['page_path'])

    
if __name__ == '__main__':
    tranforming()