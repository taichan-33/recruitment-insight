# backend/ml_predictor.py
"""
給与予測MLモデル
業界・地域・雇用形態から適正給与を予測
"""
import os
import pickle
import sqlite3
from database import DB_NAME

# scikit-learn
try:
    import pandas as pd
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.preprocessing import LabelEncoder
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import mean_absolute_error, r2_score

    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    print("⚠️ scikit-learnがインストールされていません")

MODEL_PATH = os.path.join(os.path.dirname(__file__), "salary_model.pkl")
ENCODERS_PATH = os.path.join(os.path.dirname(__file__), "label_encoders.pkl")


class SalaryPredictor:
    """給与予測モデル"""

    def __init__(self):
        self.model = None
        self.encoders = {}
        self.is_trained = False

    def load_training_data(self, db_name=None):
        """DBから訓練データを取得"""
        conn = sqlite3.connect(db_name or DB_NAME)
        conn.row_factory = sqlite3.Row

        query = """
            SELECT industry, location, wage_type, wage_min
            FROM jobs
            WHERE wage_min > 0 
              AND industry IS NOT NULL 
              AND industry != ''
              AND location IS NOT NULL 
              AND location != ''
        """

        df = pd.read_sql_query(query, conn)
        conn.close()

        return df

    def prepare_features(self, df, fit_encoders=True):
        """特徴量エンジニアリング"""
        # 地域を都道府県に正規化
        df = df.copy()
        if "prefecture" not in df.columns:
            df["prefecture"] = df["location"].apply(self._extract_prefecture)

        # カテゴリ変数をエンコード
        for col in ["industry", "prefecture", "wage_type"]:
            if fit_encoders:
                self.encoders[col] = LabelEncoder()
                # 訓練データに"unknown"と"その他"を追加して未知ラベルに対応
                unique_values = list(df[col].fillna("unknown").unique())
                if "unknown" not in unique_values:
                    unique_values.append("unknown")
                if "その他" not in unique_values:
                    unique_values.append("その他")
                self.encoders[col].fit(unique_values)
                df[f"{col}_encoded"] = self.encoders[col].transform(
                    df[col].fillna("unknown")
                )
            else:
                # 未知のカテゴリは'その他'として扱う
                df[col] = df[col].apply(
                    lambda x: x if x in self.encoders[col].classes_ else "その他"
                )
                df[f"{col}_encoded"] = self.encoders[col].transform(
                    df[col].fillna("その他")
                )

        feature_cols = ["industry_encoded", "prefecture_encoded", "wage_type_encoded"]
        return df[feature_cols], df["wage_min"]

    def _extract_prefecture(self, location):
        """住所から都道府県を抽出"""
        prefectures = [
            "北海道",
            "青森県",
            "岩手県",
            "宮城県",
            "秋田県",
            "山形県",
            "福島県",
            "茨城県",
            "栃木県",
            "群馬県",
            "埼玉県",
            "千葉県",
            "東京都",
            "神奈川県",
            "新潟県",
            "富山県",
            "石川県",
            "福井県",
            "山梨県",
            "長野県",
            "岐阜県",
            "静岡県",
            "愛知県",
            "三重県",
            "滋賀県",
            "京都府",
            "大阪府",
            "兵庫県",
            "奈良県",
            "和歌山県",
            "鳥取県",
            "島根県",
            "岡山県",
            "広島県",
            "山口県",
            "徳島県",
            "香川県",
            "愛媛県",
            "高知県",
            "福岡県",
            "佐賀県",
            "長崎県",
            "熊本県",
            "大分県",
            "宮崎県",
            "鹿児島県",
            "沖縄県",
        ]
        for pref in prefectures:
            if pref in str(location):
                return pref
        return "その他"

    def train(self, db_name=None):
        """モデルを訓練"""
        if not ML_AVAILABLE:
            return {"success": False, "error": "scikit-learn未インストール"}

        print("📊 訓練データを読み込み中...")
        df = self.load_training_data(db_name)

        if len(df) < 10:
            return {"success": False, "error": "訓練データが不足（最低10件必要）"}

        print(f"  📈 {len(df)}件のデータで訓練開始")

        # 特徴量準備
        X, y = self.prepare_features(df, fit_encoders=True)

        # データ分割
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        # モデル訓練
        self.model = RandomForestRegressor(
            n_estimators=100, max_depth=10, random_state=42, n_jobs=-1
        )
        self.model.fit(X_train, y_train)

        # 評価
        y_pred = self.model.predict(X_test)
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)

        self.is_trained = True

        # モデル保存
        self.save_model()

        print(f"  ✅ 訓練完了! MAE: {mae:.0f}円, R²: {r2:.3f}")

        return {
            "success": True,
            "samples": len(df),
            "mae": round(mae),
            "r2": round(r2, 3),
        }

    def predict(self, industry, location, wage_type="monthly"):
        """給与を予測"""
        if not self.is_trained:
            # 保存済みモデルを読み込み
            if not self.load_model():
                return {"success": False, "error": "モデルが訓練されていません"}

        # 入力データ準備
        prefecture = self._extract_prefecture(location)

        input_data = pd.DataFrame(
            [
                {
                    "industry": industry,
                    "location": location,  # locationカラムを追加
                    "prefecture": prefecture,  # prefectureを直接追加
                    "wage_type": wage_type,
                    "wage_min": 0,
                }
            ]
        )

        try:
            X, _ = self.prepare_features(input_data, fit_encoders=False)

            prediction = self.model.predict(X)[0]

            return {
                "success": True,
                "predicted_wage": round(prediction),
                "industry": industry,
                "location": location,
                "wage_type": wage_type,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def save_model(self):
        """モデルを保存"""
        with open(MODEL_PATH, "wb") as f:
            pickle.dump(self.model, f)
        with open(ENCODERS_PATH, "wb") as f:
            pickle.dump(self.encoders, f)
        print(f"  💾 モデルを保存しました: {MODEL_PATH}")

    def load_model(self):
        """モデルを読み込み"""
        if os.path.exists(MODEL_PATH) and os.path.exists(ENCODERS_PATH):
            with open(MODEL_PATH, "rb") as f:
                self.model = pickle.load(f)
            with open(ENCODERS_PATH, "rb") as f:
                self.encoders = pickle.load(f)
            self.is_trained = True
            return True
        return False


# グローバルインスタンス
predictor = SalaryPredictor()


def train_model(db_name=None):
    """モデル訓練のヘルパー関数"""
    return predictor.train(db_name)


def predict_salary(industry, location, wage_type="monthly"):
    """給与予測のヘルパー関数"""
    return predictor.predict(industry, location, wage_type)


if __name__ == "__main__":
    # テスト実行
    print("🤖 給与予測モデル訓練開始")
    result = train_model()
    print(result)

    if result["success"]:
        print("\n🔮 予測テスト:")
        pred = predict_salary("IT・エンジニア", "東京都", "monthly")
        print(f"  IT・エンジニア @東京都: {pred}")
