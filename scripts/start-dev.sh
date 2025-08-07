#!/bin/bash

# 開発環境起動スクリプト

echo "=== 開発環境起動 ==="

# 環境変数ファイルの確認
if [ ! -f ".env" ]; then
    echo "警告: .envファイルが見つかりません"
    echo "env.development.exampleを.envにコピーしてください"
    echo "cp env.development.example .env"
    exit 1
fi

# 仮想環境の確認
if [ ! -d "venv" ]; then
    echo "仮想環境を作成中..."
    python3 -m venv venv
fi

# 仮想環境のアクティベート
echo "仮想環境をアクティベート中..."
source venv/bin/activate

# 依存関係のインストール
echo "依存関係をインストール中..."
pip install -r requirements.txt

# 開発用ディレクトリの作成
echo "開発用ディレクトリを作成中..."
mkdir -p dev_uploaded_pdfs

# データベースの初期化
echo "データベースを初期化中..."
cd backend
python -c "import database; database.init_db()"

# 開発環境設定の確認
echo "開発環境設定を確認中..."
python -c "from config import config; print(f'環境: {config.__class__.__name__}'); config.validate()"

# アプリケーション起動
echo "開発サーバーを起動中..."
echo "フロントエンド: http://localhost:3000"
echo "バックエンド: http://localhost:8001"
echo "API ドキュメント: http://localhost:8001/docs"
echo ""
echo "Ctrl+C で停止"

uvicorn main:app --reload --host 0.0.0.0 --port 8001
