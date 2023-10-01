import os
import sys
from datetime import datetime
from dotenv import load_dotenv

from flask import request
from flask_restful import Resource, Api
from server_producer import app, socketio
import psycopg2

load_dotenv()
api = Api(app)

sys.path.append('../Credit_All_In_One/')
import my_logger

# datetime
now = datetime.now()
today_date = now.date()
today = now.strftime('%Y-%m-%d')


# create a logger
dev_logger = my_logger.MyLogger('chat_controller')
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


class ChatHistory(Resource):
    def get(self):
        """
        Fetch questions and answers history from PostgreSQL
        """
        pg_db = _get_pgsql()
    cursor = pg_db.cursor()
    # cursor.execute('SELECT * from credit_info;')
    # result = cursor.fetchall()
    try:
        cursor.executemany('INSERT INTO credit_info VALUES (%s, %s, %s, %s, %s);', credit_latest_info)
        pg_db.commit()
        dev_logger.info('Successfully insert into PostgreSQL')
    except Exception as e:
        dev_logger.warning(e)
    else:
        cursor.close()
        return {'data': message_output}
    

api.add_resource(ChatHistory, '/chat')






