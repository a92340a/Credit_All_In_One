import os
import re
import sys
import json
import time
from datetime import datetime
from dotenv import load_dotenv
import random

from bs4 import BeautifulSoup as bs
import requests


load_dotenv()

sys.path.append('../Credit_All_In_One/')
import my_logger
import crawler 


# datetime
now = datetime.now()
today_date = now.date()
today = now.strftime('%Y-%m-%d')


# create a logger
dev_logger = my_logger.MyLogger('crawl')
dev_logger.console_handler()
dev_logger.file_handler(today)


def crawling_ctbc(url):
    """
    3. crawler on ctbc credit card
    """
    # !!! javascript Error
    resp = requests.get(url, headers={'User-Agent':random.choice(crawler.USER_AGENT)})
    soup = bs(resp.text, 'lxml') # html.parser
    pagepath = [element['href'] for element in soup.select('body > div.twrbo-l-container > div.frame-wrapper > main > div > div > section > div.CPTL-CRD-QSH-CardSearch1 > div:nth-child(3) > div.twrbo-l-result__data > div > div:nth-child(1) > div > div > div.left > div > a')]
    return pagepath


def crawling_esun(url):
    """
    5. crawler on esun credit card
    """
    # !!! javascript Error
    resp = requests.get(url, headers={'User-Agent':random.choice(crawler.USER_AGENT)})
    soup = bs(resp.text, 'lxml')
    print(soup.select('script'))
    pagepath = ['https://www.esunbank.com/'+element['href'] for element in soup.select('a.l-card.mb-4')]
    return pagepath


def crawling_mega(url):
    """
    7. crawler on mega credit card
    """
    # !!! javascript Error
    resp = requests.get(url, headers={'User-Agent':random.choice(crawler.USER_AGENT)})
    soup = bs(resp.text, 'lxml')
    print(soup)
    pagepath = [element['href'] for element in soup.select('.btnrow > a.btn.outline')]
    return pagepath


def crawling_ubot(url):
    """
    14. crawler on ubot credit card
    """
    # !!! javascript Error
    resp = requests.get(url, headers={'User-Agent':random.choice(crawler.USER_AGENT)})
    soup = bs(resp.text, 'lxml')
    pagepath = [element['href'] for element in soup.select('.text-center > a')]
    return pagepath


def crawling_american(url):
    """
    15. crawler on american express credit card
    """
    # !!! javascript Error
    resp = requests.get(url, headers={'User-Agent':random.choice(crawler.USER_AGENT)})
    soup = bs(resp.text, 'lxml')
    # print(soup)
    pagepath = ['https://www.americanexpress.com/zh-tw/'+element['href'] for element in soup.select('.sc_paddingTop_20.sc_paddingLeft_20.sc_paddingRight_0.sc_verticallyFluid.sc_paddingBottom_30 > a')]
    return pagepath


def crawling_cooperative(url):
    """
    16. crawler on taiwan cooperative bank credit card
    """
    # !!! javascript Error
    resp = requests.get(url, headers={'User-Agent':random.choice(crawler.USER_AGENT)})
    soup = bs(resp.text, 'lxml')
    print(soup)
    pagepath = ['https://www.tcb-bank.com.tw'+element['href'] for element in soup.select('.l-action__item > a')]
    return pagepath


def crawling_taiwanbusiness(url):
    """
    19. crawler on taiwan business bank credit card
    """
    # !!! SSLError(SSLError(1, '[SSL: UNSAFE_LEGACY_RENEGOTIATION_DISABLED] unsafe legacy renegotiation disabled (_ssl.c:1129)'
    resp = requests.get(url, headers={'User-Agent':random.choice(crawler.USER_AGENT)})
    soup = bs(resp.text, 'lxml')
    pagepath = ['https://www.tbb.com.tw/'+element['href'] for element in soup.select('c-creditcard__item > a.o-btn.o-btn--secondary')]
    return pagepath


def crawling_entie(url):
    """
    22. crawler on entie bank credit card
    """
    # !!! js?
    resp = requests.get(url, headers={'User-Agent':random.choice(crawler.USER_AGENT)})
    soup = bs(resp.text, 'lxml')
    print(soup)
    pagepath = ['https://www.entiebank.com.tw'+element['href'] for element in soup.select('.card.vertical > a')]
    return pagepath


def crawling_taiwan(url):
    """
    24. crawler on taiwan bank credit card
    """
    # !!! jquery
    resp = requests.get(url, headers={'User-Agent':random.choice(crawler.USER_AGENT)})
    soup = bs(resp.text, 'lxml')
    print(soup)
    pagepath = ['https://ecard.bot.com.tw'+element['href'] for element in soup.select('.CardsBlock > a')]
    return pagepath


def crawling_shinkong(url):
    """
    28. crawler on shin kong bank credit card
    """
    # !!! js
    resp = requests.get(url, headers={'User-Agent':random.choice(crawler.USER_AGENT)})
    soup = bs(resp.text, 'lxml')
    print(soup)
    pagepath = ['https://www.skbank.com.tw/'+element['href'] for element in soup.select('a.credit-card__button-item.ng-tns-c175-3.ng-star-inserted')]
    return pagepath

BANK = [
    {'function':crawling_ctbc, 'url':['https://www.ctbcbank.com/twrbo/zh_tw/cc_index/cc_product/cc_introduction_index.html']},
    {'function':crawling_esun, 'url':['https://www.esunbank.com/zh-tw/personal/credit-card/intro']},
    {'function':crawling_mega, 'url':['https://www.megabank.com.tw/personal/credit-card/card/overview']},
    {'function':crawling_ubot, 'url':['https://card.ubot.com.tw/eCard/dspPageContent.aspx?strID=2008060014']},
    {'function':crawling_american, 'url':['https://www.americanexpress.com/zh-tw/credit-cards/all-cards/']},
    {'function':crawling_cooperative, 'url':['https://www.tcb-bank.com.tw/personal-banking/credit-card/intro/overview']},
    {'function':crawling_taiwanbusiness, 'url':['https://www.tbb.com.tw/zh-tw/personal/cards/products/overview']},
    {'function':crawling_entie, 'url':['https://www.entiebank.com.tw/entie/1_3_1_2']},
    {'function':crawling_taiwan, 'url':['https://ecard.bot.com.tw/index.html']},
    {'function':crawling_shinkong, 'url':['https://www.skbank.com.tw/CC-Creditcard?page=1&tags=undefined&card_option=undefined&international_organizations=undefined']},
]

if __name__ == '__main__':
    page_list_all = []
    for bk in BANK:
        page_list_bk = []
        for i in range(len(bk['url'])):
            try:
                page = bk['function'](bk['url'][i])
                page_list_bk.extend(list(set(page)))
                page_list_bk = list(set(page_list_bk))
            except Exception as e:
                dev_logger.warning(e)
        print(f'page_list_bk:{page_list_bk}')
        # if page_list_all:
        page_list_all.extend(page_list_bk)
        # else:
        #     page_list_all = page_list_bk
    print(f'page_list_all:{page_list_all}')
    