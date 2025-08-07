import os
import re
import asyncio
import logging
from typing import List, Optional, Tuple, Dict
from urllib.parse import urljoin, urlparse
from datetime import datetime

import httpx
from bs4 import BeautifulSoup
import pdfplumber
import PyPDF2
import nltk
try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
    print("Warning: pytesseract not available. OCR functionality will be disabled.")

from PIL import Image
import io

# ロガー設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# NLTKデータのダウンロード（初回のみ）
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
except:
    pass  # 既にダウンロード済みの場合

# Tesseractのパス設定（macOS）
try:
    pytesseract.pytesseract.tesseract_cmd = '/opt/homebrew/bin/tesseract'
except:
    pass  # デフォルトパスを使用

async def download_pdf_from_url(url: str, upload_dir: str = "uploaded_pdfs") -> Tuple[str, Optional[str]]:
    """
    URLからPDFをダウンロードし、ファイル名を返す
    戻り値: (ファイル名, エラーメッセージ)
    """
    try:
        logger.info(f"PDFダウンロード開始: {url}")
        
        # タイムアウト設定付きでダウンロード
        timeout = httpx.Timeout(60.0, connect=15.0, read=45.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            try:
                response = await client.get(url, follow_redirects=True)
                response.raise_for_status()
                logger.info(f"PDFダウンロード成功: {len(response.content)} bytes")
            except httpx.TimeoutException:
                return None, "PDFダウンロードがタイムアウトしました"
            except httpx.HTTPStatusError as e:
                return None, f"HTTPエラー: {e.response.status_code} - {e.response.reason_phrase}"
            except httpx.RequestError as e:
                return None, f"リクエストエラー: {str(e)}"

            # Content-TypeがPDFかチェック
            content_type = response.headers.get("content-type", "").lower()
            if "pdf" not in content_type:
                logger.warning(f"Content-TypeがPDFではありません: {content_type}")
                # Content-TypeがPDFでなくても、URLに.pdfが含まれていればダウンロードを試行
                if not url.lower().endswith('.pdf'):
                    return None, "URLがPDFファイルではありません"

            # ファイルサイズチェック
            content_length = response.headers.get("content-length")
            if content_length:
                size_mb = int(content_length) / (1024 * 1024)
                if size_mb > 50:  # 50MB以上は警告
                    logger.warning(f"大きなファイルです: {size_mb:.1f}MB")

            # ファイル名を決定
            filename = get_filename_from_url(url, response.headers)
            filename = get_unique_filename(upload_dir, filename)
            file_path = os.path.join(upload_dir, filename)

            # PDFを保存
            try:
                with open(file_path, "wb") as f:
                    f.write(response.content)
                logger.info(f"PDF保存完了: {filename}")
                return filename, None
            except IOError as e:
                return None, f"ファイル保存エラー: {str(e)}"

    except Exception as e:
        logger.error(f"PDFダウンロードエラー: {url} - {str(e)}")
        return None, f"ダウンロードエラー: {str(e)}"

async def crawl_and_download_pdfs(url: str, upload_dir: str = "uploaded_pdfs") -> Tuple[List[str], Optional[str]]:
    """
    WebサイトをクローリングしてPDFリンクを抽出し、ダウンロードする
    戻り値: (ダウンロードされたファイル名のリスト, エラーメッセージ)
    """
    try:
        logger.info(f"クローリング開始: {url}")
        
        # URLの形式をチェック
        if not url.startswith(('http://', 'https://')):
            return [], "URLは http:// または https:// で始まる必要があります"
        
        # タイムアウト設定付きでサイトのHTMLを取得
        timeout = httpx.Timeout(30.0, connect=10.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            try:
                logger.info(f"サイトに接続中: {url}")
                response = await client.get(url, follow_redirects=True)
                response.raise_for_status()
                logger.info(f"HTML取得成功: {len(response.content)} bytes")
                logger.info(f"Content-Type: {response.headers.get('content-type', 'unknown')}")
            except httpx.TimeoutException:
                error_msg = "サイトへの接続がタイムアウトしました。サイトが応答していないか、ネットワーク接続に問題があります。"
                logger.error(f"タイムアウトエラー: {url}")
                return [], error_msg
            except httpx.HTTPStatusError as e:
                error_msg = f"HTTPエラー {e.response.status_code}: {e.response.reason_phrase}。サイトが利用できないか、アクセスが制限されています。"
                logger.error(f"HTTPエラー: {url} - {e.response.status_code} {e.response.reason_phrase}")
                return [], error_msg
            except httpx.RequestError as e:
                error_msg = f"リクエストエラー: {str(e)}。URLが正しいか、ネットワーク接続を確認してください。"
                logger.error(f"リクエストエラー: {url} - {str(e)}")
                return [], error_msg

        # BeautifulSoupでHTMLを解析
        try:
            soup = BeautifulSoup(response.content, 'html.parser')
            logger.info("HTML解析完了")
            logger.info(f"ページタイトル: {soup.title.string if soup.title else 'タイトルなし'}")
        except Exception as e:
            error_msg = f"HTML解析エラー: {str(e)}。サイトの構造が予期しない形式です。"
            logger.error(f"HTML解析エラー: {url} - {str(e)}")
            return [], error_msg

        # PDFリンクを抽出
        pdf_links = extract_pdf_links(soup, url)
        logger.info(f"PDFリンク発見: {len(pdf_links)}個")

        if not pdf_links:
            error_msg = "PDFリンクが見つかりませんでした。このサイトにはPDFファイルが含まれていないか、リンクの形式が異なります。"
            logger.warning(f"PDFリンク未発見: {url}")
            logger.info("ページ内のリンクを確認中...")
            all_links = soup.find_all('a', href=True)
            logger.info(f"ページ内の総リンク数: {len(all_links)}")
            for i, link in enumerate(all_links[:10]):  # 最初の10個のリンクをログ出力
                logger.info(f"  リンク {i+1}: {link.get('href')} - テキスト: {link.get_text()[:50]}")
            return [], error_msg

        # PDFをダウンロード（並行処理で高速化）
        downloaded_files = []
        failed_downloads = []
        
        # 同時ダウンロード数を制限（サーバー負荷軽減）
        semaphore = asyncio.Semaphore(3)
        
        async def download_single_pdf(pdf_url: str):
            async with semaphore:
                try:
                    filename, error = await download_pdf_from_url(pdf_url, upload_dir)
                    if filename:
                        logger.info(f"PDFダウンロード成功: {filename}")
                        return filename
                    else:
                        logger.warning(f"PDFダウンロード失敗: {pdf_url} - {error}")
                        failed_downloads.append(f"{pdf_url}: {error}")
                        return None
                except Exception as e:
                    logger.error(f"PDFダウンロードエラー: {pdf_url} - {str(e)}")
                    failed_downloads.append(f"{pdf_url}: {str(e)}")
                    return None

        # 並行ダウンロード実行
        logger.info(f"PDFダウンロード開始: {len(pdf_links)}個のファイル")
        tasks = [download_single_pdf(pdf_url) for pdf_url in pdf_links]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 結果を処理
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"ダウンロードタスクエラー: {str(result)}")
                failed_downloads.append(f"タスクエラー: {str(result)}")
            elif result is not None:
                downloaded_files.append(result)

        logger.info(f"ダウンロード完了: {len(downloaded_files)}/{len(pdf_links)}個成功")
        
        # エラーメッセージの詳細化
        if downloaded_files:
            if failed_downloads:
                error_msg = f"一部のPDFのダウンロードに失敗しました。成功: {len(downloaded_files)}個、失敗: {len(failed_downloads)}個"
                logger.warning(f"部分的なダウンロード失敗: {error_msg}")
            else:
                error_msg = None
            return downloaded_files, error_msg
        else:
            error_msg = f"すべてのPDFのダウンロードに失敗しました。詳細: {', '.join(failed_downloads[:3])}"
            if len(failed_downloads) > 3:
                error_msg += f" 他{len(failed_downloads) - 3}個"
            logger.error(f"全ダウンロード失敗: {error_msg}")
            return [], error_msg

    except Exception as e:
        error_msg = f"予期しないクローリングエラー: {str(e)}。システム管理者に連絡してください。"
        logger.error(f"予期しないクローリングエラー: {url} - {str(e)}")
        import traceback
        logger.error(f"トレースバック: {traceback.format_exc()}")
        return [], error_msg

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

    # その他の要素からもPDFリンクを検索（script、meta、linkタグなど）
    for script in soup.find_all('script'):
        if script.string:
            # JavaScript内のPDFリンクを検索
            pdf_urls = re.findall(r'["\']([^"\']*\.pdf[^"\']*)["\']', script.string, re.IGNORECASE)
            for pdf_url in pdf_urls:
                if not pdf_url.startswith(('http://', 'https://')):
                    pdf_url = urljoin(base_url, pdf_url)
                if is_pdf_link(pdf_url):
                    pdf_links.append(pdf_url)

    # ページ内のテキストからPDFリンクを検索
    page_text = soup.get_text()
    pdf_urls = re.findall(r'https?://[^\s<>"\']*\.pdf[^\s<>"\']*', page_text, re.IGNORECASE)
    pdf_links.extend(pdf_urls)

    # より広範囲なPDFリンク検索
    # 1. リンクテキストに「PDF」が含まれる場合
    for link in soup.find_all('a', href=True):
        link_text = link.get_text().lower()
        if 'pdf' in link_text or 'ダウンロード' in link_text or 'download' in link_text:
            href = link['href']
            if not href.startswith(('http://', 'https://')):
                href = urljoin(base_url, href)
            if href not in pdf_links:
                pdf_links.append(href)

    # 2. 画像のalt属性やtitle属性にPDFが含まれる場合
    for img in soup.find_all('img'):
        alt_text = img.get('alt', '').lower()
        title_text = img.get('title', '').lower()
        if 'pdf' in alt_text or 'pdf' in title_text:
            # 画像の親要素にリンクがあるかチェック
            parent_link = img.find_parent('a')
            if parent_link and parent_link.get('href'):
                href = parent_link['href']
                if not href.startswith(('http://', 'https://')):
                    href = urljoin(base_url, href)
                if href not in pdf_links:
                    pdf_links.append(href)

    # 3. 特定のクラス名やIDを持つ要素からPDFリンクを検索
    for element in soup.find_all(['div', 'span', 'p'], class_=re.compile(r'pdf|download|file', re.IGNORECASE)):
        links = element.find_all('a', href=True)
        for link in links:
            href = link['href']
            if not href.startswith(('http://', 'https://')):
                href = urljoin(base_url, href)
            if href not in pdf_links:
                pdf_links.append(href)

    # 重複を除去してソート
    unique_links = list(set(pdf_links))
    unique_links.sort()
    
    logger.info(f"PDFリンク抽出結果: {len(unique_links)}個のユニークなリンク")
    for i, link in enumerate(unique_links[:5]):  # 最初の5個をログ出力
        logger.info(f"  リンク {i+1}: {link}")
    if len(unique_links) > 5:
        logger.info(f"  ... 他 {len(unique_links) - 5}個のリンク")
    
    return unique_links

def is_pdf_link(url: str) -> bool:
    """
    URLがPDFファイルかどうかを判定
    """
    # URLの正規化
    url_lower = url.lower()
    
    # URLの拡張子をチェック
    if url_lower.endswith('.pdf'):
        return True
    
    # URLにpdfという文字列が含まれているかチェック
    if 'pdf' in url_lower:
        # ただし、PDFの説明ページなどは除外
        exclude_patterns = [
            'pdf-viewer', 'pdf-reader', 'pdf-download', 'pdf-upload',
            'pdf-converter', 'pdf-editor', 'pdf-tools', 'pdf-software',
            'pdf-online', 'pdf-free', 'pdf-app', 'pdf-apps',
            'pdf-print', 'pdf-merge', 'pdf-split', 'pdf-compress'
        ]
        for pattern in exclude_patterns:
            if pattern in url_lower:
                return False
        return True
    
    # 特定のパターンでPDFファイルを識別
    pdf_patterns = [
        r'/uploads/.*\.pdf',
        r'/files/.*\.pdf',
        r'/documents/.*\.pdf',
        r'/downloads/.*\.pdf',
        r'/past.*\.pdf',
        r'/exam.*\.pdf',
        r'/test.*\.pdf',
        r'/question.*\.pdf'
    ]
    
    for pattern in pdf_patterns:
        if re.search(pattern, url_lower):
            return True
    
    # Content-TypeがPDFの場合の判定（実際のダウンロード時にチェック）
    # ここでは基本的な判定のみ行う
    
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
    try:
        logger.info(f"メタデータ抽出開始: {url}")
        
        # 例: https://example.com/schools/tokyo_high/2023/math.pdf
        # から学校名、年度、科目を抽出するロジック

        # 基本的な実装（実際のURLパターンに応じて調整が必要）
        url_lower = url.lower()

        # 年度の抽出（4桁の数字）
        year_match = re.search(r'20\d{2}', url)
        year = int(year_match.group()) if year_match else 2024
        logger.info(f"抽出された年度: {year}")

        # 科目の抽出
        subjects = ['math', 'japanese', 'science', 'social']
        subject = 'unknown'
        for subj in subjects:
            if subj in url_lower:
                subject = subj
                break
        logger.info(f"抽出された科目: {subject}")

        # 学校名の抽出（実際のURLパターンに応じて調整）
        school = 'unknown_school'
        
        # URLから学校名を抽出する試行
        url_parts = url.split('/')
        for part in url_parts:
            if 'school' in part.lower() or 'high' in part.lower() or 'middle' in part.lower():
                school = part.replace('-', '_').replace('.', '_')
                break
        
        logger.info(f"抽出された学校名: {school}")

        result = {
            'school': school,
            'subject': subject,
            'year': year
        }
        
        logger.info(f"メタデータ抽出完了: {result}")
        return result
        
    except Exception as e:
        logger.error(f"メタデータ抽出エラー: {str(e)}")
        # エラーの場合はデフォルト値を返す
        return {
            'school': 'unknown_school',
            'subject': 'unknown',
            'year': 2024
        }

async def extract_text_from_pdf(pdf_path: str) -> Optional[str]:
    """
    PDFからテキストを抽出する（AI分析用）
    """
    try:
        logger.info(f"テキスト抽出開始: {pdf_path}")
        
        # pdfplumberで試行
        try:
            with pdfplumber.open(pdf_path) as pdf:
                text = ""
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                
                if text.strip():
                    logger.info(f"pdfplumberでテキスト抽出成功: {len(text)} 文字")
                    return text.strip()
        except Exception as e:
            logger.warning(f"pdfplumberでテキスト抽出失敗: {str(e)}")
        
        # PyPDF2でフォールバック
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                
                if text.strip():
                    logger.info(f"PyPDF2でテキスト抽出成功: {len(text)} 文字")
                    return text.strip()
        except Exception as e:
            logger.warning(f"PyPDF2でテキスト抽出失敗: {str(e)}")
        
        # OCRでフォールバック
        try:
            text, _ = extract_text_from_pdf_with_ocr(pdf_path)
            if text:
                logger.info(f"OCRでテキスト抽出成功: {len(text)} 文字")
                return text
        except Exception as e:
            logger.warning(f"OCRでテキスト抽出失敗: {str(e)}")
        
        logger.error(f"すべての方法でテキスト抽出に失敗: {pdf_path}")
        return None
        
    except Exception as e:
        logger.error(f"テキスト抽出エラー: {str(e)}")
        return None

def extract_text_from_pdf_with_ocr(file_path: str) -> Tuple[str, Dict[int, str]]:
    """
    OCRを使用してPDFからテキストを抽出する
    戻り値: (全体テキスト, {ページ番号: ページテキスト})
    """
    if not TESSERACT_AVAILABLE:
        logger.warning("OCR機能が利用できません（pytesseractがインストールされていません）")
        return "", {}
    
    logger.info(f"OCRテキスト抽出開始: {file_path}")
    
    try:
        text_by_page = {}
        full_text = ""
        
        with pdfplumber.open(file_path) as pdf:
            logger.info(f"OCR - PDFページ数: {len(pdf.pages)}")
            
            for page_num, page in enumerate(pdf.pages, 1):
                try:
                    # ページを画像に変換
                    page_image = page.to_image()
                    if page_image:
                        # PIL Imageに変換
                        pil_image = page_image.original
                        
                        # 画像の前処理（コントラスト向上）
                        from PIL import ImageEnhance
                        enhancer = ImageEnhance.Contrast(pil_image)
                        pil_image = enhancer.enhance(1.5)  # コントラストを1.5倍に
                        
                        # OCRでテキスト抽出（日本語優先）
                        page_text = pytesseract.image_to_string(
                            pil_image, 
                            lang='jpn',  # 日本語のみ
                            config='--psm 6 --oem 1 -c preserve_interword_spaces=1'
                        )
                        
                        if page_text and page_text.strip():
                            # テキストの後処理
                            cleaned_text = clean_ocr_text(page_text)
                            if cleaned_text:
                                text_by_page[page_num] = cleaned_text
                                full_text += f"\n--- ページ {page_num} ---\n{cleaned_text}\n"
                                logger.info(f"OCR - ページ {page_num}: {len(cleaned_text)} 文字抽出")
                            else:
                                logger.warning(f"OCR - ページ {page_num}: クリーンアップ後にテキストが空になりました")
                        else:
                            logger.warning(f"OCR - ページ {page_num}: テキストが抽出できませんでした")
                    else:
                        logger.warning(f"OCR - ページ {page_num}: 画像変換に失敗")
                        
                except Exception as e:
                    logger.error(f"OCR - ページ {page_num} のテキスト抽出エラー: {str(e)}")
        
        if full_text.strip():
            logger.info(f"OCRでテキスト抽出成功: {len(full_text)} 文字")
            return full_text, text_by_page
        else:
            logger.warning("OCRでもテキストが抽出できませんでした")
            return "", {}
            
    except Exception as e:
        logger.error(f"OCRテキスト抽出エラー: {str(e)}")
        return "", {}

def clean_ocr_text(text: str) -> str:
    """
    OCRで抽出されたテキストをクリーンアップする
    """
    if not text:
        return ""
    
    # 基本的なクリーンアップ
    lines = text.split('\n')
    cleaned_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # 不要な文字の除去
        line = re.sub(r'[^\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF\u3000-\u303F\uFF00-\uFFEF\u0020-\u007E\u3000-\u303F]', '', line)
        
        # 連続する空白を単一の空白に
        line = re.sub(r'\s+', ' ', line)
        
        # 行の前後の空白を除去
        line = line.strip()
        
        if line and len(line) > 1:  # 1文字以下の行は除外
            cleaned_lines.append(line)
    
    # 日本語文字が含まれている行のみを保持
    japanese_lines = []
    for line in cleaned_lines:
        # 日本語文字（ひらがな、カタカナ、漢字）が含まれているかチェック
        if re.search(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]', line):
            japanese_lines.append(line)
        # 数字と記号のみの行も保持（問題番号など）
        elif re.match(r'^[\d\s\(\)①②③④⑤⑥⑦⑧⑨⑩]+$', line):
            japanese_lines.append(line)
    
    return '\n'.join(japanese_lines)

def extract_text_from_pdf(file_path: str) -> Tuple[str, Dict[int, str]]:
    """
    PDFからテキストを抽出する（通常の方法 + OCR）
    戻り値: (全体テキスト, {ページ番号: ページテキスト})
    """
    logger.info(f"PDFテキスト抽出開始: {file_path}")
    
    try:
        # ファイルの存在確認
        if not os.path.exists(file_path):
            logger.error(f"PDFファイルが存在しません: {file_path}")
            return "", {}
        
        # ファイルサイズ確認
        file_size = os.path.getsize(file_path)
        logger.info(f"PDFファイルサイズ: {file_size} bytes")
        
        if file_size == 0:
            logger.error(f"PDFファイルが空です: {file_path}")
            return "", {}
        
        # pdfplumberを使用してテキストを抽出
        text_by_page = {}
        full_text = ""

        try:
            with pdfplumber.open(file_path) as pdf:
                logger.info(f"PDFページ数: {len(pdf.pages)}")
                
                for page_num, page in enumerate(pdf.pages, 1):
                    try:
                        page_text = page.extract_text()
                        if page_text and page_text.strip():
                            text_by_page[page_num] = page_text.strip()
                            full_text += f"\n--- ページ {page_num} ---\n{page_text.strip()}\n"
                            logger.info(f"ページ {page_num}: {len(page_text)} 文字抽出")
                        else:
                            logger.warning(f"ページ {page_num}: テキストが抽出できませんでした")
                    except Exception as e:
                        logger.error(f"ページ {page_num} のテキスト抽出エラー: {str(e)}")
            
            if full_text.strip():
                logger.info(f"pdfplumberでテキスト抽出成功: {len(full_text)} 文字")
                return full_text, text_by_page
            else:
                logger.warning("pdfplumberでテキストが抽出できませんでした")
                
        except Exception as e:
            logger.error(f"pdfplumberエラー: {str(e)}")

        # PyPDF2でフォールバック
        logger.info("PyPDF2でフォールバック試行")
        try:
            text_by_page = {}
            full_text = ""

            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                logger.info(f"PyPDF2 - PDFページ数: {len(pdf_reader.pages)}")
                
                for page_num, page in enumerate(pdf_reader.pages, 1):
                    try:
                        page_text = page.extract_text()
                        if page_text and page_text.strip():
                            text_by_page[page_num] = page_text.strip()
                            full_text += f"\n--- ページ {page_num} ---\n{page_text.strip()}\n"
                            logger.info(f"PyPDF2 - ページ {page_num}: {len(page_text)} 文字抽出")
                        else:
                            logger.warning(f"PyPDF2 - ページ {page_num}: テキストが抽出できませんでした")
                    except Exception as e:
                        logger.error(f"PyPDF2 - ページ {page_num} のテキスト抽出エラー: {str(e)}")

            if full_text.strip():
                logger.info(f"PyPDF2でテキスト抽出成功: {len(full_text)} 文字")
                return full_text, text_by_page
            else:
                logger.warning("PyPDF2でもテキストが抽出できませんでした")

        except Exception as e2:
            logger.error(f"PyPDF2エラー: {str(e2)}")

        # OCRでフォールバック（利用可能な場合のみ）
        if TESSERACT_AVAILABLE:
            logger.info("OCRでフォールバック試行")
            try:
                ocr_text, ocr_text_by_page = extract_text_from_pdf_with_ocr(file_path)
                if ocr_text.strip():
                    logger.info(f"OCRでテキスト抽出成功: {len(ocr_text)} 文字")
                    return ocr_text, ocr_text_by_page
                else:
                    logger.warning("OCRでもテキストが抽出できませんでした")
            except Exception as e3:
                logger.error(f"OCRエラー: {str(e3)}")
        else:
            logger.info("OCR機能が利用できないため、スキップします")

        # 最終的にテキストが抽出できなかった場合
        logger.error(f"すべての方法でテキスト抽出に失敗: {file_path}")
        return "", {}

    except Exception as e:
        logger.error(f"PDFテキスト抽出全体エラー: {str(e)}")
        return "", {}

def analyze_questions(text: str, subject: str = "unknown") -> List[Dict]:
    """
    テキストから問題を分析して抽出する
    """
    logger.info(f"問題分析開始: {len(text)} 文字")
    
    questions = []
    lines = text.split('\n')
    current_question = None
    
    # 問題パターンを拡張（日本語の問題番号に対応）
    question_patterns = [
        r'^(\d+)[\.\)]',  # 1. 1)
        r'^問(\d+)',      # 問1
        r'^(\d+)問',      # 1問
        r'^\((\d+)\)',    # (1)
        r'^(\d+)[①②③④⑤⑥⑦⑧⑨⑩]',  # 1①
        r'^[①②③④⑤⑥⑦⑧⑨⑩](\d+)',  # ①1
        r'^(\d+)[A-Z]',   # 1A
        r'^[A-Z](\d+)',   # A1
        r'^(\d+)[a-z]',   # 1a
        r'^[a-z](\d+)',   # a1
        r'^問題(\d+)',    # 問題1
        r'^(\d+)問題',    # 1問題
        r'^第(\d+)問',    # 第1問
        r'^(\d+)番',      # 1番
        r'^(\d+)\.(\d+)', # 1.1
        r'^(\d+)-(\d+)',  # 1-1
    ]
    
    # 科目キーワードを拡張
    subject_keywords = {
        '数学': ['数学', '算数', '計算', '数式', '方程式', '関数', '図形', '面積', '体積', '角度'],
        '国語': ['国語', '読解', '文章', '漢字', '文法', '読書', '文学', '小説', '詩'],
        '理科': ['理科', '科学', '物理', '化学', '生物', '地学', '実験', '観察', '自然'],
        '社会': ['社会', '歴史', '地理', '公民', '政治', '経済', '文化', '国際'],
        '英語': ['英語', 'English', '英単語', '文法', '読解', 'リスニング'],
        'unknown': []
    }
    
    # 問題タイプの自動判定
    question_type_keywords = {
        '選択問題': ['選択', '選び', '選んで', '正しい', '誤っている', 'ア〜エ', '①〜④', 'A〜D'],
        '記述問題': ['記述', '説明', '理由', 'なぜ', 'どのように', '述べ', '書きなさい'],
        '計算問題': ['計算', '求め', '答え', '解き', '式', '方程式', '面積', '体積']
    }
    
    # 難易度キーワード
    difficulty_keywords = {
        '基礎': ['基礎', '基本', '簡単', '易しい', '初級'],
        '標準': ['標準', '普通', '中級', '一般的'],
        '応用': ['応用', '発展', '難しい', '上級', '高度'],
        'unknown': []
    }
    
    # 配点パターン
    point_patterns = [
        r'（(\d+)点）',
        r'\((\d+)点\)',
        r'(\d+)点',
        r'（(\d+)分）',
        r'\((\d+)分\)',
        r'(\d+)分',
        r'配点(\d+)',
        r'(\d+)配点'
    ]
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
        
        # 問題番号の検出
        question_number = None
        for pattern in question_patterns:
            match = re.match(pattern, line)
            if match:
                if len(match.groups()) == 1:
                    question_number = match.group(1)
                elif len(match.groups()) == 2:
                    question_number = f"{match.group(1)}.{match.group(2)}"
                break
        
        if question_number:
            # 前の問題を保存
            if current_question:
                questions.append(current_question)
            
            # 新しい問題を開始
            current_question = {
                'question_number': question_number,
                'question_text': line,
                'subject': subject,
                'question_type': '選択問題',  # デフォルト
                'difficulty': 'unknown',
                'points': 0,
                'page_number': 1  # デフォルト
            }
            
            # 問題タイプの自動判定
            for qtype, keywords in question_type_keywords.items():
                if any(keyword in line for keyword in keywords):
                    current_question['question_type'] = qtype
                    break
            
            # 配点の検出
            for pattern in point_patterns:
                point_match = re.search(pattern, line)
                if point_match:
                    current_question['points'] = int(point_match.group(1))
                    break
            
            logger.info(f"問題検出: {question_number}")
            
        elif current_question:
            # 現在の問題にテキストを追加
            current_question['question_text'] += '\n' + line
            
            # 配点がまだ設定されていない場合、行内で検索
            if current_question['points'] == 0:
                for pattern in point_patterns:
                    point_match = re.search(pattern, line)
                    if point_match:
                        current_question['points'] = int(point_match.group(1))
                        break
    
    # 最後の問題を追加
    if current_question:
        questions.append(current_question)
    
    # 配点が設定されていない問題にデフォルト値を設定
    for question in questions:
        if question['points'] == 0:
            # 問題番号に基づいて推定
            try:
                num = int(question['question_number'].split('.')[0])
                if num <= 5:
                    question['points'] = 5
                elif num <= 10:
                    question['points'] = 3
                else:
                    question['points'] = 2
            except:
                question['points'] = 3
    
    logger.info(f"問題分析完了: {len(questions)} 個の問題を検出")
    return questions

def convert_difficulty_to_int(difficulty_str: str) -> int:
    """
    難易度文字列を整数に変換する
    """
    difficulty_mapping = {
        'easy': 1,
        'medium': 2,
        'hard': 3,
        'unknown': 1,  # デフォルトは1（易しい）
        '易しい': 1,
        '普通': 2,
        '難しい': 3,
        '初級': 1,
        '中級': 2,
        '上級': 3,
    }
    
    # 文字列を小文字に変換してマッピングを確認
    difficulty_lower = difficulty_str.lower()
    return difficulty_mapping.get(difficulty_lower, 1)  # デフォルトは1

def extract_questions_from_pdf(file_path: str, subject: str = "unknown") -> List[Dict]:
    """
    PDFから問題を抽出する
    """
    logger.info(f"PDF問題抽出開始: {file_path}, 科目: {subject}")
    
    try:
        # テキスト抽出
        text, text_by_page = extract_text_from_pdf(file_path)
        
        if not text.strip():
            logger.warning(f"PDFからテキストを抽出できませんでした: {file_path}")
            return []
        
        logger.info(f"抽出されたテキスト長: {len(text)} 文字")
        logger.info(f"抽出されたページ数: {len(text_by_page)}")
        
        # テキストプレビュー（最初の数行）
        preview_lines = text.split('\n')[:10]
        preview_text = '\n'.join(preview_lines)
        logger.info(f"テキストプレビュー: {preview_text}")
        
        # 問題分析
        questions = analyze_questions(text, subject)
        
        if not questions:
            logger.warning(f"問題が検出されませんでした: {file_path}")
            # デバッグ用：テキストの最初の数行をログ出力
            lines = text.split('\n')
            logger.info(f"テキストの行数: {len(lines)}")
            for i, line in enumerate(lines[:10], 1):
                logger.info(f"行 {i}: {line}")
            return []
        
        logger.info(f"PDFから {len(questions)} 個の問題を抽出しました: {file_path}")
        
        # 問題データを整形
        formatted_questions = []
        for i, question in enumerate(questions, 1):
            try:
                # 難易度を整数に変換
                difficulty_int = convert_difficulty_to_int(question.get('difficulty', 'unknown'))
                
                formatted_question = {
                    'question_number': question['question_number'],
                    'question_text': question['question_text'],
                    'answer_text': question.get('answer_text', ''),
                    'difficulty_level': difficulty_int,  # 整数値に変換
                    'points': question.get('points', 0),
                    'page_number': question.get('page_number', 1),
                    'extracted_text': question.get('extracted_text', question['question_text']),
                    'question_type': question.get('question_type', '選択問題')
                }
                
                formatted_questions.append(formatted_question)
                
                logger.info(f"問題 {i}: 番号={question['question_number']}, "
                          f"タイプ={formatted_question['question_type']}, "
                          f"難易度={difficulty_int}, "
                          f"配点={formatted_question['points']}, "
                          f"ページ={formatted_question['page_number']}")
                
            except Exception as e:
                logger.error(f"問題 {i} の整形エラー: {e}")
                continue
        
        return formatted_questions
        
    except Exception as e:
        logger.error(f"問題抽出エラー: {e}")
        import traceback
        traceback.print_exc()
        return []
