#!/usr/bin/env python3
"""
Railway用の直接起動スクリプト
環境変数の問題を回避するための直接的なアプローチ
"""

import os
import sys
import uvicorn

def main():
    print("Railway直接起動スクリプト開始")
    
    # 環境変数の確認と設定
    port = int(os.getenv('PORT', '8000'))
    upload_dir = os.getenv('UPLOAD_DIR', '/app/uploaded_pdfs')
    
    print(f"環境変数確認:")
    print(f"PORT: {port}")
    print(f"UPLOAD_DIR: {upload_dir}")
    
    # アップロードディレクトリの作成
    try:
        os.makedirs(upload_dir, exist_ok=True)
        print(f"アップロードディレクトリ作成: {upload_dir}")
    except Exception as e:
        print(f"アップロードディレクトリ作成エラー: {e}")
    
    print("アプリケーション起動中...")
    print(f"使用ポート: {port}")
    
    # 直接uvicornを起動
    try:
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=port,
            workers=1,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("アプリケーション停止")
        sys.exit(0)
    except Exception as e:
        print(f"アプリケーション起動エラー: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 