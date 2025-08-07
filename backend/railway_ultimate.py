#!/usr/bin/env python3
"""
Railway用の究極起動スクリプト
全ての潜在的な問題を回避する最終手段
"""

import os
import sys
import uvicorn
import traceback

def main():
    print("=" * 80)
    print("RAILWAY究極起動スクリプト開始")
    print("=" * 80)
    
    # システム情報
    print(f"Python実行パス: {sys.executable}")
    print(f"Pythonバージョン: {sys.version}")
    print(f"現在のディレクトリ: {os.getcwd()}")
    
    # 環境変数の強制設定
    print("\n=== 環境変数の強制設定 ===")
    os.environ['PORT'] = '8000'
    os.environ['PYTHONPATH'] = '/app'
    os.environ['UPLOAD_DIR'] = '/app/uploaded_pdfs'
    
    print(f"PORT: {os.environ.get('PORT')}")
    print(f"PYTHONPATH: {os.environ.get('PYTHONPATH')}")
    print(f"UPLOAD_DIR: {os.environ.get('UPLOAD_DIR')}")
    
    # アップロードディレクトリの作成
    print("\n=== アップロードディレクトリ作成 ===")
    try:
        os.makedirs('/app/uploaded_pdfs', exist_ok=True)
        print("アップロードディレクトリ作成完了")
    except Exception as e:
        print(f"アップロードディレクトリ作成エラー: {e}")
        # エラーでも続行
    
    # アプリケーション起動
    print("\n=== アプリケーション起動 ===")
    print("uvicorn.run()を実行します...")
    
    try:
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            log_level="info"
        )
    except Exception as e:
        print(f"アプリケーション起動エラー: {e}")
        print(f"エラータイプ: {type(e)}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"予期しないエラー: {e}")
        traceback.print_exc()
        sys.exit(1) 