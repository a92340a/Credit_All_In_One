# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from credit_card_scraper.database import DatabaseMongo
from credit_card_scraper.items import CreditCardScraperItem

class CreditCardScraperPipeline:
    def __init__(self):
        self.db = DatabaseMongo()
        
    def process_item(self, item, spider):
        data = dict(CreditCardScraperItem(item))
        self.db.insert_data(data)
        return item
