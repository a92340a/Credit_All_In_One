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


class HuananSpider(scrapy.Spider):
    name = "huanan"
    allowed_domains = ["card.hncb.com.tw"]
    start_urls = ["https://card.hncb.com.tw/wps/portal/card/area1/cardall/!ut/p/z1/04_Sj9CPykssy0xPLMnMz0vMAfIjo8ziDfxNPT0M_A18LQICTA0cffy8Qg3CPLzcgoz0wyEKcABHA_0oovTjVhCF3_hw_ShUK9zDQCa4BDuF-Bo6GgcGm6ArMAgOMwJaYWli7u1raORuYg5TgNuSgtzQCINMT0UAQW-yYg!!/dz/d5/L2dBISEvZ0FBIS9nQSEh/"]
    handle_httpstatus_list = [302] 
    custom_settings = {
        'ITEM_PIPELINES': {
            "credit_card_scraper.pipelines.CreditCardScraperPipeline": 300,
        }
    }

    def parse(self, response):
        boxes = response.css("div.element-item ")
        for box in boxes:
            source = '華南'
            bank_name = '華南, 華南銀行, 008, huanan, HUA NAN bank'
            card_image = 'https://card.hncb.com.tw' + box.css('div.element-image div div.carousel-inner div:nth-child(1) img::attr(src)').get()
            card_name = box.css('div.element-content h5.element-title a::text').get()
            
            mobile_paymenet = ['Apple', 'Google', 'Samsung', 'Fitbit', 'HCE', 'Wali', 'Garmin', '行動支付', '支付綁定'] 
            mb_flg = 0
            for mb_name in mobile_paymenet:
                if mb_name in card_name: 
                    mb_flg += 1

            if mb_flg == 0:
                if '停發' in card_name or '停止' in card_name:
                    print('停止申辦')
                else:
                    if '華南' not in card_name:
                        card_name = '華南' + card_name
                    content = box.css('div.element-content div.element-feature ::text').getall()
                    content = self.cleaning_content(content)
                    card_content = ','.join(content)
                    if '終止發行' not in card_content:
                        card_link = box.css('div.element-content h5.element-title a::attr(href)').get()
                        if 'https://' not in card_link:
                            card_link = 'https://card.hncb.com.tw/wps/portal/card/area1/cardall/' + card_link
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
        

    def cleaning_content(self, content):
        content_cleaned = []
        for i in content:
            if i.replace('\n', '').replace('\t', '').replace('\r', '').replace('\xa0', '').replace('  ','') not in content_cleaned:
                content_cleaned.append(i.replace('\n', '').replace('\t', '').replace('\r', '').replace('\xa0', '').replace('  ',''))
        return content_cleaned

