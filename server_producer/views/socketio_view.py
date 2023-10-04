import os
import sys
import json
from datetime import datetime
from dotenv import load_dotenv

# sys.path.append('../Credit_All_In_One/')
from server_producer import socketio
from flask import request
from google.cloud.pubsublite.cloudpubsub import PublisherClient
from google.cloud.pubsublite.types import MessageMetadata


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


@socketio.on('message')
def get_and_produce_message(message):
    """
    First response with waiting message and publish message, sid to PubSub Lite
    """
    message_sid = {'message': message[0], 'user_icon': message[1], 'sid':request.sid}
    with PublisherClient() as publisher_client:
        api_future = publisher_client.publish(os.getenv('TOPIC'), json.dumps(message_sid).encode("utf-8"))
        # result() blocks. To resolve API futures asynchronously, use add_done_callback().
        message_id = api_future.result()
        calculating = 'Please wait for calculating... {}'.format(message_sid['message'])
        socketio.emit('calculating', calculating, to=request.sid)

        message_metadata = MessageMetadata.decode(message_id)
        dev_logger.info(
            f"Published a message with partition {message_metadata.partition.value} and offset {message_metadata.cursor.offset}."
        )


