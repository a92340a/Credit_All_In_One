import os
import pytz
import sys
import time
from datetime import datetime
from dotenv import load_dotenv
import json
import redis
import jieba
import jieba.analyse
from wordcloud import WordCloud


load_dotenv()
sys.path.append('../Credit_All_In_One/')
import my_logger
from my_configuration import _get_mongodb

# datetime
now = datetime.now()
today_date = now.date()
today = now.strftime('%Y-%m-%d')


# create a logger
dev_logger = my_logger.MyLogger('data_pipeline:ptt_words_split')
dev_logger.console_handler()
dev_logger.file_handler(today)


jieba.set_dictionary('data_pipeline/dict.txt.big') # simpified to tranditional chinese
jieba.load_userdict('data_pipeline/custom_words.txt') # custom words
jieba.analyse.set_stop_words('data_pipeline/stop_words.txt')
mongo_db = _get_mongodb()
mongo_collection = mongo_db["ptt"]


current_timezone = pytz.timezone("Asia/Taipei")
current_time = datetime.now(current_timezone).replace(
    hour=0, minute=0, second=0, microsecond=0
)

redis_pool = redis.ConnectionPool(host=os.getenv("REDIS_HOST"),
                                  port=os.getenv("REDIS_PORT"))
redis_conn = redis.StrictRedis(connection_pool=redis_pool, decode_responses=True)


def split_ptt_title(max_retries: int = 5, delay: int = 2):
    """
    split ptt titles from mongodb and store it in Redis
    :param max_retries: maximum number of retries
    :param delay: delay between retries in seconds
    """
    ptt_titles = list(mongo_collection.find({}, {'post_title':1, '_id':0}))
    ptt_title_cleaned = []
    for title in ptt_titles:
        title_text = title['post_title'].split('] ')
        # title_text_wo_stops = jieba.analyse.extract_tags(title_text,20)
        title_splits = jieba.cut(title_text[-1], cut_all=True)
        ptt_title_cleaned.extend(list(title_splits))
    dev_logger.info(ptt_title_cleaned)
    
    for trying in range(1, max_retries + 1):
        try:
            redis_conn.set("ptt_title", json.dumps(ptt_title_cleaned))
            break
        except Exception as e:
            dev_logger.warning(
                f"Failed to set value of comments counts sum in Redis: {e}"
                f"Attempt {trying + 1} of {max_retries}. Retrying in {delay} seconds."
            )
            if trying == max_retries:
                dev_logger.warning(f"Failed to set value of comments counts sum in {max_retries} attempts")
            time.sleep(delay)


def split_ptt_article():
    pass

    
    


if __name__ == '__main__':
    split_ptt_title()

