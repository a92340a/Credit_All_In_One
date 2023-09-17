import os
import sys
import json
from datetime import datetime
from dotenv import load_dotenv

import requests
from google.pubsub_v1 import PubsubMessage
from google.cloud.pubsublite.cloudpubsub import SubscriberClient
from google.cloud.pubsublite.types import (CloudRegion, CloudZone,
                                           MessageMetadata, SubscriptionPath, FlowControlSettings)


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


def language_calculation(message_data):
    # !!!Replacing this with openai API or Language Model!!!
    """ 
    1. Tokenization with openai API
    2. Build a Neo4j query
    3. Tuning prompt to complete a conversation with query result and openai API
    """
    message_output = message_data + ' Finn!'
    print(message_output)
    return message_output


def callback(message: PubsubMessage):
    message_data = message.data.decode("utf-8")
    metadata = MessageMetadata.decode(message.message_id)
    print(
        f"Received {message_data} of ordering key {message.ordering_key} with id {metadata}."
    )
    # Acknowledgement to Pub/Sub Lite with successful subscription
    message.ack()

    # Call language_calculation function...
    # Reply to producer server
    processed_message = language_calculation(message_data)
    payload = {'message': processed_message}
    headers = {'content-type': 'application/json'}
    response = requests.post('http://{}:{}/lang'.format(os.getenv('LOCAL_HOST'),
                                                        os.getenv('PRODUCER_PORT')), 
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
        
        print(f"Listening for messages on {str(subscription_path)}...")

        try:
            streaming_pull_future.result()
        except KeyboardInterrupt:
            streaming_pull_future.cancel()
            assert streaming_pull_future.done()
