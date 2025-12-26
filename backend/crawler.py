# crawler.py
import re
import time
import sqlite3
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from database import save_job_if_not_duplicate, get_connection, init_db

# ==========================================
# 1. ユーティリティ関数 (TDD済み)
# ==========================================


def clean_money(text):
    """金額文字列を数値に変換する"""
    if not text:
        return 0
    clean_text = re.sub(r"[^\d]", "", str(text))
    if not clean_text:
        return 0
    return int(clean_text)


# 業界分類のためのキーワード辞書（優先順位の高い順）
INDUSTRY_KEYWORDS = {
    "製造・建設": [
        "工場",
        "製造",
        "建設",
        "施工管理",
        "施工",
        "電気工事",
        "設備",
        "機械",
        "溶接",
        "組立",
        "検品",
        "倉庫",
        "物流",
        "配送",
        "現場",
        "作業員",
    ],
    "IT・エンジニア": [
        "エンジニア",
        "プログラマ",
        "SE",
        "開発",
        "IT",
        "Web",
        "システム",
        "ソフトウェア",
        "インフラ",
        "ネットワーク",
        "データ",
        "AI",
        "機械学習",
    ],
    "医療・介護": [
        "看護",
        "介護",
        "医療",
        "病院",
        "クリニック",
        "福祉",
        "保育",
        "ケア",
        "ヘルパー",
        "リハビリ",
        "薬剤",
        "検査技師",
        "歯科",
    ],
    "サービス・販売": [
        "販売",
        "接客",
        "店舗",
        "レジ",
        "飲食",
        "調理",
        "ホテル",
        "サービス",
        "清掃",
        "美容",
        "理容",
    ],
    "営業・事務": [
        "営業",
        "事務",
        "経理",
        "総務",
        "人事",
        "秘書",
        "受付",
        "コールセンター",
        "カスタマー",
        "サポート",
        "管理",
    ],
}


def classify_industry(title):
    """
    職種タイトルから業界を推定する

    Args:
        title: 職種タイトル

    Returns:
        業界名（IT・エンジニア、医療・介護、営業・事務、サービス・販売、製造・建設、その他）
    """
    if not title:
        return "その他"

    title_upper = title.upper()

    for industry, keywords in INDUSTRY_KEYWORDS.items():
        for keyword in keywords:
            if keyword.upper() in title_upper:
                return industry

    return "その他"


def parse_job_html(element):
    """
    本番用: ハローワークの求人カード(table.kyujin)を受け取り辞書を返す
    実際のハローワークHTML構造に対応（ネストされたテーブル）
    """
    try:
        # タイトル: kyujin_headクラスの行から取得
        title = ""
        head = element.find("tr", class_="kyujin_head")
        if head:
            # 最初のtd内のテキスト（リンク内の場合もある）
            link = head.find("a")
            if link:
                title = link.get_text(strip=True)
            else:
                first_td = head.find("td")
                if first_td:
                    title = first_td.get_text(strip=True)

        # kyujin_body内のネストされたテーブルから情報を抽出
        body = element.find("tr", class_="kyujin_body")

        company = ""
        location = ""
        wage_text = ""

        if body:
            # ネストされたテーブルの全行を検索
            inner_rows = body.find_all("tr", class_="border_new")

            for row in inner_rows:
                tds = row.find_all("td")
                if len(tds) >= 2:
                    label = tds[0].get_text(strip=True)
                    value = tds[1].get_text(strip=True)

                    if "事業所名" in label:
                        company = value
                    elif "就業場所" in label:
                        location = value
                    elif "賃金" in label:
                        wage_text = value
                    elif "仕事の内容" in label and not title:
                        # タイトルが取れなかった場合のフォールバック
                        title = value[:100] if value else ""

        # 給与情報の抽出
        full_text = element.text

        # 賃金形態の判定
        wage_type = "unknown"
        if "時給" in full_text:
            wage_type = "hourly"
        elif "月給" in full_text:
            wage_type = "monthly"
        elif "日給" in full_text:
            wage_type = "daily"
        elif "年俸" in full_text:
            wage_type = "annual"

        # 金額の抽出（wage_textから優先、なければfull_textから）
        wages = re.findall(r"([\d,]+)円", wage_text if wage_text else "")
        if not wages:
            wages = re.findall(r"([\d,]+)円", full_text)

        wage_min = 0
        wage_max = 0
        if len(wages) >= 1:
            wage_min = clean_money(wages[0])
            wage_max = clean_money(wages[1]) if len(wages) >= 2 else wage_min

        # 金額から賃金形態を推測
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
            "url": "",
        }

    except Exception as e:
        print(f"  ⚠️ パースエラー: {e}")
        return None


# ==========================================
# 2. クローラー実行処理（自動化版）
# ==========================================

# 都道府県コードの辞書
PREFECTURE_CODES = {
    "北海道": "01",
    "青森県": "02",
    "岩手県": "03",
    "宮城県": "04",
    "秋田県": "05",
    "山形県": "06",
    "福島県": "07",
    "茨城県": "08",
    "栃木県": "09",
    "群馬県": "10",
    "埼玉県": "11",
    "千葉県": "12",
    "東京都": "13",
    "神奈川県": "14",
    "新潟県": "15",
    "富山県": "16",
    "石川県": "17",
    "福井県": "18",
    "山梨県": "19",
    "長野県": "20",
    "岐阜県": "21",
    "静岡県": "22",
    "愛知県": "23",
    "三重県": "24",
    "滋賀県": "25",
    "京都府": "26",
    "大阪府": "27",
    "兵庫県": "28",
    "奈良県": "29",
    "和歌山県": "30",
    "鳥取県": "31",
    "島根県": "32",
    "岡山県": "33",
    "広島県": "34",
    "山口県": "35",
    "徳島県": "36",
    "香川県": "37",
    "愛媛県": "38",
    "高知県": "39",
    "福岡県": "40",
    "佐賀県": "41",
    "長崎県": "42",
    "熊本県": "43",
    "大分県": "44",
    "宮崎県": "45",
    "鹿児島県": "46",
    "沖縄県": "47",
}

# 地域別都道府県マッピング
REGION_PREFECTURES = {
    "hokkaido_tohoku": [
        "北海道",
        "青森県",
        "岩手県",
        "宮城県",
        "秋田県",
        "山形県",
        "福島県",
    ],
    "kanto": ["茨城県", "栃木県", "群馬県", "埼玉県", "千葉県", "東京都", "神奈川県"],
    "chubu": [
        "新潟県",
        "富山県",
        "石川県",
        "福井県",
        "山梨県",
        "長野県",
        "岐阜県",
        "静岡県",
        "愛知県",
    ],
    "kansai": ["三重県", "滋賀県", "京都府", "大阪府", "兵庫県", "奈良県", "和歌山県"],
    "chugoku": ["鳥取県", "島根県", "岡山県", "広島県", "山口県"],
    "shikoku": ["徳島県", "香川県", "愛媛県", "高知県"],
    "kyushu": [
        "福岡県",
        "佐賀県",
        "長崎県",
        "熊本県",
        "大分県",
        "宮崎県",
        "鹿児島県",
        "沖縄県",
    ],
}


def get_prefectures_by_region(region):
    """
    地域名から都道府県リストを取得

    Args:
        region: 地域名 ('all', 'kanto', 'kansai' など)

    Returns:
        都道府県名のリスト
    """
    if region == "all":
        return list(PREFECTURE_CODES.keys())

    return REGION_PREFECTURES.get(region, [])


def run_crawler(
    prefecture="北海道", max_pages=3, headless=False, force=False, keyword=""
):
    """
    ハローワーク求人を自動収集する

    Args:
        prefecture: 検索する都道府県名（例: "北海道", "大阪府"）
        max_pages: 取得するページ数（1ページ50件）
        headless: ヘッドレスモードで実行するか
        force: Trueの場合、重複チェックをスキップして強制保存
    """
    mode = "強制" if force else "通常"
    print(
        f"🚀 クローラーを起動中... (対象: {prefecture}, 最大{max_pages}ページ, {mode}モード)"
    )

    options = Options()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )

    driver = webdriver.Chrome(
        service=ChromeService(ChromeDriverManager().install()), options=options
    )
    driver.implicitly_wait(5)
    wait = WebDriverWait(driver, 30)

    try:
        # ハローワーク求人検索ページに直接アクセス
        print("📍 求人検索ページにアクセス中...")
        driver.get(
            "https://www.hellowork.mhlw.go.jp/kensaku/GECA110010.do?action=initDisp&screenId=GECA110010"
        )

        # ページ読み込み完了を待機
        WebDriverWait(driver, 30).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        time.sleep(3)

        # 都道府県を選択（SELECTドロップダウン）
        print(f"📍 都道府県を選択中: {prefecture}")
        try:
            pref_code = PREFECTURE_CODES.get(prefecture, "01")
            dropdown = wait.until(
                EC.visibility_of_element_located((By.ID, "ID_tDFK1CmbBox"))
            )
            select = Select(dropdown)
            select.select_by_value(pref_code)
            print(f"  ✅ {prefecture}を選択しました")
            time.sleep(2)
        except Exception as e:
            print(f"  ⚠️ 都道府県選択でエラー: {e}")
            print("  → 全国検索で続行します")

        # 検索ボタンをクリック（JavaScript経由）
        print("📍 検索を実行中...")
        try:
            search_button = wait.until(
                EC.visibility_of_element_located((By.ID, "ID_searchBtn"))
            )
            driver.execute_script("arguments[0].scrollIntoView(true);", search_button)
            time.sleep(1)
            driver.execute_script("arguments[0].click();", search_button)
            time.sleep(5)
            print("  ✅ 検索実行完了")
        except Exception as e:
            print(f"  ❌ 検索ボタンクリックでエラー: {e}")
            raise

        conn = get_connection()
        total_count = 0

        # ページごとにデータ収集
        for page in range(1, max_pages + 1):
            print(f"\n📥 ページ {page}/{max_pages} を解析中...")

            html = driver.page_source
            soup = BeautifulSoup(html, "html.parser")

            # 求人テーブルを探す
            job_rows = soup.select("table.kyujin")

            if not job_rows:
                print("  ⚠️ このページに求人データがありません")
                break

            page_count = 0
            skip_count = 0
            for row in job_rows:
                data = parse_job_html(row)
                if data:
                    # 業界を自動分類
                    industry = classify_industry(data["title"])

                    job_tuple = (
                        data["title"],
                        data["wage_min"],
                        data["wage_max"],
                        data["wage_type"],
                        data["company"],
                        data["location"],
                        data["url"],
                        industry,  # 業界分類を追加
                    )

                    # 強制モードの場合は重複チェックをスキップ
                    if force:
                        from database import save_job_to_db

                        save_job_to_db(conn, job_tuple)
                        page_count += 1
                        print(
                            f"  - [{data['wage_type']}][{industry}]: {data['title'][:25]}... ({data['wage_min']}円)"
                        )
                    elif save_job_if_not_duplicate(conn, job_tuple):
                        page_count += 1
                        print(
                            f"  - [{data['wage_type']}][{industry}]: {data['title'][:25]}... ({data['wage_min']}円)"
                        )
                    else:
                        skip_count += 1

            total_count += page_count
            if force:
                print(f"  ✅ {page_count}件を保存 (強制モード)")
            else:
                print(f"  ✅ {page_count}件を保存 ({skip_count}件は重複スキップ)")

            # 次のページへ
            if page < max_pages:
                try:
                    # 複数のパターンで「次へ」ボタンを探す
                    next_button = None
                    for selector in [
                        "//input[@value='次へ']",
                        "//button[contains(text(), '次へ')]",
                        "//a[contains(text(), '次')]",
                        "//input[contains(@value, '次')]",
                    ]:
                        try:
                            next_button = driver.find_element(By.XPATH, selector)
                            break
                        except:
                            continue

                    if next_button and next_button.is_enabled():
                        driver.execute_script("arguments[0].click();", next_button)
                        time.sleep(3)
                    else:
                        print("  → 最後のページに到達しました")
                        break
                except Exception as e:
                    print(f"  → 次のページがありません: {e}")
                    break

        conn.close()
        print(f"\n🎉 完了！ 合計 {total_count} 件のデータを jobs.db に保存しました。")

    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        import traceback

        traceback.print_exc()

    finally:
        time.sleep(2)
        driver.quit()


if __name__ == "__main__":
    import sys

    # コマンドライン引数から都道府県を取得（デフォルト: 北海道）
    prefecture = sys.argv[1] if len(sys.argv) > 1 else "北海道"
    max_pages = int(sys.argv[2]) if len(sys.argv) > 2 else 3

    run_crawler(prefecture=prefecture, max_pages=max_pages)
