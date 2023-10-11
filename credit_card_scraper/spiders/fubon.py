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


class FubonSpider(scrapy.Spider):
    name = "fubon"
    allowed_domains = ["www.fubon.com"]
    start_urls = ["https://www.fubon.com/banking/personal/credit_card/all_card/all_card.htm"]
    handle_httpstatus_list = [302] 
    custom_settings = {
        'ITEM_PIPELINES': {
            "credit_card_scraper.pipelines.CreditCardScraperPipeline": 300,
        }
    }

    def parse(self, response):
        boxes = response.css("li.credit-card")
        for box in boxes:
            source = '富邦'
            bank_name = '富邦, 北富銀, 富邦銀行, 台北富邦銀行, 勇士, 蔡家, 012, fubon'
            verify = box.css('a.btn-blueDark.pv10.w180Max.block.center::text').get()
            if verify:
                if '不開放申請' in verify or '已停止申辦' in verify:
                    print('停止申辦')
                else:
                    card_image = 'https://www.fubon.com' + box.css('div.pic img::attr(src)').get()
                    card_name = box.css('div.title::text').get()
                    if '富邦' not in card_name:
                        card_name = '富邦' + card_name
                    
                    mobile_paymenet = ['Apple', 'Google', 'Samsung', 'Fitbit', 'HCE', 'Wali', 'Garmin'] 
                    mb_flg = 0
                    for mb_name in mobile_paymenet:
                        if mb_name in card_name: 
                            mb_flg += 1
                        
                    if mb_flg == 0:    
                        content = box.css('div.descript ::text').getall()
                        content = self.cleaning_content(content)
                        card_content = ','.join(content)
                        card_link = box.css('a.link.block.mt10.mb10::attr(href)').get()
                        if 'https://' not in card_link:
                            card_link = 'https://www.fubon.com' + card_link
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

