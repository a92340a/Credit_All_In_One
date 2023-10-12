import time
import pytz
from datetime import datetime
import scrapy
from bs4 import BeautifulSoup as bs
from credit_card_scraper.items import CreditCardScraperItem

# datetime
taiwanTz = pytz.timezone("Asia/Taipei") 
now = datetime.now(taiwanTz)
today_date = now.date()
today = now.strftime('%Y-%m-%d')


class Chartered1Spider(scrapy.Spider):
    name = "chartered1"
    allowed_domains = ["www.sc.com"]
    start_urls = ["https://www.sc.com/tw/credit-cards/"]
    handle_httpstatus_list = [302]
    custom_settings = {
        'ITEM_PIPELINES': {
            "credit_card_scraper.pipelines.CreditCardScraperPipeline": 300,
        }
    }

    def parse(self, response):
        boxes = response.css('div.sc-product-action-cvp__wrapper')
        for box in boxes:
            source = '渣打'
            bank_name = '渣打, 渣打銀行, 052, Chartered, standard chartered'
            card_image = box.css('div.sc-product-action-cvp__image img::attr(src)').get()
            card_name = box.css('div.sc-product-action-cvp__image img::attr(alt)').get()
            if '渣打' not in card_name:
                card_name = '渣打' + card_name
            content = box.css('div.sc-product-action-cvp__content.sc-product-action-cvp__info ul.sc-product-action-cvp__list ::text').getall()
            content = self.cleaning_content(content)
            content = ','.join(content)
            content1 = box.css('div.sc-product-action-cvp__content.sc-product-action-cvp__info div.sc-product-action-cvp__remarks.sc-rte ::text').getall()
            content1 = self.cleaning_content(content1)
            content1 = ','.join(content1)
            card_content = content + ',' + content1
            card_link = box.css('div.sc-product-action-cvp__content.sc-product-action-cvp__info ul.sc-inline-buttons li:nth-child(2) a::attr(href)').get()
            create_dt = today
            create_timestamp = int(time.time())
            if 'https://' not in card_link:
                card_link = 'https://www.sc.com' + card_link
    
            item = CreditCardScraperItem()
            item['source'] = source
            item['bank_name'] = bank_name
            item['card_image'] = card_image
            item['card_name'] = card_name
            item['card_content'] = card_content
            item['card_link'] = card_link
            item['create_dt'] = create_dt
            item['create_timestamp'] = create_timestamp
            yield item
        

    def cleaning_content(self, content):
        content_cleaned = []
        for i in content:
            if i.replace('\n', '').replace('\t', '').replace('\r', '').replace('\xa0', '').replace('  ','') not in content_cleaned:
                content_cleaned.append(i.replace('\n', '').replace('\t', '').replace('\r', '').replace('\xa0', '').replace('  ',''))
        return content_cleaned


            
    
  