from flask import Flask
from flask_cors import CORS
from routes.jobs import jobs_bp
from routes.analysis import analysis_bp
from routes.crawler import crawler_bp
from routes.ml import ml_bp

app = Flask(__name__)
# Vue(localhost:5173) からのアクセスを許可する設定
CORS(app)

# Register Blueprints
app.register_blueprint(jobs_bp)
app.register_blueprint(analysis_bp)
app.register_blueprint(crawler_bp)
app.register_blueprint(ml_bp)

if __name__ == "__main__":
    # スケジューラーを開始
    from scheduler import start_scheduler

    start_scheduler()
    app.run(debug=True, port=5000)
