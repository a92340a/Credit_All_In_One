import os
from dotenv import load_dotenv

from flask import request
from flask_restful import Resource, Api
from server_producer import app, socketio
import psycopg2

load_dotenv()
api = Api(app)


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
        message_output = request.get_json()['message']
        socketio.emit('result', message_output['message'], to=message_output['sid'])
        return {'data': message_output}
    

api.add_resource(ChatHistory, '/chat')






