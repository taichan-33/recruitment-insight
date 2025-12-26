# backend/test/test_indeed_crawler.py
"""
Indeedクローラーのテスト
"""
import pytest
from bs4 import BeautifulSoup
from indeed_crawler import parse_indeed_job


class TestIndeedParser:
    """Indeed求人パーサーのテスト"""

    def get_mock_indeed_card(
        self,
        title="テストエンジニア",
        company="テスト株式会社",
        location="東京都渋谷区",
        salary="月給 25万円 ~ 30万円",
        employment_type="正社員",
    ):
        """テスト用のIndeed求人カードHTML（実際の構造）"""
        html = f"""
        <div class="job_seen_beacon">
            <h2 class="jobTitle"><a href="#">{title}</a></h2>
            <span data-testid="company-name">{company}</span>
            <div data-testid="text-location">{location}</div>
            <ul>
                <li class="salary-snippet-container" data-testid="attribute_snippet_testid">{salary}</li>
                <li data-testid="attribute_snippet_testid">{employment_type}</li>
            </ul>
        </div>
        """
        soup = BeautifulSoup(html, "html.parser")
        return soup.find("div", class_="job_seen_beacon")

    def test_parse_basic_job(self):
        """基本的な求人パースのテスト"""
        card = self.get_mock_indeed_card()
        result = parse_indeed_job(card)

        assert result is not None
        assert result["title"] == "テストエンジニア"
        assert result["company"] == "テスト株式会社"
        assert result["location"] == "東京都渋谷区"
        assert result["source"] == "indeed"
        assert result["employment_type"] == "正社員"

    def test_parse_monthly_salary_man_yen(self):
        """月給（万円）のパーステスト"""
        card = self.get_mock_indeed_card(salary="月給 25万円 ~ 30万円")
        result = parse_indeed_job(card)

        assert result["wage_type"] == "monthly"
        assert result["wage_min"] == 250000
        assert result["wage_max"] == 300000

    def test_parse_hourly_salary(self):
        """時給のパーステスト"""
        card = self.get_mock_indeed_card(salary="時給 1800円")
        result = parse_indeed_job(card)

        assert result["wage_type"] == "hourly"
        assert result["wage_min"] == 1800

    def test_parse_annual_salary(self):
        """年収のパーステスト"""
        card = self.get_mock_indeed_card(salary="年収 500万円")
        result = parse_indeed_job(card)

        assert result["wage_type"] == "annual"
        assert result["wage_min"] == 5000000

    def test_parse_employment_type(self):
        """雇用形態のパーステスト"""
        card = self.get_mock_indeed_card(employment_type="アルバイト・パート")
        result = parse_indeed_job(card)

        assert result["employment_type"] == "アルバイト・パート"

    def test_parse_no_salary(self):
        """給与情報なしのパーステスト"""
        html = """
        <div class="job_seen_beacon">
            <h2 class="jobTitle"><a href="#">開発者</a></h2>
            <span data-testid="company-name">ABC社</span>
            <div data-testid="text-location">大阪府</div>
            <ul>
                <li data-testid="attribute_snippet_testid">正社員</li>
            </ul>
        </div>
        """
        soup = BeautifulSoup(html, "html.parser")
        card = soup.find("div", class_="job_seen_beacon")
        result = parse_indeed_job(card)

        assert result["wage_min"] == 0
        assert result["wage_type"] == "unknown"
        assert result["employment_type"] == "正社員"

    def test_parse_empty_card(self):
        """空のカードのパーステスト"""
        html = '<div class="job_seen_beacon"></div>'
        soup = BeautifulSoup(html, "html.parser")
        card = soup.find("div", class_="job_seen_beacon")
        result = parse_indeed_job(card)

        assert result["title"] == ""
        assert result["company"] == ""


class TestIndeedCrawlerImport:
    """Indeedクローラーのインポートテスト"""

    def test_run_indeed_crawler_import(self):
        """run_indeed_crawler関数のインポートテスト"""
        from indeed_crawler import run_indeed_crawler

        assert callable(run_indeed_crawler)
