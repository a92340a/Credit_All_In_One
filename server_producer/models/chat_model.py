import os
import sys
import json
from datetime import datetime
from dotenv import load_dotenv


load_dotenv()
sys.path.append('../Credit_All_In_One/')
import my_logger
from my_configuration import _get_pgsql

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

# class ChatHistory(db.Model):
#     q_id = db.Column(db.Integer, nullable=False)
#     sid = db.Column(db.String(20))
#     create_dt = db.Column(db.Date)
#     create_timestamp = db.Column(db.Integer)
#     question = db.Column(db.Text())
#     answer = db.Column(db.Text())
#     keyword1 = db.Column(db.String(20))
#     keyword2 = db.Column(db.String(20))
#     keyword3 = db.Column(db.String(20))
#     topic = db.Column(db.Text())


# def get_qa(sid):
#     try:
#         qa_history = User.query.filter_by(sid = sid).all()
#         if qa_history:
#             return qa_history[0].to_json()
#         else:
#             return None
#     except Exception as e:
#         print(e)
#         return None