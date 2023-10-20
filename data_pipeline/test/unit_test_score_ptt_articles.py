import sys
import pytest
import collections

sys.path.append('../Credit_All_In_One/')
from data_pipeline.score_ptt_article import _find_top5_keywords, _fetch_card_alias_name, _count_num_of_appearance
import my_logger

# create a logger
dev_logger = my_logger.MyLogger('test')
dev_logger.console_handler()


def test_find_top5_keywords():
    countings = _find_top5_keywords(collection="ptt_test")
    assert type(countings) == collections.Counter
    assert len(countings) == 5


def test_fetch_card_alias_name():
    card_names = _fetch_card_alias_name()
    assert isinstance(card_names, list)
    assert isinstance(card_names[0], tuple)
    assert isinstance(card_names[0][0], list)


def test_count_num_of_appearance():
    mock_counting = {'一銀JCB晶緻卡': 1, '台新狗狗卡': 1, '台新GOGO卡': 1}
    mock_card_names = [(['一銀JCB晶緻卡'],), (['一銀LIVINGGREEN綠活卡', '一銀綠活卡', '綠活卡'],), (['台新@GOGO卡', '台新狗狗卡', '狗狗卡', '台新GOGO卡', 'GOGO卡', '@GOGO', '@GOGO卡', '台新@GOGO卡', '台新@GOGO卡', '台新＠ＧＯＧＯ卡'],)]
    new_counting = _count_num_of_appearance(mock_counting, mock_card_names)
    assert new_counting['台新@GOGO卡'] == 2
    assert new_counting['一銀JCB晶緻卡'] == 1

