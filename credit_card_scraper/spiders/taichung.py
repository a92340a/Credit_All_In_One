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


class TaichungSpider(scrapy.Spider):
    name = "taichung"
    allowed_domains = ["www.tcbbank.com.tw"]
    start_urls = ["https://www.tcbbank.com.tw/CreditCard/J_02.html"]
    handle_httpstatus_list = [302] 
    custom_settings = {
        'ITEM_PIPELINES': {
            "credit_card_scraper.pipelines.CreditCardScraperPipeline": 300,
        }
    }

    def parse(self, response):
        boxes = response.css("div.col-12.col-md-3.left.no_pad div.img_btn")
        for box in boxes:
            source = '台中銀'
            bank_name = '台中銀, 台中銀行, 053, tcb, taichung, taichung bank'
            card_image = 'https://www.tcbbank.com.tw' + box.css('img.img::attr(src)').get().split('..')[1]
            card_name = box.css('div.admin-btn div.word_block p::text').get()
            if '暫停' not in card_name:
                if '台中' not in card_name:
                    card_name = '台中銀' + card_name
                card_link = box.css('div.admin-btn a::attr(href)').get()
                if 'https://' not in card_link:
                    card_link = 'https://www.tcbbank.com.tw/CreditCard/' + card_link
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
                print('停止申辦')
            
        