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
from apscheduler.schedulers.background import BackgroundScheduler

import google.cloud.logging
from google.oauth2.service_account import Credentials


load_dotenv()
sys.path.append('../Credit_All_In_One/')
from my_configuration import _get_mongodb, _get_pgsql, _get_redis

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
dev_titles_logger = logging.getLogger("data_pipeline:ptt_titles_split")
dev_articles_logger = logging.getLogger("data_pipeline:ptt_articles_split")


jieba.set_dictionary('data_pipeline/text_jieba/dict.txt.big') # simpified to tranditional chinese
jieba.load_userdict('data_pipeline/text_jieba/custom_words.txt') # custom words
jieba.analyse.set_stop_words('data_pipeline/text_jieba/stop_words.txt')
mongo_db = _get_mongodb()
mongo_collection = mongo_db["ptt"]
redis_conn = _get_redis()
pg_db = _get_pgsql()



def split_ptt_title(max_retries: int = 5, delay: int = 2):
    """
    split ptt titles from mongodb and store it in Redis
    :param max_retries: maximum number of retries
    :param delay: delay between retries in seconds
    """
    max_create_dt = mongo_collection.find_one(sort=[('create_dt', pymongo.DESCENDING)])['create_dt']
    projection = {'post_title':1, '_id':0}
    ptt_titles = list(mongo_collection.find({'create_dt':max_create_dt}, projection))

    if ptt_titles:
        dev_titles_logger.info(json.dumps({'msg':f'Finish retrieving ptt titles on {max_create_dt} updated documents.'}))
        ptt_title_cleaned = []
        for title in ptt_titles:
            title_text = title['post_title'].split('] ')
            # title_text_wo_stops = jieba.analyse.extract_tags(title_text,20)
            title_splits = jieba.cut(title_text[-1], cut_all=False) # 精準模式
            ptt_title_cleaned.extend(list(title_splits))
        dev_titles_logger.info(json.dumps({'msg':f'Finish splits ptt_titles, number of splits: {len(ptt_title_cleaned)}'}))
        
        for trying in range(1, max_retries + 1):
            try:
                redis_conn.set("ptt_title", json.dumps(ptt_title_cleaned))
                dev_titles_logger.info(json.dumps({'msg':'Finish inserting ptt_titles into Redis'}))
                break
            except Exception as e:
                dev_titles_logger.warning(
                    json.dumps({'msg':
                        f"Failed to set value of ptt_titles in Redis: {e}"
                        f"Attempt {trying + 1} of {max_retries}. Retrying in {delay} seconds."})
                )
                if trying == max_retries:
                    dev_titles_logger.warning(json.dumps({'msg':f"Failed to set value of ptt_titles in {max_retries} attempts"}))
                time.sleep(delay)
    else:
        dev_titles_logger.warning(json.dumps({'msg':'Fail to retrieve ptt titles!'}))


def score_ptt_article(max_retries: int = 5, delay: int = 2):
    """
    fetch all banks and cards info and calculate the appearance/push on ptt
    """
    # fetch latest ptt titles, push and articles info from MongoDB, find top 5 key words from each post of title and article
    max_create_dt = mongo_collection.find_one(sort=[('create_dt', pymongo.DESCENDING)])['create_dt']
    projection = {'post_title': 1, 'push': 1, 'article': 1, '_id': 0}
    try:
        cursor = mongo_collection.find({'create_dt':max_create_dt}, projection)
        ptt_posts = list(cursor) 
        dev_articles_logger.info(json.dumps({'msg':f'Finish retrieving ptt titles and articles on {max_create_dt} updated documents.'}))
    except Exception as e:
        dev_articles_logger.warning(json.dumps({'msg':f'Failed to retrieve ptt titles and articles from MongoDB: {e}'}))
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

    # fetch distinct card_name and card_alias_name from PostgreSQL
    cursor = pg_db.cursor()
    try:
        cursor.execute("""
                       WITH card AS 
                        (
                            SELECT DISTINCT card_name, card_alias_name
                            FROM credit_info
                        )
                        SELECT ARRAY(
                                SELECT UPPER(REPLACE(unnest(ARRAY[card_name] || string_to_array(card_alias_name,', ')), ' ', ''))
                                ) AS card_names
                        FROM card
                        ORDER BY card_name, card_alias_name;
                       """)
        card_names = list(cursor)
        dev_articles_logger.info(json.dumps({'msg':'Successfully fetch card names from PostgreSQL'}))
    except Exception as e:
        dev_articles_logger.warning(json.dumps({'msg':f'Failed to fetch card names from PostgreSQL: {e}'}))
    else:
        cursor.close()

    # matching a counting results for appearance and push of each cards
    new_counting = Counter()
    for key, value in counting.items():
        for card in card_names:
            if key.replace(' ','').upper() in card[0] or key.replace(' ','').upper()+'卡' in card[0]:
                new_counting[card[0][0]] += value
    
    # insert into redis
    for trying in range(1, max_retries + 1):
        try:
            redis_conn.set("ptt_article", json.dumps(new_counting))
            dev_articles_logger.info(json.dumps({'msg':f'Finish inserting score_ptt_articles into Redis'}))
            break
        except Exception as e:
            dev_articles_logger.warning(
                json.dumps({'msg':
                    f"Failed to set value of score_ptt_articles in Redis: {e}"
                    f"Attempt {trying + 1} of {max_retries}. Retrying in {delay} seconds."})
            )
            if trying == max_retries:
                dev_articles_logger.warning(json.dumps({'msg':f"Failed to set value of score_ptt_articles in {max_retries} attempts"}))
            time.sleep(delay)


scheduler.add_job(
    split_ptt_title,
    trigger="cron",
    hour=8,
    minute=6,
    timezone=pytz.timezone("Asia/Taipei"),
)

scheduler.add_job(
    split_ptt_title,
    trigger="cron",
    hour=8,
    minute=7,
    timezone=pytz.timezone("Asia/Taipei"),
)

scheduler.start()
dev_titles_logger.info(json.dumps({'msg':'Scheduler started ...'}))
dev_articles_logger.info(json.dumps({'msg':'Scheduler started ...'}))


while True:
    pass
    

    
    
    
        

