import os
import sys
import json
import time
import pytz
import logging
import configparser
from datetime import datetime
from dotenv import load_dotenv
import pymongo
from apscheduler.schedulers.background import BackgroundScheduler

import google.cloud.logging
from google.oauth2.service_account import Credentials


config = configparser.ConfigParser()
config.read('config.ini')

load_dotenv()
sys.path.append('../Credit_All_In_One/')
from my_configuration import _get_mongodb
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
    dev_logger = logging.getLogger("data_pipeline:retrieve_ptt_popular_articles:retrieve_popular_articles")
else:
    # create a logger
    dev_logger = my_logger.MyLogger('etl')
    dev_logger.console_handler()
    dev_logger.file_handler(datetime.now(taiwanTz).strftime('%Y-%m-%d'))


mongo_db = _get_mongodb()


def retrieve_popular_articles(collection:str="ptt", pipeline="ptt_popular_articles", push_num:int=50, redis_key:str="ptt_popular_articles"):
    projection = {'post_title': 1, 'post_author':1 , 'push':1, 'post_dt':1, 'post_link':1, 'article': 1, '_id': 0}
    popular_articles = fetch_latest_from_mongodb(logger=dev_logger, pipeline=pipeline, collection=collection, projection=projection, push={'$gte': push_num})

    if popular_articles:
        insert_into_redis(logger=dev_logger, pipeline=pipeline, redis_key=redis_key, redis_value=popular_articles)
    else:
        dev_logger.warning(json.dumps({'msg':'Fail to retrieve ptt popular articles!'}))



if __name__ == '__main__':
    scheduler.add_job(
        retrieve_popular_articles,
        trigger="cron",
        hour="0, 4, 8, 12, 16, 20",
        minute=5,
        timezone=pytz.timezone("Asia/Taipei"),
    )

    scheduler.start()
    dev_logger.info(json.dumps({'msg':'Scheduler started ...'}))


    while True:
        time.sleep(5)
