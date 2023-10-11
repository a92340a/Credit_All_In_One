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


class SinopacSpider(scrapy.Spider):
    name = "sinopac"
    allowed_domains = ["bank.sinopac.com"]
    start_urls = ["https://bank.sinopac.com/sinopacBT/personal/credit-card/introduction/list.html"]
    handle_httpstatus_list = [302] 
    custom_settings = {
        'ITEM_PIPELINES': {
            "credit_card_scraper.pipelines.CreditCardScraperPipeline": 300,
        }
    }

    def parse(self, response):
        boxes = response.css("ul.Ltype1.cf li")
        for box in boxes:
            source = '永豐'
            bank_name = '永豐, 永豐銀行, 807, sinopac, Bank Sinopac'
            card_image = box.css('div.pic a img::attr(src)').get()
            card_image = 'https://bank.sinopac.com' + card_image.split('../../../..')[1]
            card_name = box.css('h2 a::text').get().strip()
            
            mobile_paymenet = ['Apple', 'Google', 'Samsung', 'Fitbit', 'HCE', 'Wali', 'Garmin'] 
            mb_flg = 0
            for mb_name in mobile_paymenet:
                if mb_name in card_name: 
                    mb_flg += 1
            
            if mb_flg == 0:
                if '其他' not in card_name:
                    if '永豐' not in card_name:
                        card_name = '永豐' + card_name
                    card_content = box.css('p ::text').get()
                    card_link = box.css('div.pic a::attr(href)').get().split('.',1)[1]
                    if 'https://' not in card_link:
                        card_link = 'https://bank.sinopac.com/sinopacBT/personal/credit-card/introduction' + card_link
                    create_dt = today
                    create_timestamp = int(time.time())
                    
                    yield scrapy.Request(
                        card_link,
                        callback=self.parse_charter2_details,
                        meta={
                            'source': source,
                            'bank_name': bank_name,
                            'card_image': card_image,
                            'card_name': card_name,
                            'card_content': card_content,
                            'card_link': card_link,
                            'create_dt': create_dt,
                            'create_timestamp': create_timestamp
                        }
                    )
            else:
                print('停止申辦')
    
    def parse_charter2_details(self, response):
        content1 = response.css('div.info h2 + p').get().replace('<p>','').replace('<br>','').replace('</p>','')

        item = CreditCardScraperItem()
        item['source'] = response.meta.get('source')
        item['bank_name'] = response.meta.get('bank_name')
        item['card_image'] = response.meta.get('card_image')
        item['card_name'] = response.meta.get('card_name')
        item['card_content'] = response.meta.get('card_content')+ ',' + content1
        item['card_link'] = response.meta.get('card_link')
        item['create_dt'] = response.meta.get('create_dt')
        item['create_timestamp'] = response.meta.get('create_timestamp')
        yield item
