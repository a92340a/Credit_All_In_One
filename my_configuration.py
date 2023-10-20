import os
from dotenv import load_dotenv
import pymongo
import psycopg2
import redis


load_dotenv()


def _get_mongodb(database="credit"):
    MONGO_CONFIG = f"mongodb://{os.getenv('MONGO_USERNAME')}:{os.getenv('MONGO_PASSWORD')}@{os.getenv('MONGO_HOST')}:{os.getenv('MONGO_PORT')}/{database}?authMechanism={os.getenv('MONGO_AUTHMECHANISM')}"
    client = pymongo.MongoClient(MONGO_CONFIG) 
    return client[database]


def _get_pgsql():
    pg_client = psycopg2.connect(
        database=os.getenv('PGSQL_DB'),
        user=os.getenv('PGSQL_USER'),
        password=os.getenv('PGSQL_PASSWD'),
        host=os.getenv('PGSQL_HOST'),
        port=os.getenv('PGSQL_PORT'),
        sslmode='verify-ca', 
        sslcert=os.getenv('SSLCERT'), 
        sslkey=os.getenv('SSLKEY'), 
        sslrootcert=os.getenv('SSLROOTCERT')
        )
    return pg_client


def _get_redis():
    redis_pool = redis.ConnectionPool(host=os.getenv("REDIS_HOST"),
                                  port=os.getenv("REDIS_PORT"))
    redis_conn = redis.StrictRedis(connection_pool=redis_pool, decode_responses=True)
    return redis_conn 