import time
from datetime import datetime
import scrapy
from credit_card_scraper.items import CreditCardScraperItem


# datetime
now = datetime.now()
today_date = now.date()
today = now.strftime('%Y-%m-%d')


class FareastSpider(scrapy.Spider):
    name = "fareast"
    allowed_domains = ["www.feib.com.tw"]
    start_urls = ["https://www.feib.com.tw/introduce/cardInfo?type=1"]
    handle_httpstatus_list = [302] 
    custom_settings = {
        'ITEM_PIPELINES': {
            "credit_card_scraper.pipelines.CreditCardScraperPipeline": 300,
        }
    }

    def parse(self, response):
        boxes = response.css("div.carousel.slide.-cards div div.carousel-item")
        for box in boxes:
            source = '遠銀'
            bank_name = "遠銀, 遠東, 遠東商銀, 805, fareast, Far Eastern Int'l Bank"
            card_image = 'https://www.feib.com.tw' + box.css('div.image.-center img::attr(src)').get()
            card_name = box.css('h2.-fs-2 ::text').getall()
            card_name = ''.join(card_name)
            if '終止' not in card_name:
                if '行動支付' not in card_name:
                    if '遠銀' not in card_name:
                        card_name = '遠銀' + card_name                
                    card_link = box.css('a::attr(href)').get()
                    if 'https://' not in card_link:
                        card_link = 'https://www.feib.com.tw' + card_link
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
            else:
                print('停止受理')
        

    def cleaning_content(self, content):
        content_cleaned = []
        for i in content:
            if i.replace('\n', '').replace('\t', '').replace('\r', '').replace('\xa0', '').replace('  ','') not in content_cleaned:
                content_cleaned.append(i.replace('\n', '').replace('\t', '').replace('\r', '').replace('\xa0', '').replace('  ',''))
        return content_cleaned

