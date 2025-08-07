#!/usr/bin/env python3
"""
Railway用の詳細ログ出力起動スクリプト
最大限のデバッグ情報を出力して問題を特定
"""

import os
import sys
import traceback
import uvicorn

def main():
    print("=" * 80)
    print("RAILWAY詳細ログ出力起動スクリプト開始")
    print("=" * 80)
    
    # システム情報
    print("\n=== システム情報 ===")
    print(f"Python実行パス: {sys.executable}")
    print(f"Pythonバージョン: {sys.version}")
    print(f"現在のディレクトリ: {os.getcwd()}")
    print(f"スクリプトの場所: {__file__}")
    
    # 環境変数の詳細確認
    print("\n=== 環境変数詳細確認 ===")
    port_raw = os.environ.get('PORT')
    print(f"PORT (raw): '{port_raw}'")
    print(f"PORT type: {type(port_raw)}")
    print(f"PORT is None: {port_raw is None}")
    print(f"PORT == '$PORT': {port_raw == '$PORT'}")
    
    if port_raw:
        try:
            port_int = int(port_raw)
            print(f"PORT (int): {port_int}")
        except ValueError as e:
            print(f"PORT変換エラー: {e}")
            print(f"PORTの内容: '{port_raw}'")
            print(f"PORTの長さ: {len(port_raw) if port_raw else 0}")
            print(f"PORTの文字コード: {[ord(c) for c in port_raw] if port_raw else []}")
    
    # その他の重要な環境変数
    print(f"\nPYTHONPATH: '{os.environ.get('PYTHONPATH', 'Not set')}'")
    print(f"UPLOAD_DIR: '{os.environ.get('UPLOAD_DIR', 'Not set')}'")
    print(f"PWD: '{os.environ.get('PWD', 'Not set')}'")
    print(f"PATH: '{os.environ.get('PATH', 'Not set')}'")
    
    # 全ての環境変数を表示
    print("\n=== 全ての環境変数 ===")
    for key, value in sorted(os.environ.items()):
        if 'KEY' in key or 'SECRET' in key or 'PASSWORD' in key:
            print(f"  {key}: [HIDDEN]")
        else:
            print(f"  {key}: '{value}'")
    
    # ファイルシステム確認
    print("\n=== ファイルシステム確認 ===")
    print(f"現在のディレクトリ: {os.getcwd()}")
    try:
        files = os.listdir('.')
        print(f"ファイル一覧 ({len(files)}個):")
        for file in sorted(files):
            if os.path.isfile(file):
                size = os.path.getsize(file)
                print(f"  📄 {file} ({size} bytes)")
            else:
                print(f"  📁 {file}/")
    except Exception as e:
        print(f"ディレクトリ読み取りエラー: {e}")
        traceback.print_exc()
    
    # ポートの設定
    print("\n=== ポート設定 ===")
    if port_raw and port_raw != '$PORT':
        try:
            port = int(port_raw)
            print(f"使用ポート: {port}")
        except ValueError as e:
            print(f"ポート変換エラー: {e}")
            port = 8000
            print(f"デフォルトポートを使用: {port}")
    else:
        port = 8000
        print(f"PORT環境変数が無効、デフォルトポートを使用: {port}")
    
    # アップロードディレクトリの作成
    print("\n=== アップロードディレクトリ作成 ===")
    upload_dir = os.environ.get('UPLOAD_DIR', '/app/uploaded_pdfs')
    try:
        os.makedirs(upload_dir, exist_ok=True)
        print(f"アップロードディレクトリ作成: {upload_dir}")
        print(f"ディレクトリ存在: {os.path.exists(upload_dir)}")
        print(f"ディレクトリ書き込み権限: {os.access(upload_dir, os.W_OK)}")
    except Exception as e:
        print(f"アップロードディレクトリ作成エラー: {e}")
        traceback.print_exc()
    
    # uvicornのインポートテスト
    print("\n=== uvicornインポートテスト ===")
    try:
        import uvicorn
        print("uvicornインポート成功")
        print(f"uvicornバージョン: {uvicorn.__version__}")
    except ImportError as e:
        print(f"uvicornインポートエラー: {e}")
        traceback.print_exc()
        return
    
    # mainモジュールのインポートテスト
    print("\n=== mainモジュールインポートテスト ===")
    try:
        import main
        print("mainモジュールインポート成功")
        print(f"main.app type: {type(main.app)}")
    except ImportError as e:
        print(f"mainモジュールインポートエラー: {e}")
        traceback.print_exc()
        return
    except Exception as e:
        print(f"mainモジュール読み込みエラー: {e}")
        traceback.print_exc()
        return
    
    # アプリケーション起動
    print("\n=== アプリケーション起動 ===")
    print(f"起動コマンド: uvicorn.run('main:app', host='0.0.0.0', port={port}, log_level='info')")
    
    try:
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=port,
            log_level="info"
        )
    except Exception as e:
        print(f"アプリケーション起動エラー: {e}")
        print(f"エラータイプ: {type(e)}")
        traceback.print_exc()
        return

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"予期しないエラー: {e}")
        traceback.print_exc()
        sys.exit(1) 