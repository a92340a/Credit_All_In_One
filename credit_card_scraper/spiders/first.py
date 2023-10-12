import time
import pytz
from datetime import datetime
import scrapy
from credit_card_scraper.items import CreditCardScraperItem


# datetime
taiwanTz = pytz.timezone("Asia/Taipei") 
now = datetime.now(taiwanTz)
today_date = now.date()
today = now.strftime('%Y-%m-%d')


class FirstSpider(scrapy.Spider):
    name = "first"
    allowed_domains = ["card.firstbank.com.tw"]
    start_urls = ["https://card.firstbank.com.tw/sites/card/touch/1565690685468"]
    handle_httpstatus_list = [302] 
    custom_settings = {
        'ITEM_PIPELINES': {
            "credit_card_scraper.pipelines.CreditCardScraperPipeline": 300,
        }
    }

    def parse(self, response):
        boxes = response.css("div.card-single")
        for box in boxes:
            source = '一銀'
            bank_name = '一銀, 第一銀行, 龐德, 007, first bank'
            card_image = '/static/images/first_bank/' + box.css('div.card-single-face div.card-single-img::attr(style)').get().split("'")[1].split('/sites/card/image/')[1].replace('?verifyType=Type1','') + '.jpg'
            card_name = box.css('div.card-single-features strong::text').get()
            
            mobile_paymenet = ['Apple', 'Google', 'Samsung', 'Fitbit', 'HCE', 'Wali', 'Garmin', '行動支付', '支付綁定', '台灣Pay'] 
            mb_flg = 0
            for mb_name in mobile_paymenet:
                if mb_name in card_name: 
                    mb_flg += 1

            if mb_flg == 0:        
                if '停止' not in card_name:
                    if '一銀' not in card_name:
                        card_name = '一銀' + card_name
                    content = box.css('div.card-single-features ul.check-list li::text').getall()
                    card_content = ','.join(content)
                    card_link = box.css('div.card-single-overlay div.overlay-action a::attr(href)').get()
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
        

    def cleaning_content(self, content):
        content_cleaned = []
        for i in content:
            if i.replace('\n', '').replace('\t', '').replace('\r', '').replace('\xa0', '').replace('  ','') not in content_cleaned:
                content_cleaned.append(i.replace('\n', '').replace('\t', '').replace('\r', '').replace('\xa0', '').replace('  ',''))
        return content_cleaned