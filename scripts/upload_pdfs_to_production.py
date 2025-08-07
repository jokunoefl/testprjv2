#!/usr/bin/env python3
"""
本番環境にPDFファイルをアップロードするスクリプト
"""

import requests
import json
import os
from pathlib import Path
from typing import List, Dict

# 設定
PRODUCTION_API_URL = "https://testprjv2-backend.onrender.com"
LOCAL_PDF_DIR = "../backend/uploaded_pdfs"

def get_production_pdfs() -> List[Dict]:
    """本番環境からPDF情報を取得"""
    try:
        response = requests.get(f"{PRODUCTION_API_URL}/pdfs/", timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"本番環境PDF取得エラー: {e}")
        return []

def upload_pdf_file(filename: str, pdf_data: Dict) -> bool:
    """PDFファイルを本番環境にアップロード"""
    try:
        pdf_file_path = Path(LOCAL_PDF_DIR) / filename
        
        if not pdf_file_path.exists():
            print(f"❌ ファイルが存在しません: {filename}")
            return False
        
        print(f"📤 アップロード中: {filename}")
        
        with open(pdf_file_path, 'rb') as f:
            files = {'file': (filename, f, 'application/pdf')}
            data = {
                'url': pdf_data['url'],
                'school': pdf_data['school'],
                'subject': pdf_data['subject'],
                'year': str(pdf_data['year'])
            }
            
            response = requests.post(
                f"{PRODUCTION_API_URL}/upload_pdf/",
                files=files,
                data=data,
                timeout=60
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
    print("=== PDF本番環境アップロード開始 ===")
    print(f"本番環境URL: {PRODUCTION_API_URL}")
    print(f"ローカルPDFディレクトリ: {LOCAL_PDF_DIR}")
    
    # 本番環境のPDF情報を取得
    production_pdfs = get_production_pdfs()
    print(f"本番環境PDF数: {len(production_pdfs)}")
    
    if not production_pdfs:
        print("本番環境にPDFデータがありません")
        return
    
    # 本番環境の既存ファイル名一覧
    production_filenames = [pdf['filename'] for pdf in production_pdfs]
    
    # ローカルのPDFファイル一覧
    local_pdf_dir = Path(LOCAL_PDF_DIR)
    if not local_pdf_dir.exists():
        print(f"ローカルPDFディレクトリが存在しません: {LOCAL_PDF_DIR}")
        return
    
    local_files = [f.name for f in local_pdf_dir.glob("*.pdf")]
    print(f"ローカルPDFファイル数: {len(local_files)}")
    
    # アップロード対象を特定（本番環境に存在しないファイル）
    upload_targets = []
    for pdf in production_pdfs:
        if pdf['filename'] in local_files and pdf['filename'] not in production_filenames:
            upload_targets.append(pdf)
    
    # または、最初の5つのファイルをテスト用にアップロード
    if not upload_targets:
        print("既存ファイルのアップロード対象がありません。テスト用に最初の5つのファイルをアップロードします。")
        upload_targets = production_pdfs[:5]
    
    print(f"アップロード対象: {len(upload_targets)}個")
    
    # プレビュー表示
    print("\n=== アップロード予定ファイル ===")
    for i, pdf in enumerate(upload_targets, 1):
        print(f"{i}. {pdf['filename']}")
        print(f"   学校: {pdf['school']}, 科目: {pdf['subject']}, 年度: {pdf['year']}")
    
    # 確認
    response = input(f"\n{len(upload_targets)}個のPDFファイルをアップロードしますか？ (y/N): ")
    if response.lower() != 'y':
        print("アップロードをキャンセルしました")
        return
    
    # アップロード実行
    success_count = 0
    error_count = 0
    
    for i, pdf in enumerate(upload_targets, 1):
        print(f"\n[{i}/{len(upload_targets)}] 処理中...")
        
        if upload_pdf_file(pdf['filename'], pdf):
            success_count += 1
        else:
            error_count += 1
        
        # 間隔を空ける
        if i < len(upload_targets):
            import time
            time.sleep(2)
    
    # 結果表示
    print(f"\n=== アップロード完了 ===")
    print(f"成功: {success_count}個")
    print(f"エラー: {error_count}個")
    print(f"合計: {len(upload_targets)}個")

if __name__ == "__main__":
    main()
