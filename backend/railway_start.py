#!/usr/bin/env python3
"""
Railway用の起動スクリプト
ポート設定の問題を解決するためのPythonスクリプト
"""

import os
import sys
import subprocess

def main():
    print("Railway Python起動スクリプト開始")
    
    # 環境変数の確認
    port = os.getenv('PORT', '8000')
    pythonpath = os.getenv('PYTHONPATH', '/app')
    upload_dir = os.getenv('UPLOAD_DIR', '/app/uploaded_pdfs')
    
    print(f"環境変数確認:")
    print(f"PORT: {port}")
    print(f"PYTHONPATH: {pythonpath}")
    print(f"UPLOAD_DIR: {upload_dir}")
    
    # アップロードディレクトリの作成
    try:
        os.makedirs(upload_dir, exist_ok=True)
        print(f"アップロードディレクトリ作成: {upload_dir}")
    except Exception as e:
        print(f"アップロードディレクトリ作成エラー: {e}")
    
    # uvicornコマンドの構築
    cmd = [
        sys.executable, '-m', 'uvicorn',
        'main:app',
        '--host', '0.0.0.0',
        '--port', str(port),
        '--workers', '1'
    ]
    
    print(f"実行コマンド: {' '.join(cmd)}")
    print("アプリケーション起動中...")
    
    # アプリケーション起動
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"アプリケーション起動エラー: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("アプリケーション停止")
        sys.exit(0)

if __name__ == "__main__":
    main() 