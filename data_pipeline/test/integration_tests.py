import sys
import json
import pytest
import collections

sys.path.append('../Credit_All_In_One/')
from data_pipeline.score_ptt_article import score_ptt_article
from data_pipeline.split_ptt_words import split_ptt_title
from data_pipeline.credit_docs_transformation import docs_comparing_and_embedding, docs_comparing_and_embedding_manually
import my_logger
from my_configuration import _get_redis

# create a logger
dev_logger = my_logger.MyLogger('test')
dev_logger.console_handler()



def test_score_ptt_article(redis_key="test"):
    redis_conn = _get_redis()
    score_ptt_article(collection="ptt_test", redis_key=redis_key)
    data_bytes = redis_conn.get(redis_key)
    data_string = data_bytes.decode('utf-8')
    data_dict = json.loads(data_string)
    assert data_dict == {'國泰長榮航空聯名卡': 1}


def test_split_ptt_title(redis_key="test"):
    redis_conn = _get_redis()
    split_ptt_title(collection="ptt_test", pipeline="split_ptt_title", redis_key=redis_key)
    data_bytes = redis_conn.get(redis_key)
    data_string = data_bytes.decode('utf-8')
    data_dict = json.loads(data_string)
    assert data_dict == ['國泰長榮極致無限卡']


def test_docs_comparing_and_embedding():
    docs_comparing_and_embedding(collection="official_website_test", card_list=['聯邦銀行吉鶴卡'], today='2023-10-10')


def test_alias_docs_comparing_and_embedding_manually():
    """
    Insert docs with card alias name
    """
    docs_comparing_and_embedding_manually(collection="official_website_test", card_list=[('聯邦銀行吉鶴卡', ['聯邦銀行&吉鶴卡','聯邦銀行123吉鶴卡'])])


def test_ori_docs_comparing_and_embedding_manually():
    """
    Insert docs with original card name
    """
    docs_comparing_and_embedding_manually(collection="official_website_test", card_list=['聯邦銀行吉鶴卡'])


if __name__ == '__main__':
    test_alias_docs_comparing_and_embedding_manually()
