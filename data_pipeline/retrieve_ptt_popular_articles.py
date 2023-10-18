import os
import sys
import json
import time
import pytz
import logging
from datetime import datetime
from dotenv import load_dotenv
import pymongo
from apscheduler.schedulers.background import BackgroundScheduler

import google.cloud.logging
from google.oauth2.service_account import Credentials

load_dotenv()
sys.path.append('../Credit_All_In_One/')
from my_configuration import _get_mongodb, _get_redis

# datetime
taiwanTz = pytz.timezone("Asia/Taipei") 
now = datetime.now(taiwanTz)
today_date = now.date()
today = now.strftime('%Y-%m-%d')


# Advanced Python Scheduler
scheduler = BackgroundScheduler()

# GCP logging
gcp_key = json.load(open(os.getenv("KEY")))
credentials = Credentials.from_service_account_info(gcp_key)
client = google.cloud.logging.Client(credentials=credentials)
client.setup_logging()

# create a logger
dev_logger = logging.getLogger("data_pipeline:retrieve_ptt_popular_articles:retrieve_popular_articles")


mongo_db = _get_mongodb()
mongo_collection = mongo_db["ptt"]
redis_conn = _get_redis()


def retrieve_popular_articles(push_num = 50, max_retries: int = 5, delay: int = 2):
    max_create_dt = mongo_collection.find_one(sort=[('create_dt', pymongo.DESCENDING)])['create_dt']

    projection = {'post_title': 1, 'post_author':1 , 'push':1, 'post_dt':1, 'post_link':1, 'article': 1, '_id': 0}
    cursor = mongo_collection.find({'push': {'$gte': push_num}, 'create_dt':max_create_dt}, projection).sort('post_dt', pymongo.DESCENDING)
    popular_articles = list(cursor)

    if popular_articles:
        dev_logger.info(json.dumps({'msg':f'Finish retrieving ptt popular articles on {max_create_dt} updated documents.'}))
        for trying in range(1, max_retries + 1):
            try:
                redis_conn.set("ptt_popular_articles", json.dumps(popular_articles))
                dev_logger.info(json.dumps({'msg':'Finish inserting ptt_popular_articles into Redis'}))
                break
            except Exception as e:
                dev_logger.warning(
                    json.dumps({'msg':
                        f"Failed to set value of ptt_popular_articles in Redis: {e}"
                        f"Attempt {trying + 1} of {max_retries}. Retrying in {delay} seconds."})
                )
                if trying == max_retries:
                    dev_logger.warning(json.dumps({'msg':f"Failed to set value of ptt_popular_articles in {max_retries} attempts."}))
                time.sleep(delay)
    else:
        dev_logger.warning(json.dumps({'msg':'Fail to retrieve ptt popular articles!'}))



def test_scheduler():
    print('hello from retrieve_ptt_popular_articles')


#scheduler.add_job(test_scheduler, "interval", seconds=5)
#scheduler.add_job(retrieve_popular_articles, "interval", minutes=5)
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
