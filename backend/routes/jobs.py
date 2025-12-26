from flask import Blueprint, jsonify, request
from database import get_all_jobs, init_db, search_jobs

jobs_bp = Blueprint("jobs", __name__)
DB_NAME = "jobs.db"


@jobs_bp.route("/api/jobs")
def get_jobs():
    """求人一覧を取得（フィルタリング対応）"""
    wage_type = request.args.get("wage_type")

    try:
        jobs_list = get_all_jobs(DB_NAME, wage_type=wage_type)
        return jsonify(jobs_list)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@jobs_bp.route("/api/search")
def search():
    """求人を検索する"""
    keyword = request.args.get("keyword")
    wage_min = request.args.get("wage_min", type=int)
    wage_max = request.args.get("wage_max", type=int)
    industry = request.args.get("industry")
    location = request.args.get("location")  # 都道府県フィルター

    try:
        results = search_jobs(
            keyword=keyword,
            wage_min=wage_min,
            wage_max=wage_max,
            industry=industry,
            location=location,
        )
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@jobs_bp.route("/api/init", methods=["POST"])
def init_database():
    """データベースを初期化する"""
    data = request.get_json() or {}
    reset = data.get("reset", False)

    try:
        init_db(reset=reset)
        return jsonify(
            {
                "status": "success",
                "message": f"データベースを初期化しました (reset={reset})",
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@jobs_bp.route("/api/industries")
def get_industries():
    """業界リストを取得"""
    industries = [
        "IT・エンジニア",
        "医療・介護",
        "営業・事務",
        "サービス・販売",
        "製造・建設",
        "その他",
    ]
    return jsonify(industries)


@jobs_bp.route("/api/regions")
def get_regions():
    """地域リストを取得"""
    regions = {
        "all": "全国",
        "hokkaido_tohoku": "北海道・東北",
        "kanto": "関東",
        "chubu": "中部",
        "kansai": "関西",
        "chugoku": "中国",
        "shikoku": "四国",
        "kyushu": "九州・沖縄",
    }
    return jsonify(regions)
