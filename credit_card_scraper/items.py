# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class CreditCardScraperItem(scrapy.Item):
    source = scrapy.Field()
    bank_name = scrapy.Field()
    card_image = scrapy.Field()
    card_name = scrapy.Field()
    card_content = scrapy.Field()
    card_link = scrapy.Field()
    create_dt = scrapy.Field()
    create_timestamp = scrapy.Field()  


class PttScraperItem(scrapy.Item):
    post_title = scrapy.Field()
    post_author = scrapy.Field()
    post_dt = scrapy.Field()
    push = scrapy.Field()
    post_link = scrapy.Field()
    create_dt = scrapy.Field()
    create_timestamp = scrapy.Field() 