import os
import re
import sys
import time
from fastapi.encoders import jsonable_encoder
from datetime import datetime
from dotenv import load_dotenv
import random

from bs4 import BeautifulSoup as bs
import requests
from langchain.document_loaders import WebBaseLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma

load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv('OPEN_KEY')

sys.path.append('../Credit_All_In_One/')
import my_logger
import crawler 
from crawler.utils import list_target_url, crawl_banks,\
    select_mongo_schema, get_chroma_schema, truncate_chroma



persist_directory = './chroma_db'
embedding = OpenAIEmbeddings() # default: "text-davinci-003", try to find replacable embedding function


# datetime
now = datetime.now()
today_date = now.date()
today = now.strftime('%Y-%m-%d')


# create a logger
dev_logger = my_logger.MyLogger('crawl')
dev_logger.console_handler()
dev_logger.file_handler(today)


# ========= target url list crawling ========= 


def crawling_yuanta(url):
    """
    17. crawler on yuanta credit card
    """
    resp = requests.get(url, headers={'User-Agent':random.choice(crawler.USER_AGENT)})
    soup = bs(resp.text, 'lxml')
    pagepath = ['https://www.yuantabank.com.tw'+element['href'] for element in soup.select('.card_items > ul > li > a')]
    return pagepath


def crawling_fareast(url):
    """
    18. crawler on yuanta credit card: type1: 信用卡, type2:聯名認同卡
    """
    # !!! pdf
    # some cards need to go deeper to get info
    resp = requests.get(url, headers={'User-Agent':random.choice(crawler.USER_AGENT)})
    soup = bs(resp.text, 'lxml')
    # skip invalid url
    pattern_full = re.compile(r'^https:\/\/www.feib.com.tw.*')
    pagepath = [element['href'] for element in soup.select('a.btn.-default')]
    pagepath_full = [i for i in pagepath if re.search(pattern_full, i)]
    return pagepath_full


def crawling_changhua(url):
    """
    20. crawler on changhua bank credit card: 個人卡, 聯名卡, 商務卡 
    """
    resp = requests.get(url, headers={'User-Agent':random.choice(crawler.USER_AGENT)})
    soup = bs(resp.text, 'lxml')
    if any(element.text in ('個人卡', '聯名卡', '商務卡') for element in soup.select('li.ul-li-items > a')):
        pagepath = ['https://www.bankchb.com/frontend/'+element['href'] for element in soup.select('li.ul-li-items > ul > li.sub-ul-li-items > a')]
    return pagepath


def crawling_kaohsiung(url):
    """
    21. crawler on kaohsiung bank credit card
    """
    return url


def crawling_kgi(url):
    """
    23. crawler on kgi bank credit card: 信用卡 公司卡
    """
    resp = requests.get(url, headers={'User-Agent':random.choice(crawler.USER_AGENT)})
    soup = bs(resp.text, 'lxml')
    pagepath = ['https://www.kgibank.com.tw'+element['href'] for element in soup.select('a.btn-text.btn--arrowRight')]
    return pagepath


def crawling_taichung(url):
    """
    25. crawler on taishung bank credit card
    """
    resp = requests.get(url, headers={'User-Agent':random.choice(crawler.USER_AGENT)})
    soup = bs(resp.text, 'lxml')
    pagepath = ['https://www.tcbbank.com.tw/CreditCard/'+element['href'] for element in soup.select('.img_btn > .admin-btn > a')]
    return pagepath


def crawling_shanghai(url):
    """
    26. crawler on shanghai bank credit card
    """
    resp = requests.get(url, headers={'User-Agent':random.choice(crawler.USER_AGENT)})
    soup = bs(resp.text, 'lxml')
    pagepath = ['https://www.scsb.com.tw/content/card/'+element['href'] for element in soup.select('a.btn.custom_red_solid_style.d-block')]
    return pagepath


def crawling_sunny(url):
    """
    27. crawler on sunny bank credit card
    """
    resp = requests.get(url, headers={'User-Agent':random.choice(crawler.USER_AGENT)})
    soup = bs(resp.text, 'lxml')
    pagepath = ['https://www.sunnybank.com.tw'+element['href'] for element in soup.select('td > a')]
    return pagepath


def crawling_rakuten(url):
    """
    29. crawler on rakuten bank credit card
    """
    resp = requests.get(url, headers={'User-Agent':random.choice(crawler.USER_AGENT)})
    soup = bs(resp.text, 'xml')
    pagepath = ['https://www.card.rakuten.com.tw'+element['href'] for element in soup.select('a.btnApplyB')]
    pagepath.append('https://www.card.rakuten.com.tw/corp/product/cccard.xhtml')
    return pagepath


BANK = [    
    {'function':crawling_yuanta, 'url':['https://www.yuantabank.com.tw/bank/creditCard/creditCard/list.do']},
    {'function':crawling_fareast, 'url':['https://www.feib.com.tw/introduce/cardInfo?type=1',
                    'https://www.feib.com.tw/introduce/cardInfo?type=2']},
    {'function':crawling_changhua, 'url':['https://www.bankchb.com/frontend/mashup.jsp?funcId=f0f6e5d215']},
    {'function':crawling_kaohsiung, 'url':['https://www.bok.com.tw/credit-card']},
    {'function':crawling_kgi, 'url':['https://www.kgibank.com.tw/zh-tw/personal/credit-card/list']},
    {'function':crawling_taichung, 'url':['https://www.tcbbank.com.tw/CreditCard/J_02.html']},
    {'function':crawling_shanghai, 'url':['https://www.scsb.com.tw/content/card/card03.html']},
    {'function':crawling_sunny, 'url':['https://www.sunnybank.com.tw/net/Page/Smenu/125']},
    {'function':crawling_rakuten, 'url':['https://www.card.rakuten.com.tw/corp/product/']},
]

if __name__ == '__main__':
    pg_list_all = list_target_url(BANK) 
    
    dev_logger.info('======== Start batch bs ========')
    get_chroma_schema()

    crawl_banks(pg_list_all)
    
    get_chroma_schema()
    dev_logger.info('======== End batch bs ========')    
