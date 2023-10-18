import time
from datetime import datetime
import scrapy
from credit_card_scraper.items import CreditCardScraperItem


# datetime
now = datetime.now()
today_date = now.date()
today = now.strftime('%Y-%m-%d')


class KaohsiungSpider(scrapy.Spider):
    name = "kaohsiung"
    allowed_domains = ["www.bok.com.tw"]
    start_urls = ["https://www.bok.com.tw/credit-card"]
    handle_httpstatus_list = [302] 
    custom_settings = {
        'ITEM_PIPELINES': {
            "credit_card_scraper.pipelines.CreditCardScraperPipeline": 300,
        }
    }

    def parse(self, response):
        boxes = response.css("div.card-intro-box")
        for box in boxes:
            source = '高雄銀'
            bank_name = '高雄銀, 高雄銀行, 016, bok, bank of kaohsiung'
            card_image = 'https://www.bok.com.tw' + box.css('span.img-wrap img::attr(src)').get()
            card_name = box.css('h3.intro-title::text').get()
            if '停發' not in card_name:
                if '高雄' not in card_name:
                    card_name = '高雄銀行' + card_name
                content = box.css('ul.cardbox-list li::text').getall()
                card_content = ','.join(content)
                card_link = box.css('a.cardbutton.next::attr(href)').get()
                if 'https://' not in card_link:
                    card_link = 'https://www.bok.com.tw' + card_link
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
            
        
