import os
import sys
import time
import pytz
import logging
from datetime import datetime
from dotenv import load_dotenv
import json
import jieba
import jieba.analyse
from collections import Counter
import pymongo
import configparser
from apscheduler.schedulers.background import BackgroundScheduler

import google.cloud.logging
from google.oauth2.service_account import Credentials


config = configparser.ConfigParser()
config.read('config.ini')

load_dotenv()
sys.path.append('../Credit_All_In_One/')
from my_configuration import _get_mongodb, _get_pgsql
import my_logger
from data_pipeline.etl_utils import insert_into_redis

# datetime
taiwanTz = pytz.timezone("Asia/Taipei") 

# Advanced Python Scheduler
scheduler = BackgroundScheduler()


if config['environment']['ENV'] == 'production':
    # GCP logging
    gcp_key = json.load(open(os.getenv("KEY")))
    credentials = Credentials.from_service_account_info(gcp_key)
    client = google.cloud.logging.Client(credentials=credentials)
    client.setup_logging()

    # create a logger
    dev_logger = logging.getLogger("data_pipeline:split_ptt_words:score_ptt_article")
else:
    # create a logger
    dev_logger = my_logger.MyLogger('etl')
    dev_logger.console_handler()
    dev_logger.file_handler(datetime.now(taiwanTz).strftime('%Y-%m-%d'))


jieba.set_dictionary('data_pipeline/txt_jieba/dict.txt.big') # simpified to tranditional chinese
jieba.load_userdict('data_pipeline/txt_jieba/custom_words.txt') # custom words
jieba.analyse.set_stop_words('data_pipeline/txt_jieba/stop_words.txt')
mongo_db = _get_mongodb()
pg_db = _get_pgsql()


def _find_top5_keywords(collection:str):
    """
    fetch latest ptt titles, push and articles info from MongoDB, find top 5 key words from each post of title and article
    :param collection: collection name which is the data source
    """
    mongo_collection = mongo_db[collection]
    max_create_dt = mongo_collection.find_one(sort=[('create_dt', pymongo.DESCENDING)])['create_dt']
    projection = {'post_title': 1, 'push': 1, 'article': 1, '_id': 0}
    try:
        cursor = mongo_collection.find({'create_dt':max_create_dt}, projection)
        ptt_posts = list(cursor) 
        dev_logger.info(json.dumps({'msg':f'Finish retrieving ptt titles and articles on {max_create_dt} updated documents.'}))
    except Exception as e:
        dev_logger.error(json.dumps({'msg':f'Failed to retrieve ptt titles and articles from MongoDB: {e}'}))
    else:
        cursor.close()
    
    counting = Counter()
    for doc in ptt_posts:
        tags = jieba.analyse.extract_tags(doc['post_title'] + '。' + doc['article'], topK=5, withWeight=False, allowPOS=())
        for tag in tags:
            if tag in counting:
                counting[tag] = counting[tag] + 1 + doc['push']
            else:
                counting[tag] = 1
    return counting


def _fetch_card_alias_name() -> list:
    # fetch distinct card_name and card_alias_name from PostgreSQL
    cursor = pg_db.cursor()
    try:
        cursor.execute("""
            SELECT ARRAY(
                SELECT UPPER(REPLACE(unnest(ARRAY[card_name] || string_to_array(card_alias_name,', ')), ' ', ''))
                ) AS card_names
            FROM card_dict
            ORDER BY card_name, card_alias_name;
            """)
        card_names = list(cursor)
        dev_logger.info(json.dumps({'msg':'Successfully fetch card names from PostgreSQL'}))
    except Exception as e:
        dev_logger.error(json.dumps({'msg':f'Failed to fetch card names from PostgreSQL: {e}'}))
    else:
        cursor.close()
    return card_names


def _count_num_of_appearance(counting, card_names):
    """
    matching a counting results for appearance and push of each cards
    :param counting:
    :param card_names:
    """
    new_counting = Counter()
    for key, value in counting.items():
        for card in card_names:
            if key.replace(' ','').upper() in card[0] or key.replace(' ','').upper()+'卡' in card[0]:
                new_counting[card[0][0]] += value
    return new_counting


def score_ptt_article(collection:str="ptt", redis_key:str="ptt_article"):
    """
    fetch all banks and cards info and calculate the appearance/push on ptt
    """
    # fetch latest ptt titles, push and articles info from MongoDB, find top 5 key words from each post of title and article
    counting = _find_top5_keywords(collection=collection)

    # fetch distinct card_name and card_alias_name from PostgreSQL
    card_names = _fetch_card_alias_name()

    # matching a counting results for appearance and push of each cards
    new_counting = _count_num_of_appearance(counting, card_names)
    
    # insert into redis
    insert_into_redis(logger=dev_logger, pipeline="score_ptt_articles", redis_key=redis_key, redis_value=new_counting)



if __name__ == '__main__':
    scheduler.add_job(
        score_ptt_article,
        trigger="cron",
        hour="0, 4, 8, 12, 16, 20",
        minute=7,
        timezone=pytz.timezone("Asia/Taipei"),
    )

    scheduler.start()
    dev_logger.info(json.dumps({'msg':'Scheduler started ...'}))


    while True:
        time.sleep(5)