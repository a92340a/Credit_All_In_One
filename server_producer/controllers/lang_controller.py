from flask import request
from flask_restful import Resource, Api
from server_producer import app, socketio


api = Api(app)


class LanguageModel(Resource):
    def post(self):
        """
        Receive results from consumer server 
        """
        message_output = request.get_json()['message']
        socketio.emit('result', message_output['message'], to=message_output['sid'])
        return {'data': message_output}
    

api.add_resource(LanguageModel, '/lang')