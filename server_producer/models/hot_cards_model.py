import os
import sys
import json
from datetime import datetime
from dotenv import load_dotenv
from wordcloud import WordCloud


load_dotenv()
sys.path.append('../Credit_All_In_One/')
import my_logger
from my_configuration import _get_pgsql, _get_redis

TC_FONT_PATH = "server_producer/models/NotoSerifTC-Regular.otf"

# datetime
now = datetime.now()
today_date = now.date()
today = now.strftime('%Y-%m-%d')


# create a logger
dev_logger = my_logger.MyLogger('producer')
dev_logger.console_handler()
dev_logger.file_handler(today)


def fetch_all_banks():
    pgsql_db = _get_pgsql()
    cursor = pgsql_db.cursor()
    sql = """
    SELECT DISTINCT bank_name 
    FROM credit_info 
    ORDER BY bank_name;
    """
    cursor.execute(sql)
    data = cursor.fetchall()
    cursor.close()
    pgsql_db.close()
    return data


def fetch_cards_ranking(top_k=5):
    pgsql_db = _get_pgsql()
    cursor = pgsql_db.cursor()
    sql = """
    SELECT bank_name, count(DISTINCT card_link) AS cnt 
    FROM credit_info 
    WHERE lst_update_dt = (SELECT max(lst_update_dt) FROM credit_info)
    GROUP BY bank_name
    ORDER BY count(*) desc
    LIMIT %s;
    """
    cursor.execute(sql, (top_k,))
    data = cursor.fetchall()
    cursor.close()
    pgsql_db.close()
    return data
    

def fetch_total_banks_and_cards():
    pgsql_db = _get_pgsql()
    cursor = pgsql_db.cursor()
    sql = """
    SELECT count(DISTINCT bank_name) AS ttl_banks, count(DISTINCT card_link) AS ttl_cards 
    FROM credit_info 
    WHERE lst_update_dt = (SELECT max(lst_update_dt) FROM credit_info);
    """
    cursor.execute(sql)
    data = cursor.fetchall()
    cursor.close()
    pgsql_db.close()
    return data


def fetch_latest_cards(days=30):
    pgsql_db = _get_pgsql()
    cursor = pgsql_db.cursor()
    sql = """
    WITH fst AS (
        SELECT 
            bank_name, card_name, card_image, card_link, min(lst_update_dt) AS first_date
        FROM credit_info
        group by bank_name, card_name, card_image, card_link
    )
    SELECT first_date, bank_name, card_name, card_image, card_link
    FROM fst 
    WHERE first_date BETWEEN current_date - %s AND current_date
    ORDER BY first_date DESC, bank_name ASC, card_name ASC;
    """
    cursor.execute(sql, (days,))
    data = cursor.fetchall()
    cursor.close()
    pgsql_db.close()
    return data


def fetch_ptt_title_splitted():
    """
    retrieve the splitted ptt_titles from Redis
    """
    redis_conn = _get_redis()
    data = json.loads(redis_conn.get("ptt_title").decode("utf-8"))
    wc = WordCloud(
                font_path=TC_FONT_PATH,
                margin=2,
                background_color="rgba(255, 255, 255, 0)", mode="RGBA",
                max_font_size=100,
                width=700,
                height=500,
            ).generate(" ".join(data))
    return wc.to_image() 


def fetch_ptt_article_scores():
    """
    retrieve the scores of cards from Redis
    """
    redis_conn = _get_redis()
    data = json.loads(redis_conn.get("ptt_article").decode("utf-8"))
    return data


if __name__ == '__main__':
    fetch_ptt_article_scores()
    