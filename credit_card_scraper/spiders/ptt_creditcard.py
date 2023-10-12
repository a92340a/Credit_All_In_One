import re
import time
import pytz
from datetime import datetime
import scrapy
from credit_card_scraper.items import PttScraperItem


# datetime
taiwanTz = pytz.timezone("Asia/Taipei") 
now = datetime.now(taiwanTz)
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
        
        # crawling n pages
        for i in range(30):
            time.sleep(1)
            url = "https://www.ptt.cc/bbs/creditcard/index" + str(last_page_number - i) + ".html"
            yield scrapy.Request(url, cookies={'over18': '1'}, callback=self.parse_ptt_titles)


    def parse_ptt_titles(self, response):
        target = response.css("div.r-ent")
        for tag in target:
            post_author = tag.css('div.author::text')[0].extract()
            push = tag.css('span::text').get()
            if push:
                if push == '爆':
                    push = 100
                else:
                    try:
                        push = int(push)
                    except ValueError:
                        push = 0
            else:
                push = 0
            post_link = tag.css('div.title a::attr(href)').get()
            print(post_link)
            if post_link:
                post_link = 'https://www.ptt.cc' + post_link
                create_dt = today
                create_timestamp =int(time.time())
                yield scrapy.Request(
                    post_link,
                    callback=self.parse_ptt_articles,
                    meta={
                        'post_author': post_author,
                        'push': push,
                        'post_link': post_link,
                        'create_dt': create_dt,
                        'create_timestamp': create_timestamp
                    }
                )
            else:
                continue


    def parse_ptt_articles(self, response):    
        main_content = response.css('div#main-content')
        post_title = main_content.css('div:nth-child(3) span.article-meta-value::text').get()
        if post_title and '[公告]' not in post_title:
            post_time = main_content.css('div:nth-child(4) span.article-meta-value::text').get()
            if not post_time:
                print('no post date')
                print(response.meta.get('post_link'))
            else:
                datetime_obj = datetime.strptime(post_time, '%a %b %d %H:%M:%S %Y')
                formatted_post_date = datetime_obj.strftime('%Y-%m-%d')
                full_article = main_content.css('::text').getall()
                article_list = []
                for i in range(8, len(full_article)):
                    if '※ 發信站:' not in full_article[i]:
                        article_list.append(full_article[i].strip())
                    else:
                        break
                article = ''.join(article_list).replace('\n', '').replace('--', '')
                
                item = PttScraperItem()
                item['post_title'] = post_title
                item['post_author'] = response.meta.get('post_author')
                item['post_dt'] = formatted_post_date
                item['push'] = response.meta.get('push')
                item['post_link'] = response.meta.get('post_link')
                item['article'] = article
                item['create_dt'] = response.meta.get('create_dt')
                item['create_timestamp'] = response.meta.get('create_timestamp')
                yield item
     