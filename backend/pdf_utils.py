import httpx
import os
from urllib.parse import urlparse, urljoin
import re
from typing import Optional, Tuple, List, Dict
import requests
from bs4 import BeautifulSoup
import asyncio
import pdfplumber
import PyPDF2
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
import logging

# ロガー設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# NLTKデータのダウンロード（初回のみ）
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
except:
    pass  # 既にダウンロード済みの場合

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
        
        # タイムアウト設定付きでサイトのHTMLを取得
        timeout = httpx.Timeout(30.0, connect=10.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            try:
                response = await client.get(url, follow_redirects=True)
                response.raise_for_status()
                logger.info(f"HTML取得成功: {len(response.content)} bytes")
            except httpx.TimeoutException:
                return [], "サイトへの接続がタイムアウトしました"
            except httpx.HTTPStatusError as e:
                return [], f"HTTPエラー: {e.response.status_code} - {e.response.reason_phrase}"
            except httpx.RequestError as e:
                return [], f"リクエストエラー: {str(e)}"

        # BeautifulSoupでHTMLを解析
        try:
            soup = BeautifulSoup(response.content, 'html.parser')
            logger.info("HTML解析完了")
        except Exception as e:
            return [], f"HTML解析エラー: {str(e)}"

        # PDFリンクを抽出
        pdf_links = extract_pdf_links(soup, url)
        logger.info(f"PDFリンク発見: {len(pdf_links)}個")

        if not pdf_links:
            return [], "PDFリンクが見つかりませんでした"

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
                        return None
                except Exception as e:
                    logger.error(f"PDFダウンロードエラー: {pdf_url} - {str(e)}")
                    return None

        # 並行ダウンロード実行
        tasks = [download_single_pdf(pdf_url) for pdf_url in pdf_links]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 結果を処理
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"ダウンロードタスクエラー: {str(result)}")
            elif result is not None:
                downloaded_files.append(result)

        logger.info(f"ダウンロード完了: {len(downloaded_files)}/{len(pdf_links)}個成功")
        return downloaded_files, None

    except Exception as e:
        logger.error(f"クローリングエラー: {str(e)}")
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

def extract_text_from_pdf(file_path: str) -> Tuple[str, Dict[int, str]]:
    """
    PDFからテキストを抽出する
    戻り値: (全体テキスト, {ページ番号: ページテキスト})
    """
    try:
        # pdfplumberを使用してテキストを抽出
        text_by_page = {}
        full_text = ""

        with pdfplumber.open(file_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                page_text = page.extract_text()
                if page_text:
                    text_by_page[page_num] = page_text
                    full_text += f"\n--- ページ {page_num} ---\n{page_text}\n"

        return full_text, text_by_page

    except Exception as e:
        logger.error(f"PDFテキスト抽出エラー: {str(e)}")
        # PyPDF2でフォールバック
        try:
            text_by_page = {}
            full_text = ""

            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page_num, page in enumerate(pdf_reader.pages, 1):
                    page_text = page.extract_text()
                    if page_text:
                        text_by_page[page_num] = page_text
                        full_text += f"\n--- ページ {page_num} ---\n{page_text}\n"

            return full_text, text_by_page

        except Exception as e2:
            logger.error(f"PyPDF2でもエラー: {str(e2)}")
            return "", {}

def analyze_questions(text: str, subject: str) -> List[Dict]:
    """
    テキストから問題を解析して抽出する
    """
    questions = []

    # 問題番号のパターンを定義
    question_patterns = [
        r'(\d+)[．.、]\s*',  # 1. 1． 1、
        r'問(\d+)[．.、]\s*',  # 問1. 問1．
        r'\((\d+)\)\s*',  # (1) (2)
        r'（(\d+)）\s*',  # （1） （2）
    ]

    # 科目別のキーワード
    subject_keywords = {
        'math': ['計算', '式', '答え', '解', '求める', '証明', '図形', '面積', '体積'],
        'japanese': ['読解', '文章', '漢字', '文法', '読む', '書く', '表現'],
        'science': ['実験', '観察', '結果', '理由', '説明', '図', '表'],
        'social': ['歴史', '地理', '政治', '経済', '文化', '説明', '理由']
    }

    lines = text.split('\n')
    current_question = None

    for line_num, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue

        # 問題番号を検出
        question_number = None
        for pattern in question_patterns:
            match = re.match(pattern, line)
            if match:
                question_number = match.group(1)
                break

        if question_number:
            # 新しい問題の開始
            if current_question:
                questions.append(current_question)

            current_question = {
                'question_number': question_number,
                'question_text': line,
                'page_number': None,  # 後で設定
                'extracted_text': line,
                'difficulty_level': None,
                'points': None
            }
        elif current_question:
            # 既存の問題に追加
            current_question['question_text'] += '\n' + line
            current_question['extracted_text'] += '\n' + line

    # 最後の問題を追加
    if current_question:
        questions.append(current_question)

    # 問題の詳細分析
    for question in questions:
        question_text = question['question_text'].lower()

        # 難易度の推定
        difficulty_keywords = {
            1: ['簡単', '基礎', '基本'],
            2: ['標準', '普通'],
            3: ['応用', '発展'],
            4: ['難問', '高度'],
            5: ['超難問', '最難関']
        }

        for level, keywords in difficulty_keywords.items():
            if any(keyword in question_text for keyword in keywords):
                question['difficulty_level'] = level
                break

        if question['difficulty_level'] is None:
            question['difficulty_level'] = 2  # デフォルト

        # 配点の推定
        point_patterns = [
            r'(\d+)点',
            r'配点(\d+)',
            r'\((\d+)点\)'
        ]

        for pattern in point_patterns:
            match = re.search(pattern, question_text)
            if match:
                question['points'] = float(match.group(1))
                break

        if question['points'] is None:
            question['points'] = 5.0  # デフォルト

    return questions

def extract_questions_from_pdf(file_path: str, subject: str) -> List[Dict]:
    """
    PDFから問題を抽出するメイン関数
    """
    try:
        # テキストを抽出
        full_text, text_by_page = extract_text_from_pdf(file_path)

        if not full_text:
            logger.warning(f"PDFからテキストを抽出できませんでした: {file_path}")
            return []

        # 問題を解析
        questions = analyze_questions(full_text, subject)

        # ページ番号を設定
        for question in questions:
            # 問題番号からページ番号を推定（簡易版）
            question_num = int(question['question_number'])
            estimated_page = min((question_num - 1) // 5 + 1, len(text_by_page))
            question['page_number'] = estimated_page

        logger.info(f"PDFから {len(questions)} 個の問題を抽出しました: {file_path}")
        return questions

    except Exception as e:
        logger.error(f"問題抽出エラー: {str(e)}")
        return []
