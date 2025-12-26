# backend/test/test_ml_predictor.py
"""
ML給与予測モデルのテスト
"""
import pytest
import os
import tempfile
from ml_predictor import SalaryPredictor, ML_AVAILABLE


class TestSalaryPredictor:
    """SalaryPredictorクラスのテスト"""

    def test_predictor_initialization(self):
        """初期化テスト"""
        predictor = SalaryPredictor()
        assert predictor.model is None
        assert predictor.is_trained == False
        assert predictor.encoders == {}

    def test_extract_prefecture(self):
        """都道府県抽出テスト"""
        predictor = SalaryPredictor()

        # 正常系
        assert predictor._extract_prefecture("東京都渋谷区") == "東京都"
        assert predictor._extract_prefecture("大阪府大阪市") == "大阪府"
        assert predictor._extract_prefecture("北海道札幌市") == "北海道"

        # 見つからない場合
        assert predictor._extract_prefecture("不明な場所") == "その他"
        assert predictor._extract_prefecture("") == "その他"
        assert predictor._extract_prefecture(None) == "その他"

    @pytest.mark.skipif(not ML_AVAILABLE, reason="scikit-learn未インストール")
    def test_train_with_insufficient_data(self):
        """データ不足時の訓練テスト"""
        # 空のDBで訓練を試みる
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            temp_db = f.name

        try:
            # 空のDBを作成
            import sqlite3

            conn = sqlite3.connect(temp_db)
            conn.execute(
                """
                CREATE TABLE jobs (
                    id INTEGER PRIMARY KEY,
                    title TEXT,
                    company TEXT,
                    location TEXT,
                    wage_min INTEGER,
                    wage_max INTEGER,
                    wage_type TEXT,
                    industry TEXT,
                    url TEXT
                )
            """
            )
            conn.commit()
            conn.close()

            predictor = SalaryPredictor()
            result = predictor.train(db_name=temp_db)

            assert result["success"] == False
            assert "不足" in result["error"]
        finally:
            os.unlink(temp_db)

    @pytest.mark.skipif(not ML_AVAILABLE, reason="scikit-learn未インストール")
    def test_predict_without_training(self):
        """訓練前の予測テスト"""
        predictor = SalaryPredictor()
        # 保存済みモデルがない状態で予測
        # モデルファイルが存在しない場合のエラーハンドリング
        result = predictor.predict("IT・エンジニア", "東京都", "monthly")

        # モデルがなければエラーまたは失敗
        if not os.path.exists("salary_model.pkl"):
            assert result["success"] == False


class TestMLFunctions:
    """ヘルパー関数のテスト"""

    def test_train_model_import(self):
        """train_model関数のインポートテスト"""
        from ml_predictor import train_model

        assert callable(train_model)

    def test_predict_salary_import(self):
        """predict_salary関数のインポートテスト"""
        from ml_predictor import predict_salary

        assert callable(predict_salary)
