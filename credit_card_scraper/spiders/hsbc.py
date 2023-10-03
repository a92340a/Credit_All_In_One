import scrapy
from bs4 import BeautifulSoup as bs

class HsbcSpider(scrapy.Spider):
    name = "hsbc"
    allowed_domains = ["www.hsbc.com.tw"]
    start_urls = ["https://www.hsbc.com.tw/zh-tw/credit-cards/"]
    handle_httpstatus_list = [302] 

    def parse(self, response):
        # urls = response.css("a.A-BTNSO-RW-ALL::attr(href)").get()
        soup = bs(response.text, 'lxml')
        pagepath = ['https://www.hsbc.com.tw'+element['href'] for element in soup.select('a.A-BTNSO-RW-ALL')] 
        print(pagepath)
        
