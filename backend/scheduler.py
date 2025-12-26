# backend/scheduler.py
"""
スケジュール実行機能
APSchedulerを使用して定期的にクローラーを実行
"""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import datetime
import json
import os

# スケジューラーインスタンス
scheduler = BackgroundScheduler()
scheduler_started = False

# スケジュール設定ファイル
SCHEDULE_FILE = "schedules.json"


def load_schedules():
    """保存済みスケジュールを読み込む"""
    if os.path.exists(SCHEDULE_FILE):
        with open(SCHEDULE_FILE, "r") as f:
            return json.load(f)
    return []


def save_schedules(schedules):
    """スケジュールを保存"""
    with open(SCHEDULE_FILE, "w") as f:
        json.dump(schedules, f, ensure_ascii=False, indent=2)


def get_schedules():
    """スケジュール一覧を取得"""
    return load_schedules()


def add_schedule(
    name, prefecture, interval_hours=24, max_pages=10, keyword="", force=False
):
    """
    スケジュールを追加

    Args:
        name: スケジュール名（一意）
        prefecture: 収集対象の都道府県
        interval_hours: 実行間隔（時間）
        max_pages: 最大ページ数
        keyword: 検索キーワード
        force: 強制収集モード
    """
    schedules = load_schedules()

    # 既存のスケジュールがあれば削除
    schedules = [s for s in schedules if s["name"] != name]

    new_schedule = {
        "name": name,
        "prefecture": prefecture,
        "interval_hours": interval_hours,
        "max_pages": max_pages,
        "keyword": keyword,
        "force": force,
        "created_at": datetime.datetime.now().isoformat(),
        "last_run": None,
    }

    schedules.append(new_schedule)
    save_schedules(schedules)

    # ジョブを追加
    _add_job(new_schedule)

    return {"success": True, "schedule": new_schedule}


def remove_schedule(name):
    """スケジュールを削除"""
    schedules = load_schedules()
    schedules = [s for s in schedules if s["name"] != name]
    save_schedules(schedules)

    # ジョブを削除
    try:
        scheduler.remove_job(name)
    except:
        pass

    return {"success": True}


def _add_job(schedule):
    """スケジューラーにジョブを追加"""
    global scheduler_started

    def job_func():
        from crawler import run_crawler

        run_crawler(
            prefecture=schedule["prefecture"],
            max_pages=schedule["max_pages"],
            headless=True,
            force=schedule.get("force", False),
            keyword=schedule.get("keyword", ""),
        )
        # 最終実行時間を更新
        schedules = load_schedules()
        for s in schedules:
            if s["name"] == schedule["name"]:
                s["last_run"] = datetime.datetime.now().isoformat()
        save_schedules(schedules)

    scheduler.add_job(
        job_func,
        trigger=IntervalTrigger(hours=schedule["interval_hours"]),
        id=schedule["name"],
        replace_existing=True,
    )

    if not scheduler_started:
        scheduler.start()
        scheduler_started = True


def start_scheduler():
    """スケジューラーを開始し、保存済みジョブを復元"""
    global scheduler_started

    if scheduler_started:
        return

    schedules = load_schedules()
    for schedule in schedules:
        _add_job(schedule)

    if not scheduler.running:
        scheduler.start()
    scheduler_started = True


def stop_scheduler():
    """スケジューラーを停止"""
    global scheduler_started
    scheduler.shutdown(wait=False)
    scheduler_started = False
