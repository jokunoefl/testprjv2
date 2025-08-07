#!/usr/bin/env python3
"""
Railway環境変数デバッグスクリプト
環境変数の問題を調査するためのデバッグツール
"""

import os
import sys

def main():
    print("=== Railway環境変数デバッグ ===")
    
    # 全ての環境変数を表示
    print("全ての環境変数:")
    for key, value in os.environ.items():
        print(f"  {key}: {value}")
    
    print("\n=== 重要な環境変数 ===")
    
    # PORT環境変数の詳細確認
    port_raw = os.environ.get('PORT')
    print(f"PORT (raw): '{port_raw}'")
    print(f"PORT type: {type(port_raw)}")
    
    if port_raw:
        try:
            port_int = int(port_raw)
            print(f"PORT (int): {port_int}")
        except ValueError as e:
            print(f"PORT変換エラー: {e}")
    else:
        print("PORT環境変数が設定されていません")
    
    # その他の重要な環境変数
    print(f"PYTHONPATH: {os.environ.get('PYTHONPATH', 'Not set')}")
    print(f"UPLOAD_DIR: {os.environ.get('UPLOAD_DIR', 'Not set')}")
    print(f"PWD: {os.environ.get('PWD', 'Not set')}")
    print(f"PATH: {os.environ.get('PATH', 'Not set')}")
    
    print("\n=== ファイルシステム確認 ===")
    print(f"現在のディレクトリ: {os.getcwd()}")
    print(f"ファイル一覧:")
    try:
        for file in os.listdir('.'):
            print(f"  {file}")
    except Exception as e:
        print(f"ディレクトリ読み取りエラー: {e}")
    
    print("\n=== テスト実行 ===")
    
    # ポートのテスト
    test_port = os.environ.get('PORT', '8000')
    print(f"テストポート: {test_port}")
    
    try:
        test_port_int = int(test_port)
        print(f"ポート変換成功: {test_port_int}")
        
        # uvicornのテストインポート
        try:
            import uvicorn
            print("uvicornインポート成功")
            
            # mainモジュールのテストインポート
            try:
                import main
                print("mainモジュールインポート成功")
                
                print("=== 起動テスト ===")
                print("uvicorn.run()を実行します...")
                uvicorn.run(
                    "main:app",
                    host="0.0.0.0",
                    port=test_port_int,
                    log_level="info"
                )
                
            except ImportError as e:
                print(f"mainモジュールインポートエラー: {e}")
                
        except ImportError as e:
            print(f"uvicornインポートエラー: {e}")
            
    except ValueError as e:
        print(f"ポート変換エラー: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 