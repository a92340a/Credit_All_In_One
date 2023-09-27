import os
import json
from datetime import datetime
from dotenv import load_dotenv

from flask import Flask, request, render_template
from flask_socketio import SocketIO
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


app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('APP_SECRET_KEY')
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv('KEY')
socketio = SocketIO(app, cors_allowed_origins="*") 


@app.route('/')
def index():
    return render_template('index.html')


from server_producer.views import socketio_view
from server_producer.controllers import lang_controller