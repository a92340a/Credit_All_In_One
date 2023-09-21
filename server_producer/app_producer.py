import os
import json
from datetime import datetime
from dotenv import load_dotenv

from flask import Flask, request, render_template
from flask_socketio import SocketIO
from google.cloud.pubsublite.cloudpubsub import PublisherClient
from google.cloud.pubsublite.types import MessageMetadata
from flask_restful import Resource, Api


load_dotenv()

import my_logger


# datetime
now = datetime.now()
today_date = now.date()
today = now.strftime('%Y-%m-%d')
year = now.strftime('%Y')

# create a logger
dev_logger = my_logger.MyLogger('producer')
dev_logger.console_handler()
dev_logger.file_handler(today)


app = Flask(__name__)
app.secret_key = os.getenv('APP_SECRET_KEY')
api = Api(app)
socketio = SocketIO(app, cors_allowed_origins="*")
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv('KEY')


@socketio.on('message')
def get_and_produce_message(message):
    """
    First response with waiting message and publish message, sid to PubSub Lite
    """
    message_sid = {'message':message, 'sid':request.sid}
    with PublisherClient() as publisher_client:
        api_future = publisher_client.publish(os.getenv('TOPIC'), json.dumps(message_sid).encode("utf-8"))
        # result() blocks. To resolve API futures asynchronously, use add_done_callback().
        message_id = api_future.result()
        calculating = f'Please wait for calculating... {message}'
        socketio.emit('calculating', calculating, to=request.sid)

        message_metadata = MessageMetadata.decode(message_id)
        dev_logger.info(
            f"Published a message with partition {message_metadata.partition.value} and offset {message_metadata.cursor.offset}."
        )


class LanguageModel(Resource):
    def post(self):
        """
        Receive results from consumer server 
        """
        message_output = request.get_json()['message']
        socketio.emit('result', message_output['message'], to=message_output['sid'])
        return {'data': message_output}
    

api.add_resource(LanguageModel, '/lang')


@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    socketio.run(app, host=os.getenv('COMMON_HOST'), port=os.getenv('PRODUCER_PORT'), debug=True, allow_unsafe_werkzeug=True)
