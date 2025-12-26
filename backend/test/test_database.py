# backend/test/test_database.py
import pytest
import sqlite3
import os
from database import get_connection, save_job, init_db


class TestDatabaseAccumulation:
    """データ蓄積機能のテスト"""

    def setup_method(self):
        """各テストの前にテスト用DBを準備"""
        self.test_db = "test_jobs.db"
        # 既存のテストDBを削除
        if os.path.exists(self.test_db):
            os.remove(self.test_db)

    def teardown_method(self):
        """各テストの後にテスト用DBを削除"""
        if os.path.exists(self.test_db):
            os.remove(self.test_db)

    def test_init_db_creates_table(self):
        """init_dbはテーブルを作成する"""
        from database import init_db_with_path

        init_db_with_path(self.test_db)

        conn = sqlite3.connect(self.test_db)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='jobs'"
        )
        result = cursor.fetchone()
        conn.close()

        assert result is not None
        assert result[0] == "jobs"

    def test_init_db_accumulate_mode_keeps_data(self):
        """蓄積モードでは既存データを保持する"""
        from database import init_db_with_path, save_job_to_db

        # 1. 初回のDB初期化とデータ保存
        init_db_with_path(self.test_db, reset=True)
        conn = sqlite3.connect(self.test_db)
        save_job_to_db(
            conn,
            ("テスト職種1", 200000, 300000, "monthly", "テスト会社1", "東京都", ""),
        )
        conn.close()

        # 2. 蓄積モードでDB初期化（データは消えない）
        init_db_with_path(self.test_db, reset=False)

        # 3. データが保持されていることを確認
        conn = sqlite3.connect(self.test_db)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM jobs")
        count = cursor.fetchone()[0]
        conn.close()

        assert count == 1

    def test_duplicate_check_prevents_same_job(self):
        """重複チェックで同じ求人は保存されない"""
        from database import init_db_with_path, save_job_to_db, is_duplicate

        init_db_with_path(self.test_db, reset=True)
        conn = sqlite3.connect(self.test_db)

        job_data = ("テスト職種", 200000, 300000, "monthly", "テスト会社", "東京都", "")

        # 1回目: 保存成功
        save_job_to_db(conn, job_data)

        # 2回目: 重複チェック
        assert is_duplicate(conn, "テスト職種", "テスト会社") == True
        assert is_duplicate(conn, "別の職種", "テスト会社") == False

        conn.close()


class TestStatsAPI:
    """統計情報APIのテスト"""

    def test_get_stats_returns_correct_data(self):
        """統計情報が正しく計算される"""
        from database import calculate_stats

        # モックデータ
        jobs = [
            {"wage_min": 200000, "wage_type": "monthly"},
            {"wage_min": 300000, "wage_type": "monthly"},
            {"wage_min": 1200, "wage_type": "hourly"},
            {"wage_min": 1500, "wage_type": "hourly"},
        ]

        stats = calculate_stats(jobs)

        assert stats["total_count"] == 4
        assert stats["monthly_count"] == 2
        assert stats["hourly_count"] == 2
        assert stats["avg_monthly_wage"] == 250000
        assert stats["avg_hourly_wage"] == 1350
