import os
import pytz
import sys
import time
from datetime import datetime
from dotenv import load_dotenv
import json
import jieba
import jieba.analyse
from collections import Counter


load_dotenv()
sys.path.append('../Credit_All_In_One/')
import my_logger
from my_configuration import _get_mongodb, _get_pgsql, _get_redis

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
redis_conn = _get_redis()
pg_db = _get_pgsql()



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
    dev_logger.info(f'Finsish splits titles, number of splits: {len(ptt_title_cleaned)}')
    
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


def score_ptt_article():
    """
    fetch all banks and cards info and calculate the appearance/push on ptt
    """
    # fetch latest ptt titles, push and articles info from MongoDB, find top 5 key words from each post of title and article
    projection = {'post_title': 1, 'push': 1, 'article': 1, '_id': 0}
    try:
        cursor = mongo_collection.find({}, projection)
        ptt_posts = list(cursor) 
        dev_logger.info('Successfully fetch card names from MongoDB')
    except Exception as e:
        dev_logger.warning(f'Failed to fetch card names from PostgreSQL: {e}')
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

    # fetch card name and card_alias name from PostgreSQL
    cursor = pg_db.cursor()
    try:
        cursor.execute("""SELECT ARRAY(
                                SELECT UPPER(REPLACE(unnest(ARRAY[card_name] || string_to_array(card_alias_name,', ')), ' ', ''))
                                ) AS card_names
                        FROM credit_info
                        ORDER BY card_name, card_alias_name;""")
        card_names = list(cursor)
        dev_logger.info('Successfully fetch card names from PostgreSQL')
    except Exception as e:
        dev_logger.warning(f'Failed to fetch card names from PostgreSQL: {e}')
    else:
        cursor.close()

    # matching a counting results for appearance and push of each cards
    new_counting = Counter()
    for key, value in counting.items():
        for card in card_names:
            if key.replace(' ','').upper() in card[0] or key.replace(' ','').upper()+'卡' in card[0]:
                new_counting[card[0][0]] += value
    return new_counting


if __name__ == '__main__':
    split_ptt_title()
    n = score_ptt_article()
    print(n)

    
    
    
        

