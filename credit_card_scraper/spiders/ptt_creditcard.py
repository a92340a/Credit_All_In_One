import re
import time
from datetime import datetime
import scrapy
from bs4 import BeautifulSoup as bs
from credit_card_scraper.items import PttScraperItem


# datetime
now = datetime.now()
today_date = now.date()
today = now.strftime('%Y-%m-%d')


class PttCreditcardSpider(scrapy.Spider):
    name = "ptt_creditcard"
    allowed_domains = ["www.ptt.cc"]
    start_urls = ["https://www.ptt.cc/bbs/creditcard/index.html"]
    custom_settings = {
        'ITEM_PIPELINES': {
            "credit_card_scraper.pipelines.PttScraperPipeline": 300,
        }
    }

    def parse(self, response):
        # find the latest page
        last_page = response.css('div.btn-group.btn-group-paging a:nth-child(2)::attr(href)').get()
        last_page_number = int(re.search(r'index([0-9]+)\.html', last_page).group(1)) + 1
        
        # crawling 50 pages
        for i in range(50):
            time.sleep(1)
            url = "https://www.ptt.cc/bbs/creditcard/index" + str(last_page_number - i) + ".html"
            yield scrapy.Request(url, cookies={'over18': '1'}, callback=self.parse_article)


    def parse_article(self, response):
        item = PttScraperItem()
        target = response.css("div.r-ent")
    
        for tag in target:
            try:
                item['post_title'] = tag.css("div.title a::text")[0].extract()
                item['post_author'] = tag.css('div.author::text')[0].extract()
                item['post_dt'] = tag.css('div.date::text')[0].extract()
                item['push'] = tag.css('span::text')[0].extract()
                item['post_link'] = 'https://www.ptt.cc' + tag.css('div.title a::attr(href)')[0].extract()
                item['create_dt'] = today
                item['create_timestamp'] =int(time.time())
                yield item
    
            except IndexError:
                pass
            continue