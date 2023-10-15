import sys
from datetime import datetime
from dotenv import load_dotenv


load_dotenv()
sys.path.append('../Credit_All_In_One/')
from my_configuration import _get_pgsql, _get_redis


# datetime
now = datetime.now()
today_date = now.date()
today = now.strftime('%Y-%m-%d')


def fetch_all_banks():
    pgsql_db = _get_pgsql()
    cursor = pgsql_db.cursor()
    sql = """
    WITH card_order AS (
        SELECT bank_name, card_name, ROW_NUMBER() OVER (ORDER BY bank_name, card_name) AS row_num
        FROM credit_info
        GROUP BY bank_name, card_name
        ORDER BY bank_name, card_name
    )
    SELECT bank_name, min(row_num) AS row_num
    FROM card_order
    GROUP BY bank_name;
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
    SELECT bank_name, count(DISTINCT card_name) AS cnt 
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
    SELECT count(DISTINCT bank_name) AS ttl_banks, count(DISTINCT card_name) AS ttl_cards 
    FROM credit_info 
    WHERE lst_update_dt = (SELECT max(lst_update_dt) FROM credit_info);
    """
    cursor.execute(sql)
    data = cursor.fetchall()
    cursor.close()
    pgsql_db.close()
    return data


def fetch_latest_cards():
    pgsql_db = _get_pgsql()
    cursor = pgsql_db.cursor()
    sql = """
    SELECT 
        lst_update_dt, bank_name, card_name, card_image, card_link
    FROM credit_info
    WHERE lst_update_dt = (SELECT MAX(lst_update_dt) FROM credit_info)
    ORDER BY bank_name, card_name;
    """
    cursor.execute(sql)
    data = cursor.fetchall()
    cursor.close()
    pgsql_db.close()
    return data


