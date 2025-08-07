#!/usr/bin/env python3
"""
ローカルのデータベースを本番環境に同期するスクリプト
"""

import sqlite3
import requests
import json
from pathlib import Path
from typing import List, Dict

# 設定
PRODUCTION_API_URL = "https://testprjv2-backend.onrender.com"
LOCAL_DB_PATH = "backend/pdfs.db"

def get_local_pdfs() -> List[Dict]:
    """ローカルデータベースからPDF情報を取得"""
    try:
        conn = sqlite3.connect(LOCAL_DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, url, school, subject, year, filename, created_at
            FROM pdfs
            ORDER BY id
        """)
        
        pdfs = []
        for row in cursor.fetchall():
            pdfs.append({
                'id': row[0],
                'url': row[1],
                'school': row[2],
                'subject': row[3],
                'year': row[4],
                'filename': row[5],
                'created_at': row[6]
            })
        
        conn.close()
        return pdfs
    except Exception as e:
        print(f"ローカルデータベース読み込みエラー: {e}")
        return []

def get_production_pdfs() -> List[Dict]:
    """本番環境からPDF情報を取得"""
    try:
        response = requests.get(f"{PRODUCTION_API_URL}/pdfs/", timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"本番環境PDF取得エラー: {e}")
        return []

def upload_pdf_to_production(pdf_data: Dict, pdf_file_path: Path) -> bool:
    """PDFファイルを本番環境にアップロード"""
    try:
        if not pdf_file_path.exists():
            print(f"ファイルが存在しません: {pdf_file_path}")
            return False
        
        with open(pdf_file_path, 'rb') as f:
            files = {'file': (pdf_data['filename'], f, 'application/pdf')}
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
                print(f"✅ アップロード成功: {pdf_data['filename']} (ID: {result.get('id', 'N/A')})")
                return True
            else:
                print(f"❌ アップロードエラー: {pdf_data['filename']} - {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ アップロードエラー: {pdf_data['filename']} - {e}")
        return False

def main():
    """メイン処理"""
    print("=== データベース本番環境同期開始 ===")
    print(f"本番環境URL: {PRODUCTION_API_URL}")
    print(f"ローカルDB: {LOCAL_DB_PATH}")
    
    # ローカルPDF情報を取得
    local_pdfs = get_local_pdfs()
    print(f"ローカルPDF数: {len(local_pdfs)}")
    
    if not local_pdfs:
        print("ローカルにPDFデータがありません")
        return
    
    # 本番環境PDF情報を取得
    production_pdfs = get_production_pdfs()
    print(f"本番環境PDF数: {len(production_pdfs)}")
    
    # 本番環境の既存ファイル名一覧
    production_filenames = [pdf['filename'] for pdf in production_pdfs]
    
    # アップロード対象を特定
    upload_targets = []
    for pdf in local_pdfs:
        if pdf['filename'] not in production_filenames:
            upload_targets.append(pdf)
    
    print(f"アップロード対象: {len(upload_targets)}個")
    
    if not upload_targets:
        print("アップロードする新しいPDFファイルがありません")
        return
    
    # プレビュー表示
    print("\n=== アップロード予定ファイル ===")
    for i, pdf in enumerate(upload_targets[:5], 1):
        print(f"{i}. {pdf['filename']}")
        print(f"   学校: {pdf['school']}, 科目: {pdf['subject']}, 年度: {pdf['year']}")
    
    if len(upload_targets) > 5:
        print(f"... 他 {len(upload_targets) - 5} ファイル")
    
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
        
        # PDFファイルパスを構築
        pdf_file_path = Path("backend/uploaded_pdfs") / pdf['filename']
        
        if upload_pdf_to_production(pdf, pdf_file_path):
            success_count += 1
        else:
            error_count += 1
        
        # 間隔を空ける
        if i < len(upload_targets):
            import time
            time.sleep(1)
    
    # 結果表示
    print(f"\n=== 同期完了 ===")
    print(f"成功: {success_count}個")
    print(f"エラー: {error_count}個")
    print(f"合計: {len(upload_targets)}個")

if __name__ == "__main__":
    main()
