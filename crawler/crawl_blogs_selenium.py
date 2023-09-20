import os
import sys
import json
import re
import time
from datetime import datetime
from dotenv import load_dotenv
import random

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup as bs
import requests
from google.cloud import bigquery

# import user_agent_list

sys.path.append('../Credit_All_In_One/')
import my_logger
import crawler

load_dotenv()

# datetime
now = datetime.now()
today_date = now.date()
today = now.strftime('%Y-%m-%d')
year = now.strftime('%Y')

# create a logger
dev_logger = my_logger.MyLogger('crawl')
dev_logger.console_handler()
dev_logger.file_handler(today)

# connect to bigquery
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv('BQ_API')
bq_client = bigquery.Client()
dataset = bq_client.dataset('crawling')
table_name = 'blogs'



def getting_cookie_and_us():
    """
    Setting the selenium crawler for clicks on credit card related topics 
    """
    running_ua = random.choice(crawler.USER_AGENT)
    service = Service(executable_path=os.getenv('SERVICE_PATH'))
    opts = Options()
    # opts.add_argument('--headless') # no show the chrome window
    # opts.add_argument('--disable-notifications') # no show the notification message
    opts.add_experimental_option("detach", True) # don't close browser automatically
    opts.add_argument('--incognito') # fresh browser session without any stored cookies or cache or plugin
    opts.add_argument(f'user-agent = {running_ua}') # change user agent for each request

    chrome = webdriver.Chrome(service=service, options=opts)
    chrome.maximize_window() # for capturing full window's item
    chrome.implicitly_wait(30)

    url = "https://www.callingtaiwan.com.tw/?s=%E4%BF%A1%E7%94%A8%E5%8D%A1%E6%8E%A8%E8%96%A6" 
    chrome.get(url)
    selenium_cookies = chrome.get_cookies()
    selenium_user_agent = chrome.execute_script("return navigator.userAgent;")
    return selenium_cookies, selenium_user_agent


def crawling_list(session, selenium_cookies, selenium_user_agent):
    # blogs: callingtaiwan, keywords search for 信用卡推薦
    url = 'https://www.callingtaiwan.com.tw/?s=%E4%BF%A1%E7%94%A8%E5%8D%A1%E6%8E%A8%E8%96%A6' 
    cookies = {'my-cookies':f'{selenium_cookies}'}
    headers = {'user-agent':f'{selenium_user_agent}'}
    
    resp = session.get(url, cookies=cookies, headers=headers)
    soup = bs(resp.text, 'lxml')
    pagetitle = [element.text for element in soup.select('h5')]
    pagepath = [element['href'] for element in soup.select('h5 > a')]

    target = [] 
    for i in crawler.TOPICS:
        for index, title in enumerate(pagetitle):
            if crawler.KEYWORD in title and i in title and (year in title or str(int(year)+1) in title):
                target.append({'topic':i, 'pagetitle':pagetitle[index], 'pagepath':pagepath[index]})
    return target
    

def crawling_detail(session, target, selenium_cookies, selenium_user_agent):
    cookies = {'my-cookies':f'{selenium_cookies}'}
    headers = {'user-agent':f'{selenium_user_agent}'}

    dev_logger.info(target['pagetitle'])
    resp = session.get(target['pagepath'], cookies=cookies, headers=headers)
    soup = bs(resp.text, 'lxml')
    data = soup.select('table')

    upload_data = {'source_type':'blogs', 
                   'source_detail':'callingtaiwan', 
                   'page_title':target['pagetitle'],
                   'page_path':target['pagepath'],
                   'topic':target['topic']
                #    'content':123,
                #    'create_date':today,
                #    'create_timestamp':int(time.time())
                   }
    upload_data_json = json.dumps(upload_data)
    print(upload_data_json)
    
    # errors = bq_client.insert_rows_json(f'{dataset}.{table_name}', upload_data_json)  
    # if errors == []:
    #     dev_logger.info("Added data")
    # else:
    #     dev_logger.warning("Something went wrong: {}".format(errors))




if __name__ == '__main__':
    try_cookies, try_user_agent = getting_cookie_and_us()
    session = requests.Session()
    
    try:
        target_info = crawling_list(session, try_cookies, try_user_agent)
        dev_logger.info(f'there are {len(target_info)} in the searching scope')
    except Exception as e:
        dev_logger.warning(e)
    
    time.sleep(random.randint(3,6))

    for item in target_info:
        crawling_detail(session, item, try_cookies, try_user_agent)
        time.sleep(random.randint(3,6))
        

    #     dev_logger.info(f"... \n response status: {resp.status_code}...")


    # for msg in consumer:
    #     data = json.loads(msg[6])
    #     upload_data = data['payload']['after']
    #     # upload_data['price'] = ctx.create_decimal(int.from_bytes(base64.b64decode(upload_data['price']), byteorder='big')) / 10 ** 2  
    #     upload_data.update({"operation":data['payload']['op']})
    #     upload_data.update({"create_timestamp":data['payload']['source']['ts_ms']})
    #     print(upload_data)
        
    #     errors = bq_client.insert_rows_json(f'{dataset}.{table_name}', [upload_data])  
    #     if errors == []:
    #         print("Added data")
    #     else:
    #         print("Something went wrong: {}".format(errors))