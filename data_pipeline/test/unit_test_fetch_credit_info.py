import sys
import pytest

sys.path.append('../Credit_All_In_One/')
from data_pipeline.fetch_credit_info import fetch_from_mongodb, insert_into_pgsql_card_dict
import my_logger

# create a logger
dev_logger = my_logger.MyLogger('test')
dev_logger.console_handler()


def test_fetch_maxdt_from_mongodb():
    credit_latest_info, card_distinct_info = fetch_from_mongodb(collection="offcial_website_test")
    assert credit_latest_info == [('聯邦', '聯邦, 聯邦銀行, 803, ubot', '聯邦銀行吉鶴卡', 'https://images.contentstack.io/v3/assets/blt4ca32b8be67c85f8/blt2ed67dd808fb1e78/62de00ba5c954177895aa31f/ubotcc.png?width=256&disable=upscale&fit=bounds&auto=webp', 'https://card.ubot.com.tw/eCard/dspPageContent.aspx?strID=2008060014', '2023-10-10')]
    assert card_distinct_info == [('聯邦', '聯邦銀行吉鶴卡', '2023-10-10')]

