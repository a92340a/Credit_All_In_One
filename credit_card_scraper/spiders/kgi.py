import time
from datetime import datetime
import scrapy
from credit_card_scraper.items import CreditCardScraperItem


# datetime
now = datetime.now()
today_date = now.date()
today = now.strftime('%Y-%m-%d')


class KgiSpider(scrapy.Spider):
    name = "kgi"
    allowed_domains = ["www.kgibank.com.tw"]
    start_urls = ["https://www.kgibank.com.tw/zh-tw/personal/credit-card/list"]
    handle_httpstatus_list = [302] 
    custom_settings = {
        'ITEM_PIPELINES': {
            "credit_card_scraper.pipelines.CreditCardScraperPipeline": 300,
        }
    }

    def parse(self, response):
        boxes = response.css("div.tab_content[role='全部卡片'] div div.container div div.bg-white.bg-lg-none")
        for box in boxes:
            source = '凱基'
            bank_name = '凱基, 凱基銀行, 809, kgi, kgi bank'
            card_image = 'https://www.kgibank.com.tw' + box.css('div div picture img::attr(src)').get()
            card_name = box.css('div.d-flex.flex-column.justify-content-lg-between.w-100p div div::text').get()
            if '停發' not in card_name:
                if '凱基' not in card_name:
                    card_name = '凱基' + card_name
                content = box.css('div.d-flex.flex-column.justify-content-lg-between.w-100p div div.color-light-blue.kgibStatic011__item-title::text').getall()
                card_content = ','.join(content)
                card_link = box.css('div.d-flex.flex-column.justify-content-lg-between.w-100p div a.btn-text.btn--arrowRight::attr(href)').get()
                if 'https://' not in card_link:
                    card_link = 'https://www.kgibank.com.tw' + card_link
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
