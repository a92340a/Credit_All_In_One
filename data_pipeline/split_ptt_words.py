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
from data_pipeline.etl_utils import fetch_latest_from_mongodb, insert_into_redis

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
    dev_logger = logging.getLogger("data_pipeline:split_ptt_words:split_ptt_title")
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


def _split_titles(ptt_titles:list) -> list:
    """
    :param ptt_titles: all ptt_titles from MongoDB with latest update date
    """
    ptt_title_cleaned = []
    for title in ptt_titles:
        title_text = title['post_title'].split('] ')
        # title_text_wo_stops = jieba.analyse.extract_tags(title_text,20)
        title_splits = jieba.cut(title_text[-1], cut_all=False) # 精準模式
        ptt_title_cleaned.extend(list(title_splits))
    return ptt_title_cleaned


def split_ptt_title(collection:str="ptt", pipeline="split_ptt_title", redis_key="ptt_title"):
    """
    split ptt titles from mongodb and store it in Redis
    :param max_retries: maximum number of retries
    :param delay: delay between retries in seconds
    """
    projection = {'post_title':1, '_id':0}
    ptt_titles = fetch_latest_from_mongodb(logger=dev_logger, collection=collection, projection=projection)
    
    if ptt_titles:
        ptt_title_cleaned = _split_titles(ptt_titles)
        dev_logger.info(json.dumps({'msg':f'Finish splits ptt_titles, number of splits: {len(ptt_title_cleaned)}'}))
        
        insert_into_redis(logger=dev_logger, pipeline=pipeline, redis_key=redis_key, redis_value=ptt_title_cleaned)
    else:
        dev_logger.error(json.dumps({'msg':'Fail to retrieve ptt titles!'}))


def test_scheduler():
    print('hello from split_ptt_words')


if __name__ == '__main__':
    #scheduler.add_job(test_scheduler, "interval", seconds=5)
    scheduler.add_job(
        split_ptt_title,
        trigger="cron",
        hour="0, 4, 8, 12, 16, 20",
        minute=6,
        timezone=pytz.timezone("Asia/Taipei"),
    )

    scheduler.start()
    dev_logger.info(json.dumps({'msg':'Scheduler started ...'}))


    while True:
        time.sleep(5)
        
    

    
    
    
        

