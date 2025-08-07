#!/usr/bin/env python3
"""
本番環境のPDFデータを正しい学校名で更新するスクリプト
"""

import requests
import sqlite3
import os
from pathlib import Path
from typing import List, Dict

# 設定
PRODUCTION_API_URL = "https://testprjv2-backend.onrender.com"
LOCAL_DB_PATH = "../backend/pdfs.db"

def get_local_pdf_data() -> List[Dict]:
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

def update_pdf_metadata(pdf_id: int, metadata: Dict) -> bool:
    """PDFのメタデータを更新"""
    try:
        response = requests.put(
            f"{PRODUCTION_API_URL}/pdfs/{pdf_id}",
            json=metadata,
            timeout=30
        )
        
        if response.status_code == 200:
            print(f"✅ 更新成功: ID {pdf_id} - {metadata['school']}")
            return True
        else:
            print(f"❌ 更新エラー: ID {pdf_id} - {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 更新エラー: ID {pdf_id} - {e}")
        return False

def main():
    """メイン処理"""
    print("=== 本番環境PDF学校名修正開始 ===")
    print(f"本番環境URL: {PRODUCTION_API_URL}")
    print(f"ローカルDB: {LOCAL_DB_PATH}")
    
    # ローカルPDF情報を取得
    local_pdfs = get_local_pdf_data()
    print(f"ローカルPDF数: {len(local_pdfs)}")
    
    if not local_pdfs:
        print("ローカルにPDFデータがありません")
        return
    
    # 本番環境のPDF情報を取得
    try:
        response = requests.get(f"{PRODUCTION_API_URL}/pdfs/", timeout=30)
        response.raise_for_status()
        production_pdfs = response.json()
        print(f"本番環境PDF数: {len(production_pdfs)}")
    except Exception as e:
        print(f"本番環境PDF取得エラー: {e}")
        return
    
    # ファイル名でマッチングして更新
    update_count = 0
    error_count = 0
    
    for local_pdf in local_pdfs:
        # 本番環境で同じファイル名のPDFを探す
        matching_pdf = None
        for prod_pdf in production_pdfs:
            if prod_pdf['filename'] == local_pdf['filename']:
                matching_pdf = prod_pdf
                break
        
        if matching_pdf:
            # メタデータを更新
            metadata = {
                'school': local_pdf['school'],
                'subject': local_pdf['subject'],
                'year': local_pdf['year'],
                'url': local_pdf['url']
            }
            
            if update_pdf_metadata(matching_pdf['id'], metadata):
                update_count += 1
            else:
                error_count += 1
        else:
            print(f"⚠️  マッチするPDFが見つかりません: {local_pdf['filename']}")
    
    # 結果表示
    print(f"\n=== 更新完了 ===")
    print(f"成功: {update_count}個")
    print(f"エラー: {error_count}個")
    print(f"合計: {len(local_pdfs)}個")
    
    if update_count > 0:
        print(f"\n✅ 学校名の修正が完了しました！")
        print(f"本番環境で学校一覧を確認してください。")

if __name__ == "__main__":
    main()
