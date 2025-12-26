from flask import Blueprint, jsonify, request
from ml_predictor import train_model, predict_salary as ml_predict

ml_bp = Blueprint("ml", __name__)


@ml_bp.route("/api/ml/train", methods=["POST"])
def train_ml_model():
    """MLモデルを訓練"""
    try:
        result = train_model()
        # Frontend expects a 'message' field
        if result.get("success"):
            result["message"] = (
                f"モデルの再学習が完了しました。精度(R2): {result.get('r2')}"
            )
        else:
            result["message"] = f"学習エラー: {result.get('error')}"
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "message": str(e), "error": str(e)}), 500


@ml_bp.route("/api/ml/predict", methods=["POST"])
def predict_salary():
    """給与を予測"""
    data = request.get_json() or {}
    industry = data.get("industry", "その他")
    location = data.get("location", "東京都")
    wage_type = data.get("wage_type", "monthly")

    try:
        result = ml_predict(industry, location, wage_type)

        # Frontend expects 'status' and 'confidence_interval'
        if result.get("success"):
            result["status"] = "success"
            wage = result.get("predicted_wage", 0)
            # 簡易的な信頼区間（±10%）
            result["confidence_interval"] = [wage * 0.9, wage * 1.1]
        else:
            result["status"] = "error"
            result["message"] = result.get("error")

        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "status": "error", "message": str(e)}), 500
