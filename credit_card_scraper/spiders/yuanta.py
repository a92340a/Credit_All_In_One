import time
from datetime import datetime
import scrapy
from credit_card_scraper.items import CreditCardScraperItem


# datetime
now = datetime.now()
today_date = now.date()
today = now.strftime('%Y-%m-%d')


class YuantaSpider(scrapy.Spider):
    name = "yuanta"
    allowed_domains = ["www.yuantabank.com.tw"]
    start_urls = ["https://www.yuantabank.com.tw/bank/creditCard/creditCard/list.do"]
    handle_httpstatus_list = [302] 
    custom_settings = {
        'ITEM_PIPELINES': {
            "credit_card_scraper.pipelines.CreditCardScraperPipeline": 300,
        }
    }

    def parse(self, response):
        for i in range(1, 5):
            time.sleep(1)
            url = 'https://www.yuantabank.com.tw/bank/creditCard/creditCard/list.do?creditcard_type=' + str(i)
            yield scrapy.Request(url, callback=self.parse_yuanta)
        
    def parse_yuanta(self, response):
        boxes = response.css("div.card_items ul li")
        for box in boxes:
            source = '元大'
            bank_name = '元大, 元大銀行, 馬家, 806, yuanta'
            card_image = box.css('div.p_box img::attr(src)').get()
            card_name = box.css('div.card_name h5::text').get()
            
            mobile_paymenet = ['Apple', 'Google', 'Samsung', 'Fitbit', 'HCE', 'Wali', 'Garmin'] 
            mb_flg = 0
            for mb_name in mobile_paymenet:
                if mb_name in card_name: 
                    mb_flg += 1
                
            if mb_flg == 0:
                if '停止' not in card_name:
                    if '元大' not in card_name:
                        card_name = '元大' + card_name
                    card_link = box.css('a::attr(href)').get()
                    if 'https://' not in card_link:
                        card_link = 'https://www.yuantabank.com.tw' + card_link
                    create_dt = today
                    create_timestamp = int(time.time())
                    
                    yield scrapy.Request(
                        card_link,
                        callback=self.parse_yuanta_details,
                        meta={
                            'source': source,
                            'bank_name': bank_name,
                            'card_image': card_image,
                            'card_name': card_name,
                            'card_link': card_link,
                            'create_dt': create_dt,
                            'create_timestamp': create_timestamp
                        }
                    )
                else:
                    print('停止申辦')
                    

    def parse_yuanta_details(self, response):
        content = response.css('div.info ul ul.dotBlue li ::text').getall()
        content = self.cleaning_content(content)
        content = ','.join(content)
        
        item = CreditCardScraperItem()
        item['source'] = response.meta.get('source')
        item['bank_name'] = response.meta.get('bank_name')
        item['card_image'] = response.meta.get('card_image')
        item['card_name'] = response.meta.get('card_name')
        item['card_content'] = content
        item['card_link'] = response.meta.get('card_link')
        item['create_dt'] = response.meta.get('create_dt')
        item['create_timestamp'] = response.meta.get('create_timestamp')
        yield item
        

    def cleaning_content(self, content):
        content_cleaned = []
        for i in content:
            if i.replace('\n', '').replace('\t', '').replace('\r', '').replace('\xa0', '').replace('  ','') not in content_cleaned:
                content_cleaned.append(i.replace('\n', '').replace('\t', '').replace('\r', '').replace('\xa0', '').replace('  ',''))
        return content_cleaned
            