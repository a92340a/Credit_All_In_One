import time
from datetime import datetime
import scrapy
from bs4 import BeautifulSoup as bs
from credit_card_scraper.items import CreditCardScraperItem


# datetime
now = datetime.now()
today_date = now.date()
today = now.strftime('%Y-%m-%d')


class Chartered2Spider(scrapy.Spider):
    name = "chartered2"
    allowed_domains = ["www.sc.com"]
    start_urls = ["https://www.sc.com/tw/credit-cards/"]
    handle_httpstatus_list = [302]
    custom_settings = {
        'ITEM_PIPELINES': {
            "credit_card_scraper.pipelines.CreditCardScraperPipeline": 300,
        }
    } 

    def parse(self, response):
        boxes = response.css('ul.sc-produt-tile__grid li')
        for box in boxes:
            if '停止受理申辦' not in box.css('a div div p::text').get():
                source = '渣打' 
                bank_name = '渣打, 渣打銀行, Chartered, standard chartered' 
                card_image = box.css('a div div img::attr(src)').get() 
                card_name = box.css('a::attr(title)').get()
                if '渣打' not in card_name:
                    card_name = '渣打' + card_name
                content = box.css('a div div p::text').get()
                card_content = self.cleaning_content(content)
                card_link = box.css('a::attr(href)').get() 
                create_dt = today
                create_timestamp = int(time.time())
                if 'https://' not in card_link:
                    card_link = 'https://www.sc.com' + card_link
                
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
    
    def parse_charter2_details(self, response):
        content1 = response.css('div#sc-lb-module-product-benefits ::text').getall()
        content1 = self.cleaning_content(content1)
        content1 = ','.join(content1)
        
        item = CreditCardScraperItem()
        item['source'] = response.meta.get('source')
        item['bank_name'] = response.meta.get('bank_name')
        item['card_image'] = response.meta.get('card_image')
        item['card_name'] = response.meta.get('card_name')
        item['card_content'] = response.meta.get('card_content')[0]+ ',' + content1
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


            
    
  


