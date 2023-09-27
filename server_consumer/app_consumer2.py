import os
import sys
import json
from datetime import datetime
from dotenv import load_dotenv
import psycopg2

import requests
from google.pubsub_v1 import PubsubMessage
from google.cloud.pubsublite.cloudpubsub import SubscriberClient
from google.cloud.pubsublite.types import (CloudRegion, CloudZone,
                                           MessageMetadata, SubscriptionPath, FlowControlSettings)

from lang_openai import load_data


load_dotenv()

sys.path.append('../Credit_All_In_One/')
import my_logger


# datetime
now = datetime.now()
today_date = now.date()
today = now.strftime('%Y-%m-%d')
year = now.strftime('%Y')

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
        port=os.getenv('PGSQL_PORT')
        )
    return pg_client

# def language_calculation(message_data):
#     """ 
#     1. load ChromaDB
#     2. Build a Neo4j query
#     3. Tuning prompt to complete a conversation with query result and openai API
#     """
#     message_sid = json.loads(message_data)
#     qa_database = load_data()
#     query = message_sid['message']
#     answer = qa_database(query)
#     message_sid['message'] = answer['result']
#     dev_logger.info('Finish query on LangChain QAbot: {}'.format(message_sid['message']))
#     return message_sid


def language_calculation(message_data):
    """ 
    1. load ChromaDB
    2. Build a Neo4j query
    3. Tuning prompt to complete a conversation with query result and openai API
    """
    message_sid = json.loads(message_data)
    query = message_sid['message']
    qa_database = load_data()
    answer = qa_database({"question": query})
    print(answer) # {'question': '你好，可以詢問你信用卡相關問題嗎', 'chat_history': [HumanMessage(content='你好，可以詢問你信用卡相關問題嗎', additional_kwargs={}, example=False), AIMessage(content='當然可以！請問你有什麼信用卡相關的問題需要幫忙解答呢？', additional_kwargs={}, example=False)], 'answer': '當然可以！請問你有什麼信用卡相關的問題需要幫忙解答呢？'}
    message_sid['message'] = answer['answer']
    dev_logger.info('Finish query on LangChain QAbot: {}'.format(message_sid['message']))
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

    # Insert QA data into PostgreSQL

# def _insert_into_pgsql(message_data, processed_message):
#     """
#     message_data: user's question and sockect sid
#     processed_message: answer from QA model
#     """
#     question = message_data["message"]
#     answer = processed_message

#     pg_db = _get_pgsql()
#     cursor = pg_db.cursor()
#     try:
#         cursor.execute('INSERT INTO question_answer VALUES (%s, %s, %s, %s, %s);', credit_latest_info)
#         pg_db.commit()
#         dev_logger.info('Successfully insert into PostgreSQL')
#     except Exception as e:
#         dev_logger.warning(e)
#     else:
#         cursor.close()


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
