import os
import sys
import time
from datetime import datetime
from dotenv import load_dotenv
import random

from bs4 import BeautifulSoup as bs
import requests
import pymongo


load_dotenv()

sys.path.append('../Credit_All_In_One/')
import my_logger
import crawler


# datetime
now = datetime.now()
today_date = now.date()
today = now.strftime('%Y-%m-%d')
year = now.strftime('%Y')

# create a logger
dev_logger = my_logger.MyLogger('crawl')
dev_logger.console_handler()
dev_logger.file_handler(today)


def _get_mongodb():
    # connect to mongodb database: stylish_data_engineering
    MONGO_CONFIG = f"mongodb://{os.getenv('MONGO_USERNAME')}:{os.getenv('MONGO_PASSWORD')}@{os.getenv('MONGO_HOST')}:{os.getenv('MONGO_PORT')}/credit?authMechanism={os.getenv('MONGO_AUTHMECHANISM')}"
    client = pymongo.MongoClient(MONGO_CONFIG) 
    return client['credit']



def crawling_list(url):
    # blogs: callingtaiwan, keywords search for 信用卡推薦
    resp = requests.get(url)
    soup = bs(resp.text, 'lxml')
    pagetitle = [element.text for element in soup.select('h5')]
    pagepath = [element['href'] for element in soup.select('h5 > a')]

    target = [] 
    for i in crawler.TOPICS:
        for index, title in enumerate(pagetitle):
            if crawler.KEYWORD in title and i in title and (year in title or str(int(year)+1) in title):
                target.append({'topic':i, 'pagetitle':pagetitle[index], 'pagepath':pagepath[index]})
    return target
    

def crawling_detail(target):
    dev_logger.info(target['pagetitle'])
    resp = requests.get(target['pagepath'])
    soup = bs(resp.text, 'lxml')
    data = [element.text.split('\n\n\n') for element in soup.select('table')]

    json_data = []
    for i in data[0][2:-2]:
        i = i.replace('\n(','(')
        tmp = i.split('\n')
        json_data.append({'bank':tmp[0],
                            'card':tmp[1],
                            'reward_rate':tmp[2],
                            'reward_limit':tmp[4]
                        })
    
    upload_data = {'source_type':'blogs', 
                   'source_detail':'callingtaiwan', 
                   'page_title':target['pagetitle'],
                   'page_path':target['pagepath'],
                   'topic':target['topic'],
                   'content':json_data,
                   'create_date':today,
                   'create_timestamp':int(time.time())
                   }
    
    mongo_db = _get_mongodb()
    mongo_collection = mongo_db["blogs"]
    record = mongo_collection.insert_one(upload_data)
    dev_logger.info(record)



if __name__ == '__main__':
    url_list = 'https://www.callingtaiwan.com.tw/?s=%E4%BF%A1%E7%94%A8%E5%8D%A1%E6%8E%A8%E8%96%A6' 

    try:
        target_info = crawling_list(url_list)
        dev_logger.info(f'there are {len(target_info)} in the searching scope')
    except Exception as e:
        dev_logger.warning(e)
    
    time.sleep(random.randint(1,2))

    for item in target_info:
        crawling_detail(item)
        time.sleep(random.randint(1,2))
        

