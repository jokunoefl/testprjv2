#!/usr/bin/env python3
"""
シンプルなPDFファイルアップロードスクリプト
"""

import requests
from pathlib import Path

# 設定
PRODUCTION_URL = "https://testprjv2-backend.onrender.com"
PDF_DIR = "backend/uploaded_pdfs"

def upload_pdf(file_path):
    """PDFファイルをアップロード"""
    try:
        with open(file_path, 'rb') as f:
            files = {'file': (file_path.name, f, 'application/pdf')}
            data = {
                'url': f'https://example.com/{file_path.name}',
                'school': 'ローカルアップロード',
                'subject': 'unknown',
                'year': '2025'
            }
            
            response = requests.post(f"{PRODUCTION_URL}/upload_pdf/", files=files, data=data)
            
            if response.status_code == 200:
                print(f"✅ {file_path.name}")
                return True
            else:
                print(f"❌ {file_path.name} - {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ {file_path.name} - {e}")
        return False

def main():
    pdf_dir = Path(PDF_DIR)
    pdf_files = list(pdf_dir.glob("*.pdf"))
    
    print(f"アップロード対象: {len(pdf_files)}ファイル")
    
    for pdf_file in pdf_files:
        upload_pdf(pdf_file)

if __name__ == "__main__":
    main()
