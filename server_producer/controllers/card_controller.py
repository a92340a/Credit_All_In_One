import sys
import json
from flask import request, jsonify, make_response
from flask_restful import Resource, Api
from server_producer import app, socketio


sys.path.append('../Credit_All_In_One/')
from my_configuration import _get_pgsql

api = Api(app)


class Card(Resource):
    def post(self):
        """
        Receive the target card and retrieve card information from PostgreSQL
        """
        request_data = request.get_data()
        card = json.loads(request_data)

        pgsql_db = _get_pgsql()
        cursor = pgsql_db.cursor()
        sql = """
        SELECT 
            bank_name, card_name, card_image, card_link
        FROM credit_info
        WHERE lst_update_dt = (SELECT MAX(lst_update_dt) FROM credit_info)
        AND card_name = %s
        """
        cursor.execute(sql, (card['searching_card'],))
        data = cursor.fetchall()
        cursor.close()
        pgsql_db.close()
        try:
            if data:
                return make_response(jsonify({'data': data}), 200)
            else:
                return make_response(jsonify({'data': 'no valid card name'}), 404)
        except Exception as err:
            return make_response(jsonify({'msg': err}), 500)
        
    

api.add_resource(Card, '/card')