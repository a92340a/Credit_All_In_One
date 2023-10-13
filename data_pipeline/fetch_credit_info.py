import os
import sys
import pytz
import logging
from datetime import datetime
from dotenv import load_dotenv
import pymongo

load_dotenv()
sys.path.append('../Credit_All_In_One/')
import my_logger
from my_configuration import _get_mongodb, _get_pgsql


# datetime
taiwanTz = pytz.timezone("Asia/Taipei") 
now = datetime.now(taiwanTz)
today_date = now.date()
today = now.strftime('%Y-%m-%d')


# create a logger
dev_logger = my_logger.MyLogger('data_pipeline:fetch_credit_info')
dev_logger.console_handler()
dev_logger.file_handler(today)


def fetch_from_mongodb():
    """
    fetch the latest credit info from MongoDB
    """
    mongo_db = _get_mongodb()
    mongo_collection = mongo_db["official_website"]
    max_create_dt = mongo_collection.find_one(sort=[('create_dt', pymongo.DESCENDING)])['create_dt']

    projection = {'source': 1, 'bank_name':1 , 'card_name':1, 'card_image':1, 'card_link': 1, 'create_dt':1, '_id': 0}
    fetch_latest_info = list(mongo_collection.find({'create_dt': max_create_dt}, projection))

    credit_latest_info = []
    for i in fetch_latest_info:
        bank_name = i['source']
        bank_alias_name = i['bank_name']
        card_name = i['card_name']
        card_image = i['card_image']
        card_link = i['card_link']
        lst_update_dt = i['create_dt']
        credit_latest_info.append(tuple([bank_name, bank_alias_name, card_name, card_image, card_link, lst_update_dt]))
    dev_logger.info('Update for {}'.format(credit_latest_info[0][5]))
    dev_logger.info(f'Numbers of latest data in MongoDB: {len(credit_latest_info)}')
    return credit_latest_info


def insert_into_pgsql(credit_latest_info):
    """
    Insert the latest credit info into PostgreSQL
    :param credit_latest_info: latest credit info from MongoDB
    """
    pg_db = _get_pgsql()
    cursor = pg_db.cursor()
    try:
        cursor.executemany("""INSERT INTO credit_info(bank_name, bank_alias_name, card_name, card_image, card_link, lst_update_dt) VALUES (%s, %s, %s, %s, %s, %s) \
                           ON CONFLICT (bank_name, card_name, lst_update_dt) DO UPDATE \
                           SET (bank_alias_name, card_image, card_link) = (EXCLUDED.bank_alias_name, EXCLUDED.card_image, EXCLUDED.card_link);""", 
                           credit_latest_info)
        pg_db.commit()
        dev_logger.info('Successfully insert into PostgreSQL')
    except Exception as e:
        dev_logger.warning(f'Failed to insert data into credit_info in PostgreSQL: {e}')
    else:
        cursor.close()


if __name__ == '__main__':
    data = fetch_from_mongodb()
    insert_into_pgsql(data)


   