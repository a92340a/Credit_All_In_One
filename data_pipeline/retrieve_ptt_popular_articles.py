import sys
import json
import time
import pytz
from datetime import datetime
from dotenv import load_dotenv
import pymongo

load_dotenv()
sys.path.append('../Credit_All_In_One/')
import my_logger
from my_configuration import _get_mongodb, _get_redis

# datetime
taiwanTz = pytz.timezone("Asia/Taipei") 
now = datetime.now(taiwanTz)
today_date = now.date()
today = now.strftime('%Y-%m-%d')


# create a logger
dev_logger = my_logger.MyLogger('data_pipeline:ptt_words_split')
dev_logger.console_handler()
dev_logger.file_handler(today)


mongo_db = _get_mongodb()
mongo_collection = mongo_db["ptt"]
redis_conn = _get_redis()


def retrieve_popular_articles(push_num = 50, max_retries: int = 5, delay: int = 2):
    max_create_dt = mongo_collection.find_one(sort=[('create_dt', pymongo.DESCENDING)])['create_dt']

    projection = {'post_title': 1, 'post_author':1 , 'post_dt':1, 'post_link':1, 'article': 1, '_id': 0}
    cursor = mongo_collection.find({'push': push_num, 'create_dt':max_create_dt}, projection).sort('post_dt', pymongo.DESCENDING)
    popular_articles = list(cursor)

    if popular_articles:
        dev_logger.info(f'Finish retrieving ptt popular articles on {max_create_dt} updated documents.')
        for trying in range(1, max_retries + 1):
            try:
                redis_conn.set("ptt_popular_articles", json.dumps(popular_articles))
                dev_logger.info('Finish inserting ptt_popular_articles into Redis')
                break
            except Exception as e:
                dev_logger.warning(
                    f"Failed to set value of ptt_popular_articles in Redis: {e}"
                    f"Attempt {trying + 1} of {max_retries}. Retrying in {delay} seconds."
                )
                if trying == max_retries:
                    dev_logger.warning(f"Failed to set value of ptt_popular_articles in {max_retries} attempts.")
                time.sleep(delay)
    else:
        dev_logger.warning('Fail to retrieve ptt popular articles!')




if __name__ == '__main__':
    retrieve_popular_articles()