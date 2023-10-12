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


class CathaySpider(scrapy.Spider):
    name = "cathay"
    allowed_domains = ["www.cathaybk.com.tw"]
    start_urls = ["https://www.cathaybk.com.tw/cathaybk/personal/product/credit-card/cards/"]
    handle_httpstatus_list = [302] 
    custom_settings = {
        'ITEM_PIPELINES': {
            "credit_card_scraper.pipelines.CreditCardScraperPipeline": 300,
        }
    }

    def parse(self, response):
        boxes = response.css("div.cubre-m-compareCard.-credit")
        for box in boxes:
            source = '國泰'
            bank_name = '國泰, 國泰銀行, 國泰世華銀行, 大樹, 蔡家, cathay, cathay united bank'
            card_image = 'https://www.cathaybk.com.tw' + box.css('div.cubre-m-compareCard__pic img::attr(src)').get()
            card_name = box.css('div.cubre-m-compareCard__title::text').get()
            if '停發' not in card_name:
                if '國泰' not in card_name:
                    card_name = '國泰' + card_name
                content = box.css('div.cubre-m-feature.-multiple ::text').getall()
                content = self.cleaning_content(content)
                card_content = ','.join(content)
                if '停止申辦' not in card_content:
                    card_link = box.css('div.cubre-m-compareCard__action div.cubre-m-compareCard__link a.cubre-a-iconLink::attr(href)').get()
                    if 'https://' not in card_link:
                        card_link = 'https://www.cathaybk.com.tw' + card_link
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
                    print('停止申辦')
            else:
                    print('停止申辦')
                
        

    def cleaning_content(self, content):
        content_cleaned = []
        for i in content:
            if i.replace('\n', '').replace('\t', '').replace('\r', '').replace('\xa0', '').replace('  ','') not in content_cleaned:
                content_cleaned.append(i.replace('\n', '').replace('\t', '').replace('\r', '').replace('\xa0', '').replace('  ',''))
        return content_cleaned