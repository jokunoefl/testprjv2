#!/usr/bin/env python3
"""
ローカルのPDFファイルを本番環境にアップロードするスクリプト
"""

import os
import requests
import json
from pathlib import Path
from typing import List, Dict, Optional

# 設定
PRODUCTION_API_URL = "https://testprjv2-backend.onrender.com"
LOCAL_PDF_DIR = "backend/uploaded_pdfs"
BATCH_SIZE = 5  # 一度にアップロードするファイル数

def get_pdf_files() -> List[Path]:
    """ローカルのPDFファイル一覧を取得"""
    pdf_dir = Path(LOCAL_PDF_DIR)
    if not pdf_dir.exists():
        print(f"エラー: PDFディレクトリが見つかりません: {LOCAL_PDF_DIR}")
        return []
    
    pdf_files = list(pdf_dir.glob("*.pdf"))
    print(f"見つかったPDFファイル数: {len(pdf_files)}")
    return pdf_files

def get_existing_pdfs() -> List[str]:
    """本番環境の既存PDFファイル名一覧を取得"""
    try:
        response = requests.get(f"{PRODUCTION_API_URL}/pdfs/", timeout=30)
        response.raise_for_status()
        existing_pdfs = response.json()
        return [pdf['filename'] for pdf in existing_pdfs]
    except Exception as e:
        print(f"本番環境のPDF一覧取得エラー: {e}")
        return []

def upload_pdf_file(file_path: Path, existing_filenames: List[str]) -> bool:
    """単一のPDFファイルをアップロード"""
    filename = file_path.name
    
    # 既に存在する場合はスキップ
    if filename in existing_filenames:
        print(f"スキップ: {filename} (既に存在)")
        return True
    
    try:
        # ファイル情報を取得
        file_size = file_path.stat().st_size
        print(f"アップロード中: {filename} ({file_size / 1024 / 1024:.1f}MB)")
        
        # ファイルをアップロード
        with open(file_path, 'rb') as f:
            files = {'file': (filename, f, 'application/pdf')}
            data = {
                'url': f'https://example.com/{filename}',  # ダミーURL
                'school': 'ローカルアップロード',
                'subject': 'unknown',
                'year': 2025
            }
            
            response = requests.post(
                f"{PRODUCTION_API_URL}/upload_pdf/",
                files=files,
                data=data,
                timeout=60
            )
            
            if response.status_code == 200:
                print(f"✅ 成功: {filename}")
                return True
            else:
                print(f"❌ エラー: {filename} - {response.status_code}")
                print(f"   レスポンス: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ アップロードエラー: {filename} - {e}")
        return False

def main():
    """メイン処理"""
    print("=== PDFファイル本番環境アップロード開始 ===")
    print(f"本番環境URL: {PRODUCTION_API_URL}")
    print(f"ローカルPDFディレクトリ: {LOCAL_PDF_DIR}")
    
    # ローカルPDFファイル一覧を取得
    pdf_files = get_pdf_files()
    if not pdf_files:
        print("アップロードするPDFファイルが見つかりません")
        return
    
    # 本番環境の既存PDF一覧を取得
    print("本番環境の既存PDF一覧を取得中...")
    existing_pdfs = get_existing_pdfs()
    print(f"本番環境の既存PDF数: {len(existing_pdfs)}")
    
    # アップロード対象ファイルをフィルタリング
    new_pdfs = [f for f in pdf_files if f.name not in existing_pdfs]
    print(f"アップロード対象ファイル数: {len(new_pdfs)}")
    
    if not new_pdfs:
        print("アップロードする新しいPDFファイルがありません")
        return
    
    # 確認
    response = input(f"{len(new_pdfs)}個のPDFファイルをアップロードしますか？ (y/N): ")
    if response.lower() != 'y':
        print("アップロードをキャンセルしました")
        return
    
    # バッチ処理でアップロード
    success_count = 0
    error_count = 0
    
    for i, pdf_file in enumerate(new_pdfs, 1):
        print(f"\n[{i}/{len(new_pdfs)}] 処理中...")
        
        if upload_pdf_file(pdf_file, existing_pdfs):
            success_count += 1
        else:
            error_count += 1
        
        # バッチ間隔を空ける
        if i % BATCH_SIZE == 0 and i < len(new_pdfs):
            print(f"バッチ処理完了。次のバッチまで待機中...")
            import time
            time.sleep(2)
    
    # 結果表示
    print(f"\n=== アップロード完了 ===")
    print(f"成功: {success_count}個")
    print(f"エラー: {error_count}個")
    print(f"合計: {len(new_pdfs)}個")

if __name__ == "__main__":
    main()
