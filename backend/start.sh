#!/bin/bash

echo "Railway起動スクリプト開始"
echo "環境変数確認:"
echo "PORT: $PORT"
echo "PYTHONPATH: $PYTHONPATH"
echo "UPLOAD_DIR: $UPLOAD_DIR"

# ポートのデフォルト値を設定
PORT=${PORT:-8000}

# アップロードディレクトリの作成
mkdir -p $UPLOAD_DIR

# アプリケーション起動
echo "アプリケーション起動中..."
echo "使用ポート: $PORT"
exec uvicorn main:app --host 0.0.0.0 --port $PORT --workers 1 