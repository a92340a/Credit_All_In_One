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


class ShanghaiSpider(scrapy.Spider):
    name = "shanghai"
    allowed_domains = ["www.scsb.com.tw"]
    start_urls = ["https://www.scsb.com.tw/content/card/card03.html"]
    handle_httpstatus_list = [302] 
    custom_settings = {
        'ITEM_PIPELINES': {
            "credit_card_scraper.pipelines.CreditCardScraperPipeline": 300,
        }
    }

    def parse(self, response):
        boxes = response.css("div.row.ctcard-list")
        for box in boxes:
            source = '上海商銀'
            bank_name = '上海, 上海商銀, 上海商業儲蓄銀行, 011, shanghai, shanghai commercial & savings bank ltd'
            card_image = 'https://www.scsb.com.tw/content/card/' + box.css('div.col-lg-auto img::attr(style)').get().split('(')[1].split(')')[0]
            card_name = box.css('div.col-lg h3::text').get()
            if '暫停' not in card_name:
                if '上海商銀' not in card_name:
                    card_name = '上海商銀' + card_name
                content = box.css('div.col-lg div.row.ctcard-info div.col-lg ul.dotLister ::text').getall()
                content = self.cleaning_content(content)
                card_content = ','.join(content)
                card_link = box.css('div.col-lg div.row.ctcard-info div.col-lg-auto div.focusBtn div.item a.btn.custom_red_solid_style.d-block::attr(href)').get()
                if 'https://' not in card_link:
                    card_link = 'https://www.scsb.com.tw/content/card' + card_link
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