#!/usr/bin/env python3
"""
Railway用の最終解決スクリプト
$PORT文字列の問題を完全に解決
"""

import os
import sys
import uvicorn

def main():
    print("=" * 80)
    print("RAILWAY最終解決スクリプト開始")
    print("=" * 80)
    
    # 環境変数の詳細確認
    port_raw = os.environ.get('PORT')
    print(f"PORT (raw): '{port_raw}'")
    print(f"PORT type: {type(port_raw)}")
    
    # $PORT文字列の問題を解決
    if port_raw == '$PORT' or port_raw is None:
        print("PORT環境変数が$PORT文字列またはNoneです")
        print("デフォルトポート8000を使用します")
        port = 8000
    else:
        try:
            port = int(port_raw)
            print(f"PORT変換成功: {port}")
        except ValueError as e:
            print(f"PORT変換エラー: {e}")
            print("デフォルトポート8000を使用します")
            port = 8000
    
    # 環境変数を明示的に設定
    os.environ['PORT'] = str(port)
    os.environ.setdefault('PYTHONPATH', '/app')
    os.environ.setdefault('UPLOAD_DIR', '/app/uploaded_pdfs')
    
    print(f"最終的なPORT設定: {port}")
    print(f"PYTHONPATH: {os.environ.get('PYTHONPATH')}")
    print(f"UPLOAD_DIR: {os.environ.get('UPLOAD_DIR')}")
    
    # アップロードディレクトリの作成
    upload_dir = os.environ.get('UPLOAD_DIR', '/app/uploaded_pdfs')
    try:
        os.makedirs(upload_dir, exist_ok=True)
        print(f"アップロードディレクトリ作成: {upload_dir}")
    except Exception as e:
        print(f"アップロードディレクトリ作成エラー: {e}")
    
    print("アプリケーション起動中...")
    
    # アプリケーション起動
    try:
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=port,
            log_level="info"
        )
    except Exception as e:
        print(f"アプリケーション起動エラー: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main() 