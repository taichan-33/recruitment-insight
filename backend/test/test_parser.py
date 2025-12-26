# backend/test/test_parser.py
from bs4 import BeautifulSoup
from crawler import parse_job_html


def get_mock_soup(wage_text):
    """
    テスト用のモックHTML(テーブル構造)を作成するヘルパー関数
    実際のハローワーク構造（kyujin_head + kyujin_body + border_new）に対応
    """
    html = f"""
    <table class="kyujin">
        <tr class="kyujin_head">
            <td><a href="#">AIアプリ開発エンジニア</a></td>
        </tr>
        <tr class="kyujin_body">
            <td>
                <table class="noborder">
                    <tr class="border_new">
                        <td class="fb">事業所名</td>
                        <td>株式会社テストテック</td>
                    </tr>
                    <tr class="border_new">
                        <td class="fb">就業場所</td>
                        <td>大阪市北区</td>
                    </tr>
                    <tr class="border_new">
                        <td class="fb">賃金（手当等を含む）</td>
                        <td>{wage_text}</td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
    """
    soup = BeautifulSoup(html, "html.parser")
    return soup.find("table", class_="kyujin")


def test_parse_job_html():
    """基本情報のパース確認"""
    row = get_mock_soup("250,000円〜500,000円")

    result = parse_job_html(row)

    assert result is not None, "Noneが返ってきています"
    assert result["title"] == "AIアプリ開発エンジニア"
    assert result["company"] == "株式会社テストテック"
    assert result["location"] == "大阪市北区"
    assert result["wage_min"] == 250000
    assert result["wage_max"] == 500000


def test_parse_wage_type_hourly():
    """時給判定の確認"""
    row = get_mock_soup("時給 1,200円〜1,500円")

    result = parse_job_html(row)

    assert result is not None
    assert result["wage_type"] == "hourly"
    assert result["wage_min"] == 1200


def test_parse_wage_type_monthly():
    """月給判定の確認"""
    row = get_mock_soup("月給 200,000円〜")

    result = parse_job_html(row)

    assert result is not None
    assert result["wage_type"] == "monthly"
    assert result["wage_min"] == 200000
