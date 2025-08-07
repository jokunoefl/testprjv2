#!/usr/bin/env python3
"""
本番環境のデータベースをリセットして、ローカルのPDFファイルを新しくアップロードするスクリプト
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

def upload_pdf_file(file_path: Path, index: int) -> bool:
    """PDFファイルを本番環境にアップロード"""
    try:
        filename = file_path.name
        print(f"📤 アップロード中 [{index}]: {filename}")
        
        # ファイルサイズを確認
        file_size = file_path.stat().st_size
        print(f"   ファイルサイズ: {file_size / 1024 / 1024:.1f}MB")
        
        # ファイル名から学校名と科目を推測
        school = "早稲田中学校"  # デフォルト
        subject = "unknown"
        year = 2025
        
        if "kokugo" in filename.lower():
            subject = "japanese"
        elif "sansu" in filename.lower() or "math" in filename.lower():
            subject = "math"
        elif "rika" in filename.lower() or "science" in filename.lower():
            subject = "science"
        elif "syakai" in filename.lower() or "social" in filename.lower():
            subject = "social"
        
        # 年度を推測
        if "2023" in filename:
            year = 2023
        elif "2024" in filename:
            year = 2024
        elif "2025" in filename:
            year = 2025
        
        with open(file_path, 'rb') as f:
            files = {'file': (filename, f, 'application/pdf')}
            data = {
                'url': f'https://www.waseda-h.ed.jp/exam/past_questions/',
                'school': school,
                'subject': subject,
                'year': str(year)
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
    print("=== 本番環境PDFリセット・アップロード開始 ===")
    print(f"本番環境URL: {PRODUCTION_API_URL}")
    print(f"ローカルPDFディレクトリ: {LOCAL_PDF_DIR}")
    
    # ローカルPDFファイル一覧を取得
    local_pdf_files = get_local_pdf_files()
    if not local_pdf_files:
        print("アップロードするPDFファイルが見つかりません")
        return
    
    # 最初の10個のファイルのみをアップロード（テスト用）
    test_files = local_pdf_files[:10]
    print(f"テスト用に最初の{len(test_files)}個のファイルをアップロードします")
    
    # プレビュー表示
    print("\n=== アップロード予定ファイル ===")
    for i, pdf_file in enumerate(test_files, 1):
        file_size = pdf_file.stat().st_size
        print(f"{i}. {pdf_file.name} ({file_size / 1024 / 1024:.1f}MB)")
    
    # 確認
    response = input(f"\n{len(test_files)}個のPDFファイルをアップロードしますか？ (y/N): ")
    if response.lower() != 'y':
        print("アップロードをキャンセルしました")
        return
    
    # アップロード実行
    success_count = 0
    error_count = 0
    
    for i, pdf_file in enumerate(test_files, 1):
        print(f"\n[{i}/{len(test_files)}] 処理中...")
        
        if upload_pdf_file(pdf_file, i):
            success_count += 1
        else:
            error_count += 1
        
        # 間隔を空ける
        if i < len(test_files):
            import time
            time.sleep(5)  # サーバー負荷を考慮して間隔を空ける
    
    # 結果表示
    print(f"\n=== アップロード完了 ===")
    print(f"成功: {success_count}個")
    print(f"エラー: {error_count}個")
    print(f"合計: {len(test_files)}個")
    
    if success_count > 0:
        print(f"\n✅ アップロードが完了しました！")
        print(f"本番環境でPDF表示をテストしてください。")

if __name__ == "__main__":
    main()
