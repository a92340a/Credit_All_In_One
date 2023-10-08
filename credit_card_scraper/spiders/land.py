import re
import time
from datetime import datetime
import scrapy
from bs4 import BeautifulSoup as bs
from credit_card_scraper.items import CreditCardScraperItem


# datetime
now = datetime.now()
today_date = now.date()
today = now.strftime('%Y-%m-%d')


class LandSpider(scrapy.Spider):
    name = "land"
    allowed_domains = ["www.landbank.com.tw"]
    start_urls = ["https://www.landbank.com.tw/Category/Items/%E9%8A%80%E8%A1%8C%E5%8D%A1_",
                  "https://www.landbank.com.tw/Category/Items/%E8%AA%8D%E5%90%8C%E5%8D%A1%E3%80%81%E8%81%AF%E5%90%8D%E5%8D%A1%E2%80%94JCB%E7%B3%BB%E5%88%97"]
    handle_httpstatus_list = [302] 
    custom_settings = {
        'ITEM_PIPELINES': {
            "credit_card_scraper.pipelines.CreditCardScraperPipeline": 300,
        }
    }

    def parse(self, response):
        boxes = response.css("div.contect_contect div.row div.col-md-6")
        for box in boxes:
            source = '土銀'
            bank_name = '土地, 土地銀行, 土銀, 005, land, land bank of taiwan'
            card_image = '/static/images/land_bank' + box.css('div p a img::attr(src)').get()
            card_name = box.css('div p a strong span::text').get().split('■ ')[1]
            if '停止' not in card_name:
                if '土地' not in card_name:
                    card_name = '土地' + card_name
                card_link = box.css('div p a::attr(href)').get()
                create_dt = today
                create_timestamp = int(time.time())
                
                item = CreditCardScraperItem()
                item['source'] = source
                item['bank_name'] = bank_name
                item['card_image'] = card_image
                item['card_name'] = card_name
                item['card_content'] = card_name #
                item['card_link'] = card_link
                item['create_dt'] = create_dt
                item['create_timestamp'] = create_timestamp
                yield item

