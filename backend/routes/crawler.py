from flask import Blueprint, jsonify, request
import threading
from shared_state import crawler_status
from scheduler import get_schedules, add_schedule, remove_schedule

crawler_bp = Blueprint("crawler", __name__)


@crawler_bp.route("/api/crawl", methods=["POST"])
def run_crawl():
    """クローラーを実行する"""
    if crawler_status["is_running"]:
        return (
            jsonify({"status": "error", "message": "クローラーは既に実行中です"}),
            400,
        )

    data = request.get_json() or {}
    prefecture = data.get("prefecture", "北海道")
    max_pages = data.get("max_pages", 10)
    force = data.get("force", False)  # 強制収集モード

    # バックグラウンドでクローラーを実行
    def run_crawler_thread():
        crawler_status["is_running"] = True
        crawler_status["last_error"] = None

        try:
            from crawler import run_crawler

            run_crawler(
                prefecture=prefecture, max_pages=max_pages, headless=False, force=force
            )
            crawler_status["last_result"] = {
                "success": True,
                "prefecture": prefecture,
                "max_pages": max_pages,
                "force": force,
            }
        except Exception as e:
            crawler_status["last_error"] = str(e)
            crawler_status["last_result"] = {"success": False, "error": str(e)}
        finally:
            crawler_status["is_running"] = False

    thread = threading.Thread(target=run_crawler_thread)
    thread.start()

    return (
        jsonify(
            {
                "status": "started",
                "message": f"クローラーを開始しました: {prefecture}, {max_pages}ページ, {'強制モード' if force else '通常モード'}",
            }
        ),
        202,
    )


@crawler_bp.route("/api/crawl/indeed", methods=["POST"])
def run_crawl_indeed():
    """Indeedから求人を収集"""
    if crawler_status["is_running"]:
        return (
            jsonify({"status": "error", "message": "クローラーは既に実行中です"}),
            400,
        )

    data = request.get_json() or {}
    keyword = data.get("keyword", "")
    location = data.get("location", "東京都")
    max_pages = data.get("max_pages", 3)

    def run_indeed_thread():
        crawler_status["is_running"] = True
        crawler_status["last_error"] = None

        try:
            print("🚀 Indeedクローラースレッド開始...")
            from indeed_crawler import run_indeed_crawler

            print(f"📦 indeed_crawler インポート成功")

            result = run_indeed_crawler(
                keyword=keyword, location=location, max_pages=max_pages, headless=False
            )
            crawler_status["last_result"] = result
            print(f"✅ クローラー完了: {result}")
        except Exception as e:
            import traceback

            print(f"❌ Indeedクローラーエラー: {e}")
            traceback.print_exc()
            crawler_status["last_error"] = str(e)
            crawler_status["last_result"] = {"success": False, "error": str(e)}
        finally:
            crawler_status["is_running"] = False

    thread = threading.Thread(target=run_indeed_thread)
    thread.start()

    return (
        jsonify(
            {
                "status": "started",
                "message": f"Indeed検索を開始: {keyword or '全て'} @ {location}",
            }
        ),
        202,
    )


@crawler_bp.route("/api/crawl/region", methods=["POST"])
def run_crawl_region():
    """複数都道府県を一括収集"""
    if crawler_status["is_running"]:
        return (
            jsonify({"status": "error", "message": "クローラーは既に実行中です"}),
            400,
        )

    data = request.get_json() or {}
    region = data.get("region", "kanto")
    max_pages = data.get("max_pages", 3)
    force = data.get("force", False)
    keyword = data.get("keyword", "")

    from crawler import get_prefectures_by_region

    prefectures = get_prefectures_by_region(region)

    def run_region_crawler():
        crawler_status["is_running"] = True
        crawler_status["last_error"] = None

        try:
            from crawler import run_crawler

            total = 0
            for i, pref in enumerate(prefectures):
                print(f"\n🌏 [{i+1}/{len(prefectures)}] {pref}を収集中...")
                run_crawler(
                    prefecture=pref,
                    max_pages=max_pages,
                    headless=True,
                    force=force,
                    keyword=keyword,
                )
                total += 1

            crawler_status["last_result"] = {
                "success": True,
                "region": region,
                "prefectures_count": total,
            }
        except Exception as e:
            crawler_status["last_error"] = str(e)
            crawler_status["last_result"] = {"success": False, "error": str(e)}
        finally:
            crawler_status["is_running"] = False

    thread = threading.Thread(target=run_region_crawler)
    thread.start()

    return (
        jsonify(
            {
                "status": "started",
                "message": f"{len(prefectures)}都道府県の収集を開始しました",
                "prefectures": prefectures,
            }
        ),
        202,
    )


@crawler_bp.route("/api/crawl/status")
def get_crawl_status():
    """クローラーの実行状態を取得"""
    return jsonify(
        {
            "is_running": crawler_status["is_running"],
            "last_result": crawler_status["last_result"],
            "last_error": crawler_status["last_error"],
        }
    )


@crawler_bp.route("/api/schedules")
def get_schedules_api():
    """スケジュール一覧を取得"""
    return jsonify(get_schedules())


@crawler_bp.route("/api/schedules", methods=["POST"])
def add_schedule_api():
    """スケジュールを追加"""
    data = request.get_json() or {}
    result = add_schedule(
        name=data.get("name", "default"),
        prefecture=data.get("prefecture", "東京都"),
        interval_hours=data.get("interval_hours", 24),
        max_pages=data.get("max_pages", 10),
        keyword=data.get("keyword", ""),
        force=data.get("force", False),
    )
    return jsonify(result)


@crawler_bp.route("/api/schedules/<name>", methods=["DELETE"])
def remove_schedule_api(name):
    """スケジュールを削除"""
    result = remove_schedule(name)
    return jsonify(result)
