import os
import sys
from datetime import datetime
from dotenv import load_dotenv
import psycopg2
import pymongo

sys.path.append('../Credit_All_In_One/')
import my_logger

load_dotenv()

# datetime
now = datetime.now()
today_date = now.date()
today = now.strftime('%Y-%m-%d')


# create a logger
dev_logger = my_logger.MyLogger('summary')
dev_logger.console_handler()
dev_logger.file_handler(today)


def _get_mongodb():
    """ connect to mongodb database: credit """
    MONGO_CONFIG = f"mongodb://{os.getenv('MONGO_USERNAME')}:{os.getenv('MONGO_PASSWORD')}@{os.getenv('MONGO_HOST')}:{os.getenv('MONGO_PORT')}/credit?authMechanism={os.getenv('MONGO_AUTHMECHANISM')}"
    client = pymongo.MongoClient(MONGO_CONFIG) 
    return client['credit']


def _get_pgsql():
    pg_client = psycopg2.connect(
        database=os.getenv('PGSQL_DB'),
        user=os.getenv('PGSQL_USER'),
        password=os.getenv('PGSQL_PASSWD'),
        host=os.getenv('PGSQL_HOST'),
        port=os.getenv('PGSQL_PORT')
        )
    return pg_client


# 'source':bank, 
# 'url': url,
# 'content':jsonable_encoder(text),
# 'create_date':today,
# 'create_timestamp':int(time.time())

pipeline = [
        {'$group': 
            {
                '_id': ['$source', '$url'],
                'lst_update_dt': {'$max': '$create_date'}
            }
        }
]


BANK_CH_NAME = {
    'crawling_taishin':'台新銀行',
    'crawling_cathay':'國泰世華',
    'crawling_ctbc':'中國信託',
    'crawling_hsbc':'滙豐銀行', 
    'crawling_esun':'玉山銀行', 
    'crawling_fubon':'台北富邦', 
    'crawling_mega':'兆豐銀行', 
    'crawling_sinopac':'永豐銀行', 
    'crawling_huanan':'華南銀行', 
    'crawling_first':'第一銀行', 
    'crawling_land':'土地銀行', 
    'crawling_chartered':'渣打銀行', 
    'crawling_dbs':'星展銀行',
    'crawling_ubot':'聯邦銀行', 
    'crawling_american':'美國運通',
    'crawling_cooperative':'合作金庫', 
    'crawling_yuanta':'元大銀行', 
    'crawling_fareast':'遠東商銀',
    'crawling_taiwanbusiness':'臺灣企銀',
    'crawling_changhua':'彰化銀行',
    'crawling_kaohsiung':'高雄銀行', 
    'crawling_entie':'安泰銀行',
    'crawling_kgi':'凱基銀行',
    'crawling_taiwan':'臺灣銀行',
    'crawling_taichung':'台中銀行',
    'crawling_shanghai':'上海商銀',
    'crawling_sunny':'陽信銀行',
    'crawling_shinkong':'新光銀行',
    'crawling_rakuten':'台灣樂天',
}


if __name__ == '__main__':
    mongo_db = _get_mongodb()
    mongo_collection = mongo_db["official_web"]
    pipeline = [{'$match': {'url','https://www.fubon.com/banking/personal/credit_card/all_card/omiyage/omiyage.htm'}}]
    # cur = mongo_collection.find()
    # for i in cur:
    #     print(i)
    r = list(mongo_collection.aggregate(pipeline))
    print(r)
    # fetch_latest_info = list(mongo_collection.aggregate(pipeline))

    # credit_latest_info = []
    # for i in fetch_latest_info:
    #     bank_name = BANK_CH_NAME[i['_id'][0]]
    #     function_name = i['_id'][0]
    #     url = i['_id'][1]
    #     lst_update_dt = i['lst_update_dt']
    #     credit_latest_info.append(tuple([bank_name, function_name, None, url, lst_update_dt]))
    # dev_logger.info(f'Numbers of latest MongoDB data: {len(credit_latest_info)}')

    # pg_db = _get_pgsql()
    # cursor = pg_db.cursor()
    # # cursor.execute('SELECT * from credit_info;')
    # # result = cursor.fetchall()
    # try:
    #     cursor.executemany('INSERT INTO credit_info VALUES (%s, %s, %s, %s, %s);', credit_latest_info)
    #     pg_db.commit()
    #     dev_logger.info('Successfully insert into PostgreSQL')
    # except Exception as e:
    #     dev_logger.warning(e)
    # else:
    #     cursor.close()
