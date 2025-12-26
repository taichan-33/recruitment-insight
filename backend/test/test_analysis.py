# backend/test/test_analysis.py
"""
可視化機能のテスト（TDD）
給与推移、業界比較、ヒートマップ
"""
import pytest
import sqlite3
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestSalaryTrend:
    """給与推移APIのテスト"""

    def test_get_salary_trend_returns_list(self):
        """給与推移が配列を返すこと"""
        from database import get_salary_trend

        result = get_salary_trend()
        assert isinstance(result, list)

    def test_salary_trend_has_required_fields(self):
        """給与推移データに必要なフィールドがあること"""
        from database import get_salary_trend

        result = get_salary_trend()
        if len(result) > 0:
            item = result[0]
            assert "date" in item or "month" in item
            assert "avg_wage" in item
            assert "job_count" in item


class TestIndustryComparison:
    """業界比較APIのテスト"""

    def test_get_industry_comparison_returns_list(self):
        """業界比較が配列を返すこと"""
        from database import get_industry_comparison

        result = get_industry_comparison()
        assert isinstance(result, list)

    def test_industry_comparison_has_required_fields(self):
        """業界比較データに必要なフィールドがあること"""
        from database import get_industry_comparison

        result = get_industry_comparison()
        if len(result) > 0:
            item = result[0]
            assert "industry" in item
            assert "job_count" in item
            assert "avg_wage" in item
            assert "min_wage" in item
            assert "max_wage" in item


class TestHeatmapData:
    """ヒートマップAPIのテスト"""

    def test_get_heatmap_data_returns_dict(self):
        """ヒートマップがdict形式を返すこと"""
        from database import get_heatmap_data

        result = get_heatmap_data()
        assert isinstance(result, dict)

    def test_heatmap_has_required_structure(self):
        """ヒートマップデータに必要な構造があること"""
        from database import get_heatmap_data

        result = get_heatmap_data()
        assert "prefectures" in result
        assert "industries" in result
        assert "data" in result
        assert isinstance(result["prefectures"], list)
        assert isinstance(result["industries"], list)
        assert isinstance(result["data"], list)
