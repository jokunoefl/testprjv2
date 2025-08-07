#!/bin/bash

# 本番環境起動スクリプト

echo "=== 本番環境起動 ==="

# 環境変数の確認
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "エラー: ANTHROPIC_API_KEYが設定されていません"
    exit 1
fi

if [ -z "$SECRET_KEY" ]; then
    echo "エラー: SECRET_KEYが設定されていません"
    exit 1
fi

# 環境変数の設定
export ENVIRONMENT=production

# 本番用ディレクトリの作成
echo "本番用ディレクトリを作成中..."
mkdir -p /app/uploaded_pdfs

# データベースの初期化
echo "データベースを初期化中..."
cd backend
python -c "import database; database.init_db()"

# 本番環境設定の確認
echo "本番環境設定を確認中..."
python -c "from config import config; print(f'環境: {config.__class__.__name__}'); config.validate()"

# アプリケーション起動
echo "本番サーバーを起動中..."
echo "ポート: $PORT"

uvicorn main:app --host 0.0.0.0 --port $PORT
