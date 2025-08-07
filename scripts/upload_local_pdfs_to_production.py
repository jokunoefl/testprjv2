#!/usr/bin/env python3
"""
ローカルのPDFファイルを本番環境に直接アップロードするスクリプト
"""

import requests
import os
from pathlib import Path
from typing import List, Dict

# 設定
PRODUCTION_API_URL = "https://testprjv2-backend.onrender.com"
LOCAL_PDF_DIR = "../backend/uploaded_pdfs"

def get_local_pdf_files() -> List[Path]:
    """ローカルのPDFファイル一覧を取得"""
    pdf_dir = Path(LOCAL_PDF_DIR)
    if not pdf_dir.exists():
        print(f"ローカルPDFディレクトリが存在しません: {LOCAL_PDF_DIR}")
        return []
    
    pdf_files = list(pdf_dir.glob("*.pdf"))
    print(f"ローカルPDFファイル数: {len(pdf_files)}")
    return pdf_files

def get_production_pdfs() -> List[Dict]:
    """本番環境からPDF情報を取得"""
    try:
        response = requests.get(f"{PRODUCTION_API_URL}/pdfs/", timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"本番環境PDF取得エラー: {e}")
        return []

def upload_pdf_file(file_path: Path) -> bool:
    """PDFファイルを本番環境にアップロード"""
    try:
        filename = file_path.name
        print(f"📤 アップロード中: {filename}")
        
        # ファイルサイズを確認
        file_size = file_path.stat().st_size
        print(f"   ファイルサイズ: {file_size / 1024 / 1024:.1f}MB")
        
        with open(file_path, 'rb') as f:
            files = {'file': (filename, f, 'application/pdf')}
            data = {
                'url': f'https://example.com/{filename}',  # ダミーURL
                'school': 'ローカルアップロード',
                'subject': 'unknown',
                'year': '2025'
            }
            
            response = requests.post(
                f"{PRODUCTION_API_URL}/upload_pdf/",
                files=files,
                data=data,
                timeout=120  # 大きなファイル用にタイムアウトを延長
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ アップロード成功: {filename} (ID: {result.get('id', 'N/A')})")
                return True
            else:
                print(f"❌ アップロードエラー: {filename} - {response.status_code}")
                print(f"   レスポンス: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ アップロードエラー: {filename} - {e}")
        return False

def main():
    """メイン処理"""
    print("=== ローカルPDF本番環境アップロード開始 ===")
    print(f"本番環境URL: {PRODUCTION_API_URL}")
    print(f"ローカルPDFディレクトリ: {LOCAL_PDF_DIR}")
    
    # ローカルPDFファイル一覧を取得
    local_pdf_files = get_local_pdf_files()
    if not local_pdf_files:
        print("アップロードするPDFファイルが見つかりません")
        return
    
    # 本番環境の既存PDF一覧を取得
    production_pdfs = get_production_pdfs()
    production_filenames = [pdf['filename'] for pdf in production_pdfs]
    print(f"本番環境既存PDF数: {len(production_pdfs)}")
    
    # アップロード対象を特定（既に存在しないファイル）
    upload_targets = []
    for pdf_file in local_pdf_files:
        if pdf_file.name not in production_filenames:
            upload_targets.append(pdf_file)
    
    print(f"アップロード対象: {len(upload_targets)}個")
    
    if not upload_targets:
        print("アップロードする新しいPDFファイルがありません")
        return
    
    # プレビュー表示
    print("\n=== アップロード予定ファイル ===")
    for i, pdf_file in enumerate(upload_targets[:10], 1):
        file_size = pdf_file.stat().st_size
        print(f"{i}. {pdf_file.name} ({file_size / 1024 / 1024:.1f}MB)")
    
    if len(upload_targets) > 10:
        print(f"... 他 {len(upload_targets) - 10} ファイル")
    
    # 確認
    response = input(f"\n{len(upload_targets)}個のPDFファイルをアップロードしますか？ (y/N): ")
    if response.lower() != 'y':
        print("アップロードをキャンセルしました")
        return
    
    # アップロード実行
    success_count = 0
    error_count = 0
    
    for i, pdf_file in enumerate(upload_targets, 1):
        print(f"\n[{i}/{len(upload_targets)}] 処理中...")
        
        if upload_pdf_file(pdf_file):
            success_count += 1
        else:
            error_count += 1
        
        # 間隔を空ける
        if i < len(upload_targets):
            import time
            time.sleep(3)  # サーバー負荷を考慮して間隔を空ける
    
    # 結果表示
    print(f"\n=== アップロード完了 ===")
    print(f"成功: {success_count}個")
    print(f"エラー: {error_count}個")
    print(f"合計: {len(upload_targets)}個")

if __name__ == "__main__":
    main()
