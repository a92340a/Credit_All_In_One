import sys
import json
from datetime import datetime
from dotenv import load_dotenv


load_dotenv()
sys.path.append('../Credit_All_In_One/')
import my_logger
from my_configuration import _get_pgsql, _get_redis

# datetime
now = datetime.now()
today_date = now.date()
today = now.strftime('%Y-%m-%d')


# create a logger
dev_logger = my_logger.MyLogger('producer')
dev_logger.console_handler()
dev_logger.file_handler(today)



def fetch_latest_chats():
    pgsql_db = _get_pgsql()
    cursor = pgsql_db.cursor()
    sql = """
    SELECT to_char(create_dt,'yyyy-mm-dd') AS create_dt, 
        (to_timestamp(create_timestamp) AT TIME ZONE 'Asia/Shanghai')::time AS create_timestamp, 
        user_icon, question, answer
    FROM question_answer
    WHERE length(answer) > 150
    ORDER BY create_dt DESC, create_timestamp DESC
    LIMIT 5; 
    """
    cursor.execute(sql)
    data = cursor.fetchall()
    cursor.close()
    pgsql_db.close()
    return data


def fetch_popular_card_names():
    """
    retrieve the scores of cards from Redis and map with card dict to show the exactly card name
    """
    redis_conn = _get_redis()
    redis_data = json.loads(redis_conn.get("ptt_article").decode("utf-8"))

    pgsql_db = _get_pgsql()
    cursor = pgsql_db.cursor()
    sql = "SELECT card_name FROM card_dict"
    cursor.execute(sql)
    pgsql_data = cursor.fetchall()
    pgsql_data_upper = [i[0].replace(' ','').upper() for i in pgsql_data]
    
    total_scores = 0
    for score in redis_data.values():
        total_scores += score
       
    new_redis_data = dict()
    for key, value in redis_data.items():
        for card_upper_name, card_ori_name in zip(pgsql_data_upper, pgsql_data):
            if key == card_upper_name:
                new_redis_data[card_ori_name[0]] = value/total_scores

    cursor.close()
    pgsql_db.close()
    return new_redis_data


if __name__ == '__main__':
    fetch_popular_card_names()