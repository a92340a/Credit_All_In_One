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


class TaishinSpider(scrapy.Spider):
    name = "taishin"
    allowed_domains = ["www.taishinbank.com.tw"]
    start_urls = ["https://www.taishinbank.com.tw/TSB/personal/credit/intro/overview/index.html"]
    handle_httpstatus_list = [302] 
    custom_settings = {
        'ITEM_PIPELINES': {
            "credit_card_scraper.pipelines.CreditCardScraperPipeline": 300,
        }
    }

    def parse(self, response):
        for i in range(2, 5):
            time.sleep(1)
            url = "https://www.taishinbank.com.tw/TSB/personal/credit/intro/overview/index.html?type=type" + str(i)
            yield scrapy.Request(url, cookies={'over18': '1'}, callback=self.parse_taishin)


    def parse_taishin(self, response):
        boxes = response.css("div.ts-comp-29 ")
        for box in boxes:
            source = '台新'
            bank_name = '台新, 台新銀行, taishin, taishin international bank'
            card_image = 'https://www.taishinbank.com.tw' + box.css('div.left div.pic a img::attr(src)').get()
            card_name = box.css('div.right div.itemscont div.itemstitle a p::text').get()
            if '台新' not in card_name:
                card_name = '台新' + card_name
            content = box.css('li.ul-li-items div.desc ::text').getall()
            content = self.cleaning_content(content)
            card_content = ','.join(content)
            if '停止受理' not in card_content:
                card_link = box.css('div.left div.pic a::attr(href)').get()
                if 'https://' not in card_link:
                    card_link = 'https://www.taishinbank.com.tw' + card_link
                create_dt = today
                create_timestamp = int(time.time())
                
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
            else:
                print('停止受理')
        

    def cleaning_content(self, content):
        content_cleaned = []
        for i in content:
            if i.replace('\n', '').replace('\t', '').replace('\r', '').replace('\xa0', '').replace('  ','') not in content_cleaned:
                content_cleaned.append(i.replace('\n', '').replace('\t', '').replace('\r', '').replace('\xa0', '').replace('  ',''))
        return content_cleaned

                
            

