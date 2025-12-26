# tests/test_crawler.py
from crawler import clean_money

def test_clean_money_normal():
    # 普通の金額表記
    assert clean_money("200,000円") == 200000

def test_clean_money_range():
    # 範囲表記の一部だけ渡された場合など
    assert clean_money("350,000") == 350000

def test_clean_money_dirty():
    # 余計な文字が入っている場合
    assert clean_money("月給: 180,000円") == 180000

def test_clean_money_none():
    # 空の場合
    assert clean_money("") == 0
    assert clean_money(None) == 0

    