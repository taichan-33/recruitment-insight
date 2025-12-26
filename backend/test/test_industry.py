# backend/test/test_industry.py
import pytest


class TestIndustryClassification:
    """業界分類機能のテスト"""

    def test_classify_it_engineer(self):
        """IT・エンジニア系の分類"""
        from crawler import classify_industry

        assert classify_industry("システムエンジニア") == "IT・エンジニア"
        assert classify_industry("プログラマー") == "IT・エンジニア"
        assert classify_industry("Webエンジニア") == "IT・エンジニア"
        assert classify_industry("AIアプリ開発エンジニア") == "IT・エンジニア"
        assert classify_industry("ITサポート") == "IT・エンジニア"

    def test_classify_medical_care(self):
        """医療・介護系の分類"""
        from crawler import classify_industry

        assert classify_industry("看護師") == "医療・介護"
        assert classify_industry("介護福祉士") == "医療・介護"
        assert classify_industry("保育士") == "医療・介護"
        assert classify_industry("医療事務") == "医療・介護"
        assert classify_industry("看護助手") == "医療・介護"

    def test_classify_sales_office(self):
        """営業・事務系の分類"""
        from crawler import classify_industry

        assert classify_industry("営業職") == "営業・事務"
        assert classify_industry("一般事務") == "営業・事務"
        assert classify_industry("営業事務") == "営業・事務"
        assert classify_industry("経理担当") == "営業・事務"
        assert classify_industry("総務・経理") == "営業・事務"

    def test_classify_service_retail(self):
        """サービス・販売系の分類"""
        from crawler import classify_industry

        assert classify_industry("販売スタッフ") == "サービス・販売"
        assert classify_industry("接客・調理") == "サービス・販売"
        assert classify_industry("レジ業務") == "サービス・販売"
        assert classify_industry("飲食店スタッフ") == "サービス・販売"

    def test_classify_manufacturing(self):
        """製造・建設系の分類"""
        from crawler import classify_industry

        assert classify_industry("工場作業員") == "製造・建設"
        assert classify_industry("電気工事士") == "製造・建設"
        assert classify_industry("施工管理") == "製造・建設"
        assert classify_industry("現場作業員") == "製造・建設"

    def test_classify_other(self):
        """その他の分類"""
        from crawler import classify_industry

        assert classify_industry("会計年度任用職員") == "その他"
        assert classify_industry("ドライバー") == "その他"


class TestSearchAPI:
    """検索APIのテスト"""

    def test_search_by_keyword(self):
        """キーワード検索"""
        from database import search_jobs

        # 関数が存在することを確認（結果は空でも可）
        results = search_jobs(keyword="エンジニア")
        assert isinstance(results, list)

    def test_search_by_wage_range(self):
        """給与範囲検索"""
        from database import search_jobs

        results = search_jobs(wage_min=200000, wage_max=300000)
        assert isinstance(results, list)

    def test_search_by_industry(self):
        """業界フィルター"""
        from database import search_jobs

        results = search_jobs(industry="IT・エンジニア")
        assert isinstance(results, list)


class TestAnalysisAPI:
    """分析APIのテスト"""

    def test_get_industry_stats(self):
        """業界別統計"""
        from database import get_industry_stats

        stats = get_industry_stats()
        assert isinstance(stats, list)
        # 各業界の件数と平均給与が含まれる
        for item in stats:
            assert "industry" in item
            assert "count" in item

    def test_get_location_stats(self):
        """地域別統計"""
        from database import get_location_stats

        stats = get_location_stats()
        assert isinstance(stats, list)
