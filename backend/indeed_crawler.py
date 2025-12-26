# backend/indeed_crawler.py
"""
Indeed求人クローラー
キーワード・地域で求人を検索・収集
undetected-chromedriverでCAPTCHA回避
"""
import re
import time
import sqlite3
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from database import get_connection, init_db
from crawler import classify_industry, clean_money


def parse_indeed_job(card):
    """
    Indeed求人カードをパース
    実際のHTML構造:
    - 給与: li.salary-snippet-container内のテキスト
    - 雇用形態: li[data-testid="attribute_snippet_testid"]のテキスト（給与以外）
    """
    try:
        # タイトル
        title_elem = card.find("h2", class_="jobTitle")
        title = title_elem.get_text(strip=True) if title_elem else ""

        # URL
        url = ""
        if title_elem:
            link_elem = title_elem.find("a")
            if link_elem:
                href = link_elem.get("href")
                if href:
                    if href.startswith("/"):
                        url = f"https://jp.indeed.com{href}"
                    else:
                        url = href

        # 「新着」タグを除去
        if title.startswith("新着"):
            title = title[2:].strip()

        # 会社名
        company_elem = card.find("span", {"data-testid": "company-name"})
        company = company_elem.get_text(strip=True) if company_elem else ""

        # 場所
        location_elem = card.find("div", {"data-testid": "text-location"})
        if not location_elem:
            location_elem = card.find("div", {"data-testid": "icon-location"})
        location = location_elem.get_text(strip=True) if location_elem else ""

        # 給与 - salary-snippet-containerから取得
        salary_elem = card.find("li", class_="salary-snippet-container")

        wage_min = 0
        wage_max = 0
        wage_type = "unknown"
        employment_type = ""

        if salary_elem:
            salary_text = salary_elem.get_text(strip=True)

            # 給与タイプ判定
            if "時給" in salary_text:
                wage_type = "hourly"
            elif "月給" in salary_text or "月収" in salary_text:
                wage_type = "monthly"
            elif "年収" in salary_text or "年俸" in salary_text:
                wage_type = "annual"

            # 金額抽出（例: "月給 25万円 ~ 30万円" → 250000, 300000）
            # 「万円」パターン
            man_pattern = re.findall(r"([\d.]+)\s*万円", salary_text)
            if man_pattern:
                wage_min = int(float(man_pattern[0]) * 10000)
                if len(man_pattern) > 1:
                    wage_max = int(float(man_pattern[1]) * 10000)
                else:
                    wage_max = wage_min
            else:
                # 通常の数値パターン（例: "1,800円"）
                yen_pattern = re.findall(r"([\d,]+)円", salary_text.replace(",", ""))
                if yen_pattern:
                    wage_min = int(yen_pattern[0])
                    if len(yen_pattern) > 1:
                        wage_max = int(yen_pattern[1])
                    else:
                        wage_max = wage_min

            # 年収を月給に変換（12で割る）- 統一のため
            if wage_type == "annual" and wage_min > 0:
                wage_min = wage_min // 12
                wage_max = wage_max // 12
                wage_type = "monthly"  # 月給として統一

        # 雇用形態 - 給与以外のattribute_snippet_testidから取得
        attribute_elems = card.find_all(
            "li", {"data-testid": "attribute_snippet_testid"}
        )
        for attr in attribute_elems:
            if "salary-snippet-container" not in attr.get("class", []):
                text = attr.get_text(strip=True)
                if text in ["正社員", "アルバイト・パート", "派遣社員", "契約社員"]:
                    employment_type = text
                    break

        # 金額から推測
        if wage_type == "unknown" and wage_min > 0:
            if wage_min < 10000:
                wage_type = "hourly"
            elif wage_min >= 100000:
                wage_type = "monthly"

        return {
            "title": title[:100] if title else "",
            "company": company,
            "location": location,
            "wage_min": wage_min,
            "wage_max": wage_max,
            "wage_type": wage_type,
            "employment_type": employment_type,
            "employment_type": employment_type,
            "source": "indeed",
            "url": url,
        }
    except Exception as e:
        print(f"  ⚠️ パースエラー: {e}")
        return None


def run_indeed_crawler(keyword="", location="東京都", max_pages=3, headless=True):
    """
    Indeedから求人を収集
    undetected-chromedriverでCAPTCHA回避

    Args:
        keyword: 検索キーワード
        location: 地域
        max_pages: 取得ページ数
        headless: ヘッドレスモード
    """
    print(f"🔍 Indeed検索開始 (キーワード: {keyword or '全て'}, 地域: {location})")

    # undetected_chromedriverオプション
    options = uc.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")

    # undetected_chromedriverでドライバー作成（CAPTCHA回避機能内蔵）
    driver = uc.Chrome(options=options, headless=headless)
    wait = WebDriverWait(driver, 20)

    try:
        conn = get_connection()
        total_count = 0

        for page in range(max_pages):
            start = page * 10
            url = f"https://jp.indeed.com/jobs?q={keyword}&l={location}&start={start}"

            print(f"\n📥 ページ {page + 1}/{max_pages} を取得中...")
            driver.get(url)

            # ページ読み込み完了を待機
            time.sleep(3)

            # ページをスクロールしてコンテンツを読み込む
            driver.execute_script("window.scrollTo(0, 500);")
            time.sleep(1)
            driver.execute_script("window.scrollTo(0, 1000);")
            time.sleep(1)
            driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(1)

            # JavaScriptレンダリングを待機 - 求人カードが表示されるまで待つ
            try:
                wait.until(
                    EC.presence_of_element_located((By.CLASS_NAME, "job_seen_beacon"))
                )
            except:
                # 別のセレクタを試す
                try:
                    wait.until(
                        EC.presence_of_element_located(
                            (By.CSS_SELECTOR, "[class*='cardOutline']")
                        )
                    )
                except:
                    print(f"  ⚠️ 求人カードが見つかりません")

            # 求人カードを取得
            html = driver.page_source
            soup = BeautifulSoup(html, "html.parser")

            # Indeed求人カードセレクタ
            job_cards = soup.find_all("div", class_="job_seen_beacon")
            if not job_cards:
                job_cards = soup.find_all("div", {"class": re.compile("cardOutline")})

            print(f"  📋 {len(job_cards)}件の求人を発見")

            page_count = 0
            skip_count = 0
            for card in job_cards:
                job_data = parse_indeed_job(card)
                if job_data and job_data["title"]:
                    # 業界分類
                    job_data["industry"] = classify_industry(job_data["title"])

                    # 重複チェック
                    try:
                        c = conn.cursor()
                        c.execute(
                            """
                            SELECT COUNT(*) FROM jobs 
                            WHERE title = ? AND company = ?
                            """,
                            (job_data["title"], job_data["company"]),
                        )
                        exists = c.fetchone()[0] > 0

                        if exists:
                            skip_count += 1
                            continue

                        # 保存
                        c.execute(
                            """
                            INSERT INTO jobs 
                            (title, company, location, wage_min, wage_max, wage_type, industry, url)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                            """,
                            (
                                job_data["title"],
                                job_data["company"],
                                job_data["location"],
                                job_data["wage_min"],
                                job_data["wage_max"],
                                job_data["wage_type"],
                                job_data["industry"],
                                job_data.get("url", ""),
                            ),
                        )
                        page_count += 1
                    except Exception as e:
                        print(f"  ⚠️ 保存エラー: {e}")

            conn.commit()
            total_count += page_count
            if skip_count > 0:
                print(f"  ✅ {page_count}件を保存 (重複スキップ: {skip_count}件)")
            else:
                print(f"  ✅ {page_count}件を保存")

            time.sleep(2)

        print(f"\n🎉 Indeed収集完了！ 合計 {total_count} 件を保存")
        return {"success": True, "count": total_count}

    except Exception as e:
        print(f"❌ エラー: {e}")
        return {"success": False, "error": str(e)}
    finally:
        driver.quit()


if __name__ == "__main__":
    init_db()
    run_indeed_crawler(
        keyword="エンジニア", location="東京都", max_pages=2, headless=False
    )
