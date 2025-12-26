from flask import Blueprint, jsonify
from database import (
    get_all_jobs,
    calculate_stats,
    get_industry_stats,
    get_location_stats,
    get_industry_ranking,
    get_hot_industries,
    get_salary_trend,
    get_industry_comparison,
    get_heatmap_data,
)

analysis_bp = Blueprint("analysis", __name__)
DB_NAME = "jobs.db"


@analysis_bp.route("/api/stats")
def get_stats():
    """統計情報を取得"""
    try:
        jobs_list = get_all_jobs(DB_NAME)
        stats = calculate_stats(jobs_list)
        return jsonify(stats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@analysis_bp.route("/api/analysis/industry")
def get_industry_analysis():
    """業界別統計を取得"""
    try:
        stats = get_industry_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@analysis_bp.route("/api/analysis/location")
def get_location_analysis():
    """地域別統計を取得"""
    try:
        stats = get_location_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@analysis_bp.route("/api/analysis/ranking")
def get_ranking():
    """業界ランキング（求人数・平均賃金）を取得"""
    try:
        ranking = get_industry_ranking()
        return jsonify(ranking)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@analysis_bp.route("/api/analysis/hot")
def get_hot():
    """ホット業界ランキングを取得"""
    try:
        hot = get_hot_industries()
        return jsonify(hot)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@analysis_bp.route("/api/analysis/salary-trend")
def salary_trend():
    """給与推移データを取得"""
    try:
        result = get_salary_trend()
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@analysis_bp.route("/api/analysis/industry-comparison")
def industry_comparison():
    """業界比較データを取得"""
    try:
        result = get_industry_comparison()
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@analysis_bp.route("/api/analysis/heatmap")
def heatmap():
    """ヒートマップデータを取得"""
    try:
        result = get_heatmap_data()
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
