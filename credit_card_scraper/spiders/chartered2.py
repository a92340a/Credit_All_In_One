import scrapy


class Chartered2Spider(scrapy.Spider):
    name = "chartered2"
    allowed_domains = ["www.sc.com"]
    start_urls = ["https://www.sc.com/tw/credit-cards/"]

    def parse(self, response):
        pass
