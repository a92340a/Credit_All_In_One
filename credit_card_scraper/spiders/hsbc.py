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


class HsbcSpider(scrapy.Spider):
    name = "hsbc"
    allowed_domains = ["www.hsbc.com.tw"]
    start_urls = ["https://www.hsbc.com.tw/zh-tw/credit-cards/"]
    handle_httpstatus_list = [302]
    custom_settings = {
        'ITEM_PIPELINES': {
            "credit_card_scraper.pipelines.CreditCardScraperPipeline": 300,
        }
    } 

    def parse(self, response):
        boxes = response.css("div.advancedProductModule")
        for box in boxes:
            source = '滙豐'
            bank_name = '匯豐, 滙豐, 台灣滙豐, 081, hsbc'
            card_image = box.css('div div div.smart-image figure picture img::attr(src)').get()
            card_name = box.css('div div .A-LNKND38L-RW-ALL.text-container.text::text').get().strip()
            if '不接受新卡申請' not in card_name:
                if '滙豐' not in card_name:
                    card_name = '滙豐' + card_name
                content1 = box.css('div div ul.main-list.advancedProductModule ::text').getall()
                content1 = self.cleaning_content(content1)
                content1 = ','.join(content1)
                content2 = box.css('div div div.A-TYP16BL-RW-ALL.text-container.icon-visible ::text').getall()
                content2 = self.cleaning_content(content2)
                content2 = ','.join(content2)
                content3 = box.css('div div div.M-PRDFCTS-RW-DEV div div div.O-SMARTSPCGEN-DEV.M-CONTMAST-RW-RBWM.rich-text div p::text').getall()
                content3 = self.cleaning_content(content3)
                content3 = ','.join(content3)
                card_content = content1 + ',' + content2 + ',' + content3
                if '停止申辦' not in card_content:
                    card_link = box.css('div div.action-buttons.sm-12.md-12.lg-12 div a.A-BTNSO-RW-ALL::attr(href)').get()
                    if 'https://' not in card_link:
                        card_link = 'https://www.hsbc.com.tw' + card_link
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

        
