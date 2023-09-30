import os
from datetime import datetime
from dotenv import load_dotenv
import psycopg2

import my_logger 
load_dotenv()


# datetime
now = datetime.now()
today_date = now.date()
today = now.strftime('%Y-%m-%d')


# create a logger
dev_logger = my_logger.MyLogger('producer')
dev_logger.console_handler()
dev_logger.file_handler(today)

    
def _get_pgsql():
    pg_client = psycopg2.connect(
        database=os.getenv('PGSQL_DB'),
        user=os.getenv('PGSQL_USER'),
        password=os.getenv('PGSQL_PASSWD'),
        host=os.getenv('PGSQL_HOST'),
        port=os.getenv('PGSQL_PORT')
        )
    return pg_client


def fetch_cards_ranking(top_k):
    pgsql_db = _get_pgsql()
    cursor = pgsql_db.cursor()
    sql = """
    SELECT bank_name, count(DISTINCT url) AS cnt 
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
    

def fetch_total_cards():
    pgsql_db = _get_pgsql()
    cursor = pgsql_db.cursor()
    sql = """
    SELECT count(DISTINCT url) AS cnt 
    FROM credit_info 
    WHERE lst_update_dt = (SELECT max(lst_update_dt) FROM credit_info);
    """
    cursor.execute(sql)
    data = cursor.fetchall()
    cursor.close()
    pgsql_db.close()
    return data
