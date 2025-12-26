# backend/test/test_advanced.py
import pytest


class TestMultiplePrefectures:
    """複数都道府県収集機能のテスト"""

    def test_region_prefectures_mapping(self):
        """地域→都道府県のマッピングが正しい"""
        from crawler import REGION_PREFECTURES

        # 北海道・東北
        assert "北海道" in REGION_PREFECTURES["hokkaido_tohoku"]
        assert "青森県" in REGION_PREFECTURES["hokkaido_tohoku"]

        # 関東
        assert "東京都" in REGION_PREFECTURES["kanto"]
        assert "神奈川県" in REGION_PREFECTURES["kanto"]

        # 関西
        assert "大阪府" in REGION_PREFECTURES["kansai"]
        assert "京都府" in REGION_PREFECTURES["kansai"]

    def test_get_prefectures_by_region(self):
        """地域指定で都道府県リストを取得"""
        from crawler import get_prefectures_by_region

        # 全国
        all_prefs = get_prefectures_by_region("all")
        assert len(all_prefs) == 47

        # 関東
        kanto = get_prefectures_by_region("kanto")
        assert len(kanto) == 7


class TestKeywordSearch:
    """キーワード検索機能のテスト"""

    def test_run_crawler_with_keyword(self):
        """キーワード付きでクローラー実行"""
        # run_crawlerにkeywordパラメータがあることを確認
        from crawler import run_crawler
        import inspect

        sig = inspect.signature(run_crawler)
        assert "keyword" in sig.parameters


class TestScheduler:
    """スケジューラー機能のテスト"""

    def test_get_schedule_list(self):
        """スケジュール一覧取得"""
        from scheduler import get_schedules

        schedules = get_schedules()
        assert isinstance(schedules, list)

    def test_add_schedule(self):
        """スケジュール追加"""
        from scheduler import add_schedule, remove_schedule

        # テスト用スケジュールを追加
        result = add_schedule(
            name="test_schedule", prefecture="東京都", interval_hours=24
        )
        assert result["success"] == True

        # クリーンアップ
        remove_schedule("test_schedule")
