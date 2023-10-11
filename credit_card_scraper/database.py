import os
from dotenv import load_dotenv
import pymongo


# def _get_mongodb():
#     """ connect to mongodb database: credit """
#     MONGO_CONFIG = f"mongodb://{os.getenv('MONGO_USERNAME')}:{os.getenv('MONGO_PASSWORD')}@{os.getenv('MONGO_HOST')}:{os.getenv('MONGO_PORT')}/credit?authMechanism={os.getenv('MONGO_AUTHMECHANISM')}"
#     client = pymongo.MongoClient(MONGO_CONFIG) 
#     return client['credit']

load_dotenv()

class DatabaseMongo:
    def __init__(self, collection):
        MONGO_CONFIG = f"mongodb://{os.getenv('MONGO_USERNAME')}:{os.getenv('MONGO_PASSWORD')}@{os.getenv('MONGO_HOST')}:{os.getenv('MONGO_PORT')}/credit?authMechanism={os.getenv('MONGO_AUTHMECHANISM')}"
        try:
            self.client = pymongo.MongoClient(MONGO_CONFIG)['credit']
            self.collection = self.client[collection]
        except Exception as e:
            print("Connection fail:", e)

    def insert_data(self, values=None):
        try:
            self.collection.insert_one(values)
            return self.collection
        except Exception as e:
            print("Error inserting data:", e)
            return None