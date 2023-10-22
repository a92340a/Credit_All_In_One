import os
import sys
import json
import time
import pytz
import logging
from datetime import datetime
from dotenv import load_dotenv
import pymongo
import configparser
from apscheduler.schedulers.background import BackgroundScheduler

import google.cloud.logging
from google.oauth2.service_account import Credentials


load_dotenv()
sys.path.append('../Credit_All_In_One/')
from my_configuration import _get_pgsql
import my_logger
from data_pipeline.etl_utils import fetch_latest_from_mongodb

config = configparser.ConfigParser()
config.read('config.ini')

# datetime
taiwanTz = pytz.timezone("Asia/Taipei") 

# Advanced Python Scheduler
scheduler = BackgroundScheduler()


if config['environment']['ENV'] == 'production':
    # GCP logging
    gcp_key = json.load(open(os.getenv("KEY")))
    credentials = Credentials.from_service_account_info(gcp_key)
    client = google.cloud.logging.Client(credentials=credentials)
    client.setup_logging()

    # create a logger
    dev_logger = logging.getLogger("data_pipeline:fetch_credit_info")
else:
    # create a logger
    dev_logger = my_logger.MyLogger('etl')
    dev_logger.console_handler()
    dev_logger.file_handler(datetime.now(taiwanTz).strftime('%Y-%m-%d'))


def _rebuild_credit_card_data(fetch_latest_info:list):
    credit_latest_info = []
    card_distinct_info = []
    for i in fetch_latest_info:
        bank_name = i['source']
        bank_alias_name = i['bank_name']
        card_name = i['card_name']
        card_image = i['card_image']
        card_link = i['card_link']
        lst_update_dt = i['create_dt']
        credit_latest_info.append(tuple([bank_name, bank_alias_name, card_name, card_image, card_link, lst_update_dt]))
        card_distinct_info.append(tuple([card_name, lst_update_dt]))
    dev_logger.info(json.dumps({'msg':'Update for {}'.format(credit_latest_info[0][5])}))
    dev_logger.info(json.dumps({'msg':f'Numbers of latest data in MongoDB: {len(credit_latest_info)}'}))
    return credit_latest_info, card_distinct_info


def _insert_into_pgsql_credit_info(credit_latest_info:list):
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
        dev_logger.info(json.dumps({'msg':'Successfully insert into PostgreSQL: credit_info'}))
    except Exception as e:
        dev_logger.error(json.dumps({'msg':f'Failed to insert data into credit_info in PostgreSQL: {e}'}))
    else:
        cursor.close()
        pg_db.close()


def _insert_into_pgsql_card_dict(card_distinct_info:list):
    """
    Insert the distinct card info PostgreSQL card dict
    :param credit_latest_info: latest credit info_from MongoDB
    """
    pg_db = _get_pgsql()
    cursor = pg_db.cursor()
    try:
        cursor.executemany("""INSERT INTO card_dict(card_name, lst_mtn_dt) VALUES (%s, %s) \
                           ON CONFLICT (card_name) DO NOTHING;""", 
                           card_distinct_info)
        pg_db.commit()
        
        # verify if there is new card today
        sql = "SELECT * FROM card_dict WHERE lst_mtn_dt = %s;"
        cursor.execute(sql, (datetime.now(taiwanTz).strftime('%Y-%m-%d'),))
        is_new_card = cursor.fetchall()
        if is_new_card:
            dev_logger.info(json.dumps({'msg':f'Successfully update PostgreSQL: card_dict. {is_new_card}'}))
        else:
            dev_logger.info(json.dumps({'msg':'No new card and not update PostgreSQL: card_dict'}))
    except Exception as e:
        dev_logger.error(json.dumps({'msg':f'Failed to insert data into card_dict in PostgreSQL: {e}'}))
    else:
        cursor.close()
        pg_db.close()


def main_credit_info(collection:str="official_website", pipeline:str="fetch_credit_info"):
    projection = {'source': 1, 'bank_name':1 , 'card_name':1, 'card_image':1, 'card_link': 1, 'create_dt':1, '_id': 0}
    fetch_latest_info = fetch_latest_from_mongodb(logger=dev_logger, pipeline=pipeline, collection=collection, projection=projection)
    data_credit_info, data_card_dict = _rebuild_credit_card_data(fetch_latest_info)
    
    _insert_into_pgsql_card_dict(data_card_dict)
    _insert_into_pgsql_credit_info(data_credit_info)



if __name__ == '__main__':
    #scheduler.add_job(main_credit_info, "interval", minutes=5)
    scheduler.add_job(
        main_credit_info,
        trigger="cron",
        hour="0, 4, 8, 12, 16, 20",
        minute=0,
        timezone=pytz.timezone("Asia/Taipei"),
    )

    scheduler.start()
    dev_logger.info(json.dumps({'msg':'Scheduler started ...'}))


    while True:
        time.sleep(5)


   
