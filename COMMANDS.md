# 🚀 プロジェクト実行コマンド一覧

このプロジェクトをローカル環境で実行するための手順とコマンドです。
ターミナルを 2 つ開き、Frontend と Backend を並行して実行してください。

## 1. Backend (API サーバー)

**セットアップと起動**

```bash
# `backend` ディレクトリへ移動
cd backend

# 仮想環境の作成（初回のみ）
python3 -m venv .venv

# 仮想環境のアクティベート
source .venv/bin/activate

# 依存パッケージのインストール（初回のみ）
pip install -r requirements.txt

# サーバー起動 (http://127.0.0.1:5000)
python3 app.py
```

**その他のコマンド**

```bash
# クローラーの手動実行 (北海道の求人を3ページ分収集)
python3 crawler.py 北海道 3

# テスト実行
pytest
```

## 2. Frontend (UI)

**セットアップと起動**

```bash
# `frontend` ディレクトリへ移動
cd frontend

# 依存パッケージのインストール（初回のみ）
npm install

# 開発サーバー起動 (http://localhost:5173)
npm run dev
```

---

### ブラウザでアクセス

起動後、ブラウザで以下の URL にアクセスしてください。
👉 [http://localhost:5173](http://localhost:5173)
