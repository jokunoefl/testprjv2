#!/usr/bin/env python3
"""
Railway用の環境変数明示設定起動スクリプト
環境変数を明示的に設定してから起動
"""

import os
import uvicorn

# 環境変数を明示的に設定
os.environ.setdefault("PORT", "8000")
os.environ.setdefault("PYTHONPATH", "/app")
os.environ.setdefault("UPLOAD_DIR", "/app/uploaded_pdfs")

# ポートを取得
port = int(os.environ["PORT"])
print(f"Railway環境変数起動 - ポート: {port}")
print(f"PYTHONPATH: {os.environ.get('PYTHONPATH')}")
print(f"UPLOAD_DIR: {os.environ.get('UPLOAD_DIR')}")

# アプリケーション起動
uvicorn.run("main:app", host="0.0.0.0", port=port, log_level="info") 