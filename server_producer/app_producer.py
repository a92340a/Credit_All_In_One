import os
import sys
from datetime import datetime
from dotenv import load_dotenv

from flask import Flask, request, render_template
from flask_socketio import SocketIO
from google.cloud.pubsublite.cloudpubsub import PublisherClient
from google.cloud.pubsublite.types import MessageMetadata
from flask_restful import Resource, Api


load_dotenv()

sys.path.append('../Credit_All_In_One/')
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
api = Api(app)
socketio = SocketIO(app, cors_allowed_origins="*")
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv('KEY')


@socketio.on('message')
def get_and_produce_message(message):
    with PublisherClient() as publisher_client:
        api_future = publisher_client.publish(os.getenv('TOPIC'), message.encode("utf-8"))
        # result() blocks. To resolve API futures asynchronously, use add_done_callback().
        message_id = api_future.result()
        calculating = f'Please wait for calculating... {message}'
        socketio.emit('calculating', calculating)

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
        socketio.emit('result', message_output)
        return {'data': message_output}
    

api.add_resource(LanguageModel, '/lang')


@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    socketio.run(app, host=os.getenv('COMMON_HOST'), port=os.getenv('PRODUCER_PORT'), debug=True, allow_unsafe_werkzeug=True)
