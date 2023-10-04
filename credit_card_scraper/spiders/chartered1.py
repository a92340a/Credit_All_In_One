import time
from datetime import datetime
import scrapy
from bs4 import BeautifulSoup as bs
from credit_card_scraper.items import CreditCardScraperItem

# datetime
now = datetime.now()
today_date = now.date()
today = now.strftime('%Y-%m-%d')


class Chartered1Spider(scrapy.Spider):
    name = "chartered1"
    allowed_domains = ["www.sc.com"]
    start_urls = ["https://www.sc.com/tw/credit-cards/"]
    handle_httpstatus_list = [302] 

    def parse(self, response):
        boxes = response.css('div.sc-product-action-cvp__wrapper')
        for box in boxes:
            source = 'crawling_chartered'
            bank_name = '渣打, 渣打銀行, Chartered, chartered'
            card_image = box.css('div.sc-product-action-cvp__image img::attr(src)').get()
            card_name = box.css('div.sc-product-action-cvp__image img::attr(alt)').get()
            content = box.css('div.sc-product-action-cvp__content.sc-product-action-cvp__info ul.sc-product-action-cvp__list ::text').getall()
            content = ''.join(content).replace('\n', '').replace('\t', '').replace('\r', '').replace('\xa0', '')
            content1 = box.css('div.sc-product-action-cvp__content.sc-product-action-cvp__info div.sc-product-action-cvp__remarks.sc-rte ::text').getall()
            content1 = ''.join(content1).replace('\n', '').replace('\t', '').replace('\r', '').replace('\xa0', '')
            card_content = content + '，' + content1
            card_link = box.css('div.sc-product-action-cvp__content.sc-product-action-cvp__info ul.sc-inline-buttons li:nth-child(2) a::attr(href)').get()
            create_dt = today
            create_timestamp = int(time.time())
            if 'https://' not in card_link:
                card_link = 'https://www.sc.com/' + card_link
    
            chartered_item = CreditCardScraperItem()
            chartered_item['source'] = source
            chartered_item['bank_name'] = bank_name
            chartered_item['card_image'] = card_image
            chartered_item['card_name'] = card_name
            chartered_item['card_content'] = card_content
            chartered_item['card_link'] = card_link
            chartered_item['create_dt'] = create_dt
            chartered_item['create_timestamp'] = create_timestamp
            yield chartered_item
            
    
  