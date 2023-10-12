import time
import pytz
import random
from datetime import datetime
import scrapy
from credit_card_scraper.items import CreditCardScraperItem

# datetime
taiwanTz = pytz.timezone("Asia/Taipei") 
now = datetime.now(taiwanTz)
today_date = now.date()
today = now.strftime('%Y-%m-%d')

class CooperativeSpider(scrapy.Spider):
    name = "cooperative"
    allowed_domains = ["www.money101.com.tw"]
    start_urls = ["https://www.money101.com.tw/%E4%BF%A1%E7%94%A8%E5%8D%A1/%E5%85%A8%E9%83%A8"]
    handle_httpstatus_list = [302] 
    custom_settings = {
        'ITEM_PIPELINES': {
            "credit_card_scraper.pipelines.CreditCardScraperPipeline": 300,
        }
    }


    def parse(self, response):
        time.sleep(random.randint(3, 5))
        url = 'https://www.money101.com.tw/%E4%BF%A1%E7%94%A8%E5%8D%A1/%E5%85%A8%E9%83%A8?providers=%E5%90%88%E4%BD%9C%E9%87%91%E5%BA%AB'
        yield scrapy.Request(url, callback=self.parse_corp, dont_filter=True)


    def parse_corp(self,response):
        boxes = response.css('article.block.rounded.bg-white.shadow')
        for box in boxes:
            source = '合庫'
            bank_name = '合庫, 合作金庫銀行, 006, taiwan cooperative bank'
            card_image = box.css('div.flex.flex-col.p-2 div div div div div a img::attr(src)').get()
            if not card_image:
                card_image = box.css('div.flex.flex-col.p-2 div div a img::attr(src)').get()
            card_name = box.css('div.flex.items-center.justify-between a div h2::text').get()
            content = box.css('div.flex.flex-col.p-2 div div div div div.flex-1 ::text').getall()
            card_content = ''.join(content).replace('回饋','回饋,').replace('上限','上限,')
            if not card_content:
                content = box.css('div.flex.flex-col.p-2 div div.flex-1 ::text').getall()
                card_content = ''.join(content).replace('回饋','回饋,').replace('上限','上限,')
            card_link = 'https://www.tcb-bank.com.tw/personal-banking/credit-card/intro/overview'
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
         