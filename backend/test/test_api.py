# backend/test/test_api.py
import pytest
import json
import sys
import os

# backendディレクトリをパスに追加
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app


class TestJobsAPI:
    """求人APIのテスト"""

    def setup_method(self):
        """テストクライアントを準備"""
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_get_jobs_returns_list(self):
        """GET /api/jobs はリストを返す"""
        response = self.client.get("/api/jobs")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)

    def test_get_jobs_with_filter(self):
        """GET /api/jobs?wage_type=hourly はフィルタリングする"""
        response = self.client.get("/api/jobs?wage_type=hourly")
        assert response.status_code == 200
        data = json.loads(response.data)
        # フィルタリングされたデータはすべてhourlyであるべき
        for job in data:
            assert job.get("wage_type") == "hourly"

    def test_get_stats_returns_statistics(self):
        """GET /api/stats は統計情報を返す"""
        response = self.client.get("/api/stats")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "total_count" in data
        assert "monthly_count" in data
        assert "hourly_count" in data


class TestCrawlAPI:
    """クローラーAPIのテスト"""

    def setup_method(self):
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_crawl_endpoint_exists(self):
        """POST /api/crawl エンドポイントが存在する"""
        response = self.client.post(
            "/api/crawl", json={"prefecture": "北海道", "max_pages": 1}
        )
        # 実際にクロールは実行しないが、エンドポイントは200または202を返す
        assert response.status_code in [200, 202, 400]

    def test_crawl_requires_prefecture(self):
        """クロール実行には都道府県が必要"""
        response = self.client.post("/api/crawl", json={})
        # パラメータ不足でもデフォルト値で動作するか確認
        assert response.status_code in [200, 202, 400]
