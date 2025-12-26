# database.py
import sqlite3

DB_NAME = "jobs.db"


def get_connection(db_name=None):
    """本番用のDB接続を作るヘルパー関数"""
    return sqlite3.connect(db_name or DB_NAME)


def init_db(reset=True):
    """テーブルの初期化（本番用）"""
    init_db_with_path(DB_NAME, reset=reset)


def init_db_with_path(db_path, reset=True):
    """
    テーブルの初期化（パス指定可能）

    Args:
        db_path: データベースファイルのパス
        reset: Trueの場合はテーブルを削除して再作成、Falseの場合は既存テーブルを保持
    """
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    if reset:
        c.execute("DROP TABLE IF EXISTS jobs")
        print("データベースをリセットしました。")

    # テーブルが存在しない場合のみ作成
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            wage_min INTEGER,
            wage_max INTEGER,
            wage_type TEXT,
            company TEXT,
            location TEXT,
            url TEXT,
            industry TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    )
    conn.commit()
    conn.close()
    print(f"DB initialized (reset={reset})")


def save_job(conn, job_data):
    """
    求人データを1件保存する（後方互換性のため）
    job_data: (title, min, max, type, company, loc, url)
    """
    save_job_to_db(conn, job_data)


def save_job_to_db(conn, job_data):
    """
    求人データを1件保存する
    job_data: (title, wage_min, wage_max, wage_type, company, location, url)
              または (title, wage_min, wage_max, wage_type, company, location, url, industry)
    """
    c = conn.cursor()

    if len(job_data) == 8:
        # industryを含む新形式
        c.execute(
            """
            INSERT INTO jobs (title, wage_min, wage_max, wage_type, company, location, url, industry) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
            job_data,
        )
    else:
        # 後方互換性のための旧形式
        c.execute(
            """
            INSERT INTO jobs (title, wage_min, wage_max, wage_type, company, location, url) 
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            job_data,
        )
    conn.commit()


def is_duplicate(conn, title, company):
    """
    同じタイトルと会社名の求人が既に存在するかチェック

    Returns:
        True: 重複あり
        False: 重複なし
    """
    c = conn.cursor()
    c.execute(
        """
        SELECT COUNT(*) FROM jobs WHERE title = ? AND company = ?
    """,
        (title, company),
    )
    count = c.fetchone()[0]
    return count > 0


def save_job_if_not_duplicate(conn, job_data):
    """
    重複していない場合のみ求人を保存する

    Returns:
        True: 保存成功
        False: 重複のためスキップ
    """
    title = job_data[0]
    company = job_data[4]

    if is_duplicate(conn, title, company):
        return False

    save_job_to_db(conn, job_data)
    return True


def calculate_stats(jobs):
    """
    求人データから統計情報を計算する

    Args:
        jobs: 求人データのリスト（辞書形式）

    Returns:
        統計情報の辞書
    """
    total_count = len(jobs)

    monthly_jobs = [j for j in jobs if j.get("wage_type") == "monthly"]
    hourly_jobs = [j for j in jobs if j.get("wage_type") == "hourly"]

    monthly_count = len(monthly_jobs)
    hourly_count = len(hourly_jobs)

    avg_monthly_wage = 0
    if monthly_jobs:
        avg_monthly_wage = sum(j["wage_min"] for j in monthly_jobs) // monthly_count

    avg_hourly_wage = 0
    if hourly_jobs:
        avg_hourly_wage = sum(j["wage_min"] for j in hourly_jobs) // hourly_count

    return {
        "total_count": total_count,
        "monthly_count": monthly_count,
        "hourly_count": hourly_count,
        "avg_monthly_wage": avg_monthly_wage,
        "avg_hourly_wage": avg_hourly_wage,
    }


def get_all_jobs(db_name=None, wage_type=None):
    """
    全ての求人データを取得する

    Args:
        db_name: データベースファイル名
        wage_type: フィルタリングする賃金形態 ('monthly', 'hourly' など)

    Returns:
        求人データのリスト
    """
    conn = sqlite3.connect(db_name or DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    if wage_type:
        c.execute(
            "SELECT * FROM jobs WHERE wage_type = ? ORDER BY id DESC", (wage_type,)
        )
    else:
        c.execute("SELECT * FROM jobs ORDER BY id DESC")

    rows = c.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def search_jobs(
    keyword=None,
    wage_min=None,
    wage_max=None,
    industry=None,
    location=None,
    db_name=None,
):
    """
    求人を検索する

    Args:
        keyword: 検索キーワード（タイトル・会社名に部分一致）
        wage_min: 最低給与
        wage_max: 最高給与
        industry: 業界フィルター
        location: 都道府県フィルター（部分一致）
        db_name: データベースファイル名

    Returns:
        検索結果のリスト
    """
    conn = sqlite3.connect(db_name or DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    query = "SELECT * FROM jobs WHERE 1=1"
    params = []

    if keyword:
        query += " AND (title LIKE ? OR company LIKE ?)"
        params.extend([f"%{keyword}%", f"%{keyword}%"])

    if wage_min is not None:
        query += " AND wage_min >= ?"
        params.append(wage_min)

    if wage_max is not None:
        query += " AND wage_min <= ?"
        params.append(wage_max)

    if industry:
        query += " AND industry = ?"
        params.append(industry)

    if location:
        query += " AND location LIKE ?"
        params.append(f"%{location}%")

    query += " ORDER BY id DESC"

    try:
        c.execute(query, params)
        rows = c.fetchall()
    except sqlite3.OperationalError:
        # industryカラムが存在しない場合、industryフィルターなしで再実行
        if industry:
            query = query.replace(" AND industry = ?", "")
            params = [p for p in params if p != industry]
            c.execute(query, params)
            rows = c.fetchall()
        else:
            rows = []
    finally:
        conn.close()

    return [dict(row) for row in rows]


def get_industry_stats(db_name=None):
    """
    業界別の統計を取得

    Returns:
        業界ごとの件数と平均給与
    """
    conn = sqlite3.connect(db_name or DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    try:
        c.execute(
            """
            SELECT 
                industry,
                COUNT(*) as count,
                AVG(wage_min) as avg_wage
            FROM jobs
            WHERE industry IS NOT NULL
            GROUP BY industry
            ORDER BY count DESC
        """
        )
        rows = c.fetchall()
        return [dict(row) for row in rows]
    except:
        # industryカラムがない場合は空リストを返す
        return []
    finally:
        conn.close()


def get_location_stats(db_name=None):
    """
    地域別の統計を取得（都道府県レベルで集計）

    Returns:
        地域ごとの件数
    """
    conn = sqlite3.connect(db_name or DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    # 都道府県を抽出して集計
    c.execute(
        """
        SELECT 
            CASE
                WHEN location LIKE '%北海道%' THEN '北海道'
                WHEN location LIKE '%東京%' THEN '東京都'
                WHEN location LIKE '%大阪%' THEN '大阪府'
                WHEN location LIKE '%京都%' THEN '京都府'
                WHEN location LIKE '%神奈川%' THEN '神奈川県'
                WHEN location LIKE '%埼玉%' THEN '埼玉県'
                WHEN location LIKE '%千葉%' THEN '千葉県'
                WHEN location LIKE '%愛知%' THEN '愛知県'
                WHEN location LIKE '%福岡%' THEN '福岡県'
                WHEN location LIKE '%兵庫%' THEN '兵庫県'
                WHEN location LIKE '%沖縄%' THEN '沖縄県'
                WHEN location LIKE '%広島%' THEN '広島県'
                WHEN location LIKE '%宮城%' THEN '宮城県'
                WHEN location LIKE '%静岡%' THEN '静岡県'
                ELSE location
            END as prefecture,
            COUNT(*) as count
        FROM jobs
        WHERE location IS NOT NULL AND location != ''
        GROUP BY prefecture
        ORDER BY count DESC
        LIMIT 10
    """
    )
    rows = c.fetchall()
    conn.close()

    return [{"location": row["prefecture"], "count": row["count"]} for row in rows]


def get_industry_ranking(db_name=None):
    """
    業界ランキング（求人数・平均賃金）を取得

    Returns:
        業界ごとの求人数、平均月給、平均時給のリスト
    """
    conn = sqlite3.connect(db_name or DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    try:
        c.execute(
            """
            SELECT 
                industry,
                COUNT(*) as job_count,
                ROUND(AVG(CASE WHEN wage_type = 'monthly' THEN wage_min END)) as avg_monthly,
                ROUND(AVG(CASE WHEN wage_type = 'hourly' THEN wage_min END)) as avg_hourly,
                MAX(CASE WHEN wage_type = 'monthly' THEN wage_min END) as max_monthly,
                MIN(CASE WHEN wage_type = 'monthly' AND wage_min > 0 THEN wage_min END) as min_monthly
            FROM jobs
            WHERE industry IS NOT NULL AND industry != ''
            GROUP BY industry
            ORDER BY job_count DESC
        """
        )
        rows = c.fetchall()
        return [dict(row) for row in rows]
    except:
        return []
    finally:
        conn.close()


def get_hot_industries(db_name=None):
    """
    ホットな業界を分析（求人数 × 平均賃金でスコアリング）

    Returns:
        業界のホットスコアランキング
    """
    conn = sqlite3.connect(db_name or DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    try:
        c.execute(
            """
            SELECT 
                industry,
                COUNT(*) as job_count,
                ROUND(AVG(
                    CASE 
                        WHEN wage_type = 'hourly' THEN wage_min * 160
                        WHEN wage_type = 'annual' THEN wage_min / 12
                        ELSE wage_min 
                    END
                )) as estimated_monthly,
                COUNT(*) * AVG(
                    CASE 
                        WHEN wage_type = 'hourly' THEN wage_min * 160
                        WHEN wage_type = 'annual' THEN wage_min / 12
                        ELSE wage_min 
                    END
                ) / 10000 as hot_score
            FROM jobs
            WHERE industry IS NOT NULL AND industry != '' 
                AND wage_min > 0 
                AND wage_min < 10000000
            GROUP BY industry
            ORDER BY hot_score DESC
        """
        )
        rows = c.fetchall()
        return [dict(row) for row in rows]
    except:
        return []
    finally:
        conn.close()


def get_salary_trend(db_name=None):
    """
    給与推移データを取得（月別の平均給与）

    Returns:
        月別の平均給与と求人数のリスト
    """
    conn = sqlite3.connect(db_name or DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    try:
        c.execute(
            """
            SELECT 
                strftime('%Y-%m', created_at) as month,
                COUNT(*) as job_count,
                ROUND(AVG(
                    CASE 
                        WHEN wage_type = 'hourly' THEN wage_min * 160
                        WHEN wage_type = 'annual' THEN wage_min / 12
                        ELSE wage_min 
                    END
                )) as avg_wage
            FROM jobs
            WHERE wage_min > 0 AND wage_min < 10000000
            GROUP BY month
            ORDER BY month DESC
            LIMIT 12
        """
        )
        rows = c.fetchall()
        return [dict(row) for row in rows]
    except:
        return []
    finally:
        conn.close()


def get_industry_comparison(db_name=None):
    """
    業界別比較データを取得

    Returns:
        業界ごとの求人数、平均給与、最小・最大給与
    """
    conn = sqlite3.connect(db_name or DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    try:
        c.execute(
            """
            SELECT 
                industry,
                COUNT(*) as job_count,
                ROUND(AVG(
                    CASE 
                        WHEN wage_type = 'hourly' THEN wage_min * 160
                        WHEN wage_type = 'annual' THEN wage_min / 12
                        ELSE wage_min 
                    END
                )) as avg_wage,
                MIN(
                    CASE 
                        WHEN wage_type = 'hourly' THEN wage_min * 160
                        WHEN wage_type = 'annual' THEN wage_min / 12
                        ELSE wage_min 
                    END
                ) as min_wage,
                MAX(
                    CASE 
                        WHEN wage_type = 'hourly' THEN wage_min * 160
                        WHEN wage_type = 'annual' THEN wage_min / 12
                        ELSE wage_min 
                    END
                ) as max_wage
            FROM jobs
            WHERE industry IS NOT NULL AND industry != '' 
                AND wage_min > 0 AND wage_min < 10000000
            GROUP BY industry
            ORDER BY job_count DESC
        """
        )
        rows = c.fetchall()
        return [dict(row) for row in rows]
    except:
        return []
    finally:
        conn.close()


def get_heatmap_data(db_name=None):
    """
    ヒートマップ用データを取得（地域×業界）

    Returns:
        地域と業界のマトリクスデータ
    """
    conn = sqlite3.connect(db_name or DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    try:
        # 都道府県リスト
        prefectures = [
            "北海道",
            "東京都",
            "大阪府",
            "神奈川県",
            "愛知県",
            "福岡県",
            "沖縄県",
        ]

        # 業界リスト
        c.execute(
            "SELECT DISTINCT industry FROM jobs WHERE industry IS NOT NULL AND industry != ''"
        )
        industries = [row["industry"] for row in c.fetchall()]

        # マトリクスデータ作成
        data = []
        for pref in prefectures:
            row_data = []
            for ind in industries:
                c.execute(
                    """
                    SELECT COUNT(*) as count 
                    FROM jobs 
                    WHERE location LIKE ? AND industry = ?
                    """,
                    (f"%{pref}%", ind),
                )
                result = c.fetchone()
                row_data.append(result["count"] if result else 0)
            data.append(row_data)

        return {"prefectures": prefectures, "industries": industries, "data": data}
    except:
        return {"prefectures": [], "industries": [], "data": []}
    finally:
        conn.close()
