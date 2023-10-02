import os
import sys
import json
import time
from datetime import datetime
from dotenv import load_dotenv
import psycopg2

import requests
from google.pubsub_v1 import PubsubMessage
from google.cloud.pubsublite.cloudpubsub import SubscriberClient
from google.cloud.pubsublite.types import (CloudRegion, CloudZone,
                                           MessageMetadata, SubscriptionPath, FlowControlSettings)
from langchain.memory import MongoDBChatMessageHistory
from lang_openai import load_data


load_dotenv()

sys.path.append('../Credit_All_In_One/')
import my_logger


# datetime
now = datetime.now()
today_date = now.date()
today = now.strftime('%Y-%m-%d')

# create a logger
dev_logger = my_logger.MyLogger('consumer')
dev_logger.console_handler()
dev_logger.file_handler(today)


os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv('KEY')
project_number = os.getenv('PROJECT_NUMBER')
cloud_region = os.getenv('CLOUD_REGION')
zone_id = os.getenv('ZONE_ID')
subscription_id = os.getenv('SUB_ID')
location = CloudZone(CloudRegion(cloud_region), zone_id)


subscription_path = SubscriptionPath(project_number, location, subscription_id)
per_partition_flow_control_settings = FlowControlSettings(
    # 1,000 outstanding messages. Must be > 0.
    messages_outstanding=1000,
    # 10 MiB. Must be greater than the allowed size of the largest message (1 MiB).
    bytes_outstanding=10 * 1024 * 1024,
)

def _get_pgsql():
    pg_client = psycopg2.connect(
        database=os.getenv('PGSQL_DB'),
        user=os.getenv('PGSQL_USER'),
        password=os.getenv('PGSQL_PASSWD'),
        host=os.getenv('PGSQL_HOST'),
        port=os.getenv('PGSQL_PORT'),
        sslmode='verify-ca', 
        sslcert=os.getenv('SSLCERT'), 
        sslkey=os.getenv('SSLKEY'), 
        sslrootcert=os.getenv('SSLROOTCERT')
        )
    return pg_client
    

def _insert_into_pgsql(sid, question, answer):
    """
    sid: user's sockect sid
    question: user's question 
    answer: answer from QA model
    """
    pg_db = _get_pgsql()
    cursor = pg_db.cursor()
    try:
        cursor.execute("""INSERT INTO question_answer(sid,create_dt,create_timestamp,question,answer) 
                       VALUES (%s, %s, %s, %s, %s);""", 
                       (sid, today, int(time.time()), question, answer['answer']))
        pg_db.commit()
        dev_logger.info('Successfully insert into PostgreSQL')
    except Exception as e:
        dev_logger.warning(f'Inserting into pgsql error: {e}')
    else:
        cursor.close()


def language_calculation(message_data):
    """ 
    1. Fetching chatting history for specific sid 
    2. Loading Conversational Retrieval Chain with vector ChromaDB
    3. Inserting the question and answer info to PostgreSQL from chatting history
    """
    message_sid = json.loads(message_data)
    query = message_sid['message']
    sid = message_sid['sid']

    # fetch chatting history
    connection_string = f"mongodb://{os.getenv('MONGO_USERNAME')}:{os.getenv('MONGO_PASSWORD')}@{os.getenv('MONGO_HOST')}:{os.getenv('MONGO_PORT')}/credit?authMechanism={os.getenv('MONGO_AUTHMECHANISM')}"
    history = MongoDBChatMessageHistory(
        connection_string=connection_string, 
        session_id=sid,
        database_name='credit',
        collection_name='chat_history'    
    )

    # QA chain
    qa_database = load_data(history)
    answer = qa_database({"question": query, "chat_history":history.messages})
    message_sid['message'] = answer['answer']
    dev_logger.info('Finish query on LangChain QAbot: {}'.format(message_sid['message']))
    
    history.add_user_message(query)  
    history.add_ai_message(answer['answer'])  
    
    # Insert QA data into PostgreSQL
    _insert_into_pgsql(sid, query, answer)
    return message_sid


def callback(message: PubsubMessage):
    message_data = message.data.decode("unicode_escape")
    metadata = MessageMetadata.decode(message.message_id)
    dev_logger.info(
        f"Received {message_data} of ordering key {message.ordering_key} with id {metadata}."
    )
    # Acknowledgement to Pub/Sub Lite with successful subscription
    message.ack()

    # Call language_calculation function...
    # Reply to producer server
    processed_message = language_calculation(message_data)
    payload = {'message': processed_message}
    headers = {'content-type': 'application/json'}
    if os.getenv('ENV') == 'development':
        HOST = '127.0.0.1'
    else:
        HOST = '0.0.0.0'
    response = requests.post('http://{}:{}/lang'.format(HOST, os.getenv('PRODUCER_PORT')), 
                                data=json.dumps(payload), headers=headers)

    if response.status_code == 200:
        dev_logger.info('Successfully send to producer server')
    else:
        dev_logger.warning(f'Error sending message. Status code: {response.status_code}')


if __name__ == '__main__':
    with SubscriberClient() as subscriber_client:
        streaming_pull_future = subscriber_client.subscribe(
            subscription_path, 
            callback=callback,
            per_partition_flow_control_settings=per_partition_flow_control_settings
        )
        
        dev_logger.info(f"Listening for messages on {str(subscription_path)}...")

        try:
            streaming_pull_future.result()
        except KeyboardInterrupt:
            streaming_pull_future.cancel()
            assert streaming_pull_future.done()
