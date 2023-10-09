import os
import sys
from datetime import datetime
from dotenv import load_dotenv
import psycopg2

load_dotenv()
sys.path.append('../Credit_All_In_One/')
import my_logger
from my_configuration import _get_mongodb, _get_pgsql


# datetime
now = datetime.now()
today_date = now.date()
today = now.strftime('%Y-%m-%d')


# create a logger
dev_logger = my_logger.MyLogger('data_pipeline:fetch_credit_info')
dev_logger.console_handler()
dev_logger.file_handler(today)


pipeline = [
        {'$group': 
            {
                '_id': ['$source', '$bank_name', '$card_name', '$card_image', '$card_link'],
                'lst_update_dt': {'$max': '$create_dt'}
            }
        }
    ]


def fetch_from_mongodb():
    """
    fetch the latest credit info from MongoDB
    """
    mongo_db = _get_mongodb()
    mongo_collection = mongo_db["official_website"]
    fetch_latest_info = list(mongo_collection.aggregate(pipeline))

    credit_latest_info = []
    for i in fetch_latest_info:
        bank_name = i['_id'][0]
        bank_alias_name = i['_id'][1]
        card_name = i['_id'][2]
        card_image = i['_id'][3]
        card_link = i['_id'][4]
        lst_update_dt = i['lst_update_dt']
        credit_latest_info.append(tuple([bank_name, bank_alias_name, card_name, card_image, card_link, lst_update_dt]))
    dev_logger.info('Update for {}'.format(fetch_latest_info[0]['lst_update_dt']))
    dev_logger.info(f'Numbers of latest MongoDB data: {len(credit_latest_info)}')
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
                           ON CONFLICT (bank_name, card_name) DO UPDATE \
                           SET (bank_alias_name, card_image, card_link, lst_update_dt) = (EXCLUDED.bank_alias_name, EXCLUDED.card_image, EXCLUDED.card_link, EXCLUDED.lst_update_dt);""", 
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


   
