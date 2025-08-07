#!/usr/bin/env python3
"""
PDFファイル名からメタデータを抽出して本番環境にアップロードするスクリプト
"""

import os
import re
import requests
from pathlib import Path
from typing import List, Dict, Optional, Tuple

# 設定
PRODUCTION_API_URL = "https://testprjv2-backend.onrender.com"
LOCAL_PDF_DIR = "backend/uploaded_pdfs"

def extract_metadata_from_filename(filename: str) -> Dict[str, str]:
    """ファイル名からメタデータを抽出"""
    metadata = {
        'school': '不明',
        'subject': 'unknown',
        'year': 2025,
        'url': f'https://example.com/{filename}'
    }
    
    # ファイル名のパターンマッチング
    filename_lower = filename.lower()
    
    # 年度の抽出
    year_match = re.search(r'20(\d{2})', filename)
    if year_match:
        metadata['year'] = int(f"20{year_match.group(1)}")
    
    # 科目の抽出
    if 'kokugo' in filename_lower or 'ja' in filename_lower:
        metadata['subject'] = 'japanese'
    elif 'math' in filename_lower or 'sansu' in filename_lower:
        metadata['subject'] = 'math'
    elif 'sci' in filename_lower or 'rika' in filename_lower:
        metadata['subject'] = 'science'
    elif 'social' in filename_lower or 'syakai' in filename_lower:
        metadata['subject'] = 'social'
    
    # 学校名の抽出
    if 'waseda' in filename_lower:
        metadata['school'] = '早稲田中学校'
    elif 'junior' in filename_lower:
        metadata['school'] = 'ジュニア中学校'
    elif '帰国生' in filename:
        metadata['school'] = '帰国生対象校'
    else:
        metadata['school'] = 'その他中学校'
    
    return metadata

def get_subject_label(subject: str) -> str:
    """科目コードを日本語ラベルに変換"""
    labels = {
        'japanese': '国語',
        'math': '算数',
        'science': '理科',
        'social': '社会',
        'unknown': '不明'
    }
    return labels.get(subject, subject)

def upload_pdf_with_metadata(file_path: Path, existing_filenames: List[str]) -> bool:
    """メタデータ付きでPDFファイルをアップロード"""
    filename = file_path.name
    
    # 既に存在する場合はスキップ
    if filename in existing_filenames:
        print(f"スキップ: {filename} (既に存在)")
        return True
    
    try:
        # メタデータを抽出
        metadata = extract_metadata_from_filename(filename)
        file_size = file_path.stat().st_size
        
        print(f"アップロード中: {filename}")
        print(f"  学校: {metadata['school']}")
        print(f"  科目: {get_subject_label(metadata['subject'])}")
        print(f"  年度: {metadata['year']}")
        print(f"  サイズ: {file_size / 1024 / 1024:.1f}MB")
        
        # ファイルをアップロード
        with open(file_path, 'rb') as f:
            files = {'file': (filename, f, 'application/pdf')}
            data = {
                'url': metadata['url'],
                'school': metadata['school'],
                'subject': metadata['subject'],
                'year': str(metadata['year'])
            }
            
            response = requests.post(
                f"{PRODUCTION_API_URL}/upload_pdf/",
                files=files,
                data=data,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 成功: {filename} (ID: {result.get('id', 'N/A')})")
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
    print("=== PDFファイル本番環境アップロード（メタデータ付き）===")
    print(f"本番環境URL: {PRODUCTION_API_URL}")
    print(f"ローカルPDFディレクトリ: {LOCAL_PDF_DIR}")
    
    # ローカルPDFファイル一覧を取得
    pdf_dir = Path(LOCAL_PDF_DIR)
    if not pdf_dir.exists():
        print(f"エラー: PDFディレクトリが見つかりません: {LOCAL_PDF_DIR}")
        return
    
    pdf_files = list(pdf_dir.glob("*.pdf"))
    print(f"見つかったPDFファイル数: {len(pdf_files)}")
    
    if not pdf_files:
        print("アップロードするPDFファイルが見つかりません")
        return
    
    # 本番環境の既存PDF一覧を取得
    print("本番環境の既存PDF一覧を取得中...")
    try:
        response = requests.get(f"{PRODUCTION_API_URL}/pdfs/", timeout=30)
        response.raise_for_status()
        existing_pdfs = response.json()
        existing_filenames = [pdf['filename'] for pdf in existing_pdfs]
        print(f"本番環境の既存PDF数: {len(existing_pdfs)}")
    except Exception as e:
        print(f"本番環境のPDF一覧取得エラー: {e}")
        existing_filenames = []
    
    # アップロード対象ファイルをフィルタリング
    new_pdfs = [f for f in pdf_files if f.name not in existing_filenames]
    print(f"アップロード対象ファイル数: {len(new_pdfs)}")
    
    if not new_pdfs:
        print("アップロードする新しいPDFファイルがありません")
        return
    
    # プレビュー表示
    print("\n=== アップロード予定ファイル ===")
    for i, pdf_file in enumerate(new_pdfs[:5], 1):  # 最初の5件を表示
        metadata = extract_metadata_from_filename(pdf_file.name)
        print(f"{i}. {pdf_file.name}")
        print(f"   学校: {metadata['school']}, 科目: {get_subject_label(metadata['subject'])}, 年度: {metadata['year']}")
    
    if len(new_pdfs) > 5:
        print(f"... 他 {len(new_pdfs) - 5} ファイル")
    
    # 確認
    response = input(f"\n{len(new_pdfs)}個のPDFファイルをアップロードしますか？ (y/N): ")
    if response.lower() != 'y':
        print("アップロードをキャンセルしました")
        return
    
    # アップロード実行
    success_count = 0
    error_count = 0
    
    for i, pdf_file in enumerate(new_pdfs, 1):
        print(f"\n[{i}/{len(new_pdfs)}] 処理中...")
        
        if upload_pdf_with_metadata(pdf_file, existing_filenames):
            success_count += 1
        else:
            error_count += 1
        
        # 間隔を空ける
        if i < len(new_pdfs):
            import time
            time.sleep(1)
    
    # 結果表示
    print(f"\n=== アップロード完了 ===")
    print(f"成功: {success_count}個")
    print(f"エラー: {error_count}個")
    print(f"合計: {len(new_pdfs)}個")

if __name__ == "__main__":
    main()
