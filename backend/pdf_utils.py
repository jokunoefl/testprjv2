import httpx
import os
from urllib.parse import urlparse, urljoin
import re
from typing import Optional, Tuple, List
import requests
from bs4 import BeautifulSoup
import asyncio

async def download_pdf_from_url(url: str, upload_dir: str = "uploaded_pdfs") -> Tuple[str, Optional[str]]:
    """
    URLからPDFをダウンロードし、ファイル名を返す
    戻り値: (ファイル名, エラーメッセージ)
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            
            # Content-TypeがPDFかチェック
            content_type = response.headers.get("content-type", "").lower()
            if "pdf" not in content_type:
                return None, "URLがPDFファイルではありません"
            
            # ファイル名を決定
            filename = get_filename_from_url(url, response.headers)
            filename = get_unique_filename(upload_dir, filename)
            file_path = os.path.join(upload_dir, filename)
            
            # PDFを保存
            with open(file_path, "wb") as f:
                f.write(response.content)
            
            return filename, None
            
    except httpx.HTTPError as e:
        return None, f"HTTPエラー: {str(e)}"
    except Exception as e:
        return None, f"ダウンロードエラー: {str(e)}"

async def crawl_and_download_pdfs(url: str, upload_dir: str = "uploaded_pdfs") -> Tuple[List[str], Optional[str]]:
    """
    WebサイトをクローリングしてPDFリンクを抽出し、ダウンロードする
    戻り値: (ダウンロードされたファイル名のリスト, エラーメッセージ)
    """
    try:
        # サイトのHTMLを取得
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            
        # BeautifulSoupでHTMLを解析
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # PDFリンクを抽出
        pdf_links = extract_pdf_links(soup, url)
        
        if not pdf_links:
            return [], "PDFリンクが見つかりませんでした"
        
        # PDFをダウンロード
        downloaded_files = []
        for pdf_url in pdf_links:
            try:
                filename, error = await download_pdf_from_url(pdf_url, upload_dir)
                if filename:
                    downloaded_files.append(filename)
                else:
                    print(f"PDFダウンロード失敗: {pdf_url} - {error}")
            except Exception as e:
                print(f"PDFダウンロードエラー: {pdf_url} - {str(e)}")
        
        return downloaded_files, None
        
    except Exception as e:
        return [], f"クローリングエラー: {str(e)}"

def extract_pdf_links(soup: BeautifulSoup, base_url: str) -> List[str]:
    """
    HTMLからPDFリンクを抽出
    """
    pdf_links = []
    
    # aタグからPDFリンクを抽出
    for link in soup.find_all('a', href=True):
        href = link['href']
        
        # 相対URLを絶対URLに変換
        if not href.startswith(('http://', 'https://')):
            href = urljoin(base_url, href)
        
        # PDFファイルかチェック
        if is_pdf_link(href):
            pdf_links.append(href)
    
    # 重複を除去
    return list(set(pdf_links))

def is_pdf_link(url: str) -> bool:
    """
    URLがPDFファイルかどうかを判定
    """
    # URLの拡張子をチェック
    if url.lower().endswith('.pdf'):
        return True
    
    # URLにpdfという文字列が含まれているかチェック
    if 'pdf' in url.lower():
        return True
    
    return False

def get_filename_from_url(url: str, headers: dict) -> str:
    """URLまたはヘッダーからファイル名を抽出"""
    # Content-Dispositionヘッダーからファイル名を取得
    content_disposition = headers.get("content-disposition", "")
    if "filename=" in content_disposition:
        match = re.search(r'filename="([^"]+)"', content_disposition)
        if match:
            return match.group(1)
    
    # URLのパスからファイル名を取得
    parsed_url = urlparse(url)
    path = parsed_url.path
    if path.endswith('.pdf'):
        filename = os.path.basename(path)
        if filename:
            return filename
    
    # デフォルトファイル名
    return f"downloaded_{hash(url) % 10000}.pdf"

def get_unique_filename(upload_dir: str, filename: str) -> str:
    """ファイル名の重複を避けるため、必要に応じて番号を付与"""
    base_name, extension = os.path.splitext(filename)
    counter = 1
    unique_filename = filename
    
    while os.path.exists(os.path.join(upload_dir, unique_filename)):
        unique_filename = f"{base_name}_{counter}{extension}"
        counter += 1
    
    return unique_filename

def extract_metadata_from_url(url: str) -> dict:
    """
    URLから学校名、科目、年度などのメタデータを抽出
    （実際の実装では、URLのパターンに応じて抽出ロジックを実装）
    """
    # 例: https://example.com/schools/tokyo_high/2023/math.pdf
    # から学校名、年度、科目を抽出するロジック
    
    # 基本的な実装（実際のURLパターンに応じて調整が必要）
    url_lower = url.lower()
    
    # 年度の抽出（4桁の数字）
    year_match = re.search(r'20\d{2}', url)
    year = int(year_match.group()) if year_match else 2024
    
    # 科目の抽出
    subjects = ['math', 'japanese', 'science', 'social']
    subject = 'unknown'
    for subj in subjects:
        if subj in url_lower:
            subject = subj
            break
    
    # 学校名の抽出（実際のURLパターンに応じて調整）
    school = 'unknown_school'
    
    return {
        'school': school,
        'subject': subject,
        'year': year
    }
