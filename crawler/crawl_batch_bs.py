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

sys.path.append('../Credit_All_In_One/')
import my_logger
import crawler 
from crawler.utils import list_target_url, crawl_banks,\
    select_mongo_schema, get_chroma_schema, truncate_chroma


os.environ["OPENAI_API_KEY"] = os.getenv('OPEN_KEY')
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

def crawling_taishin(url):
    """
    1. crawler on taishin credit card: 頂級卡(type2), 銀行卡(type3), 聯名卡(type4)
    """
    # Use 'User-Agent' for anti-crawling
    resp = requests.get(url, headers={'User-Agent':random.choice(crawler.USER_AGENT)})
    soup = bs(resp.text, 'lxml')
    pagepath = ['https://www.taishinbank.com.tw'+element['href'] for element in soup.select('.itemstitle > a')]
    return pagepath


def crawling_cathay(url):
    """
    2. crawler on cathay credit card
    """
    resp = requests.get(url, headers={'User-Agent':random.choice(crawler.USER_AGENT)})
    soup = bs(resp.text, 'lxml')
    pagepath = ['https://www.cathaybk.com.tw'+element['href'] for element in soup.select('.cubre-m-compareCard__link > a')]
    return pagepath


def crawling_hsbc(url):
    """
    4. crawler on hsbc credit card
    """
    resp = requests.get(url, headers={'User-Agent':random.choice(crawler.USER_AGENT)})
    soup = bs(resp.text, 'lxml')
    pagepath = ['https://www.hsbc.com.tw'+element['href'] for element in soup.select('a.A-BTNSO-RW-ALL')]
    return pagepath


def crawling_fubon(url):
    """
    6. crawler on fubon credit card
    """
    resp = requests.get(url, headers={'User-Agent':random.choice(crawler.USER_AGENT)})
    soup = bs(resp.text, 'lxml')
    pagepath = [element['href'] for element in soup.select('.credit-card > a.link.block.mt10.mb10')]
    # skip mobile pay url
    pattern_nomobile = re.compile(r'^(?!.*\/mobile_).*$')
    pagepath_nomobile = [i for i in pagepath if re.search(pattern_nomobile, i)]
    # add domain
    pattern_domain = re.compile(r'https://www.fubon.com.*')
    pagepath_full = [i if re.search(pattern_domain, i) else 'https://www.fubon.com'+i for i in pagepath_nomobile]
    return pagepath_full


def crawling_sinopac(url):
    """
    8. crawler on sinopac credit card
    """
    resp = requests.get(url, headers={'User-Agent':random.choice(crawler.USER_AGENT)})
    soup = bs(resp.text, 'lxml')
    pagepath = ['https://bank.sinopac.com/sinopacBT/personal/credit-card/introduction'+element['href'][1:] for element in soup.select('.Ltype1.cf > li > h2 > a')]
    # skip mobile pay url
    pattern_nomobile = re.compile(r'^(?!.*\/mobile\/).*$')
    pagepath_nomobile = [i for i in pagepath if re.search(pattern_nomobile, i)]
    return pagepath_nomobile


def crawling_huanan(url):
    """
    9. crawler on huanan credit card
    """
    resp = requests.get(url, headers={'User-Agent':random.choice(crawler.USER_AGENT)})
    soup = bs(resp.text, 'lxml')
    pagepath = [element['href'] for element in soup.select('.element-action > a')]
    # rebuild url
    pagepath_full = []
    pattern_card = re.compile(r'.*\/card\/(.*)$')
    for i in pagepath:
        if re.search(pattern_card, i):
            card_name = re.search(pattern_card, i).groups()[0]
            pagepath_full.append('https://card.hncb.com.tw/wps/portal/card/area1/cardall/'+card_name)
    return pagepath_full


def crawling_first(url):
    """
    10. crawler on first credit card
    """
    resp = requests.get(url, headers={'User-Agent':random.choice(crawler.USER_AGENT)})
    soup = bs(resp.text, 'lxml')
    pagepath = [element['href'] for element in soup.select('.card-single-overlay > .overlay-action > a')]
    # skip invaild url
    pattern_valid = re.compile(r'.*/zh_TW/\d+$')
    pagepath_valid = [i for i in pagepath if re.search(pattern_valid, i)]
    return pagepath_valid


def crawling_land(url):
    """
    11. crawler on land credit card
    """
    resp = requests.get(url, headers={'User-Agent':random.choice(crawler.USER_AGENT)})
    soup = bs(resp.text, 'lxml')
    pagepath = [element['href'] for element in soup.select('.text-center > a')]
    return pagepath


def crawling_chartered(url):
    """
    12. crawler on chartered credit card
    """
    resp = requests.get(url, headers={'User-Agent':random.choice(crawler.USER_AGENT)})
    soup = bs(resp.text, 'lxml')
    pagepath = [element['href'] for element in soup.select('.sc-inline-buttons__item > a')]
    # skip invaild url
    pattern_topcardinfo = re.compile(r'^\/tw\/credit-cards.*')
    pagepath_top = ['https://www.sc.com'+i for i in pagepath if re.search(pattern_topcardinfo, i)]
    pattern_topcardspecial = re.compile(r'.*\/tw\/Campaign\/card.*')
    pagepath_top_special = [i for i in pagepath if re.search(pattern_topcardspecial, i)]
    pagepath_others = ['https://www.sc.com'+element['href'] for element in soup.select('.sc-produt-tile__item > a')]
    pagepath_full = pagepath_top + pagepath_others + pagepath_top_special
    return pagepath_full


BANK = [
    {'function':crawling_taishin, 'url':['https://www.taishinbank.com.tw/TSB/personal/credit/intro/overview/index.html?type=type2',
                'https://www.taishinbank.com.tw/TSB/personal/credit/intro/overview/index.html?type=type3',
                'https://www.taishinbank.com.tw/TSB/personal/credit/intro/overview/index.html?type=type4']},
    {'function':crawling_cathay, 'url':['https://www.cathaybk.com.tw/cathaybk/personal/product/credit-card/cards/']},
    {'function':crawling_hsbc, 'url':['https://www.hsbc.com.tw/credit-cards/']},
    {'function':crawling_fubon, 'url':['https://www.fubon.com/banking/personal/credit_card/all_card/all_card.htm']},
    {'function':crawling_sinopac, 'url':['https://bank.sinopac.com/sinopacBT/personal/credit-card/introduction/list.html']},
    {'function':crawling_huanan, 'url':['https://card.hncb.com.tw/wps/portal/card/area1/cardall/']},
    {'function':crawling_first, 'url':['https://card.firstbank.com.tw/sites/card/touch/1565690685468']},
    {'function':crawling_land, 'url':['https://www.landbank.com.tw/Category/Items/%E9%8A%80%E8%A1%8C%E5%8D%A1_',
                'https://www.landbank.com.tw/Category/Items/%E8%AA%8D%E5%90%8C%E5%8D%A1%E3%80%81%E8%81%AF%E5%90%8D%E5%8D%A1%E2%80%94JCB%E7%B3%BB%E5%88%97']},
    {'function':crawling_chartered, 'url':['https://www.sc.com/tw/credit-cards/']},    
]





if __name__ == '__main__':
    pg_list_all = list_target_url(BANK) 
    
    dev_logger.info('======== Start batch bs ========')
    get_chroma_schema()

    crawl_banks(pg_list_all)
    
    get_chroma_schema()
    dev_logger.info('======== End batch bs ========')    
