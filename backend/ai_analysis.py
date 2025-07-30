import os
import logging
import base64
from typing import Optional, List
from anthropic import Anthropic
from pdf2image import convert_from_path
from PIL import Image
import io
from config import settings

logger = logging.getLogger(__name__)

# Claude APIクライアントの初期化
anthropic = Anthropic(api_key=settings.ANTHROPIC_API_KEY)

async def analyze_pdf_with_claude(pdf_id: int, pdf_path: str, school: str, subject: str, year: int) -> dict:
    """
    PDFをClaudeに送信して分析を実行する
    """
    try:
        logger.info(f"PDF分析開始: ID={pdf_id}, ファイル={pdf_path}")
        
        # PDFファイルを画像に変換
        images = convert_pdf_to_images(pdf_path)
        if not images:
            return {
                "success": False,
                "error": "PDFファイルの画像変換に失敗しました。"
            }
        
        # Claudeへのプロンプトを作成
        prompt = create_analysis_prompt(school, subject, year)
        
        # Claudeに画像を送信
        analysis_result = send_images_to_claude(prompt, images)
        
        logger.info(f"PDF分析完了: ID={pdf_id}")
        return {
            "success": True,
            "analysis": analysis_result,
            "pdf_file_size": os.path.getsize(pdf_path),
            "pages_converted": len(images)
        }
        
    except Exception as e:
        logger.error(f"PDF分析エラー: ID={pdf_id}, エラー={str(e)}")
        return {
            "success": False,
            "error": f"分析中にエラーが発生しました: {str(e)}"
        }

def convert_pdf_to_images(pdf_path: str) -> Optional[List[str]]:
    """
    PDFファイルを画像に変換する
    """
    try:
        logger.info(f"PDFを画像に変換中: {pdf_path}")
        
        # PDFの各ページを画像に変換
        images = convert_from_path(pdf_path, dpi=200)
        logger.info(f"PDF変換完了: {len(images)} ページ")
        
        # 画像をbase64エンコード
        encoded_images = []
        for i, image in enumerate(images):
            # 画像をJPEG形式でメモリに保存
            img_buffer = io.BytesIO()
            image.save(img_buffer, format='JPEG', quality=85)
            img_buffer.seek(0)
            
            # base64エンコード
            img_base64 = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
            encoded_images.append(img_base64)
            
            logger.info(f"ページ {i+1} をエンコード完了: {len(img_base64)} 文字")
        
        return encoded_images
        
    except Exception as e:
        logger.error(f"PDF画像変換エラー: {str(e)}")
        return None

def create_analysis_prompt(school: str, subject: str, year: int) -> str:
    """
    Claudeへの分析プロンプトを作成する
    """
    prompt = f"""
以下のPDFファイルの画像を分析してください。

**PDF情報:**
- 学校: {school}
- 科目: {subject}
- 年度: {year}

**分析要求:**
以下の項目について、見出しを**太字**で、内容を構造化して回答してください：

**1. PDF概要**
このPDFの全体像と目的を簡潔に説明してください。

**2. 問題構成分析**
含まれている問題の種類、特徴、構成パターンを分析してください。

**3. 難易度評価**
全体的な難易度レベルと、各分野・問題タイプ別の難易度傾向を評価してください。

**4. 学習ポイント**
学習上の重要なポイント、注意点、対策方法を指摘してください。

**5. 教育的価値**
このPDFの教育的意義、活用方法、学習効果について評価してください。

**6. 総合評価**
このPDFの総合的な評価と、どのような学習者に適しているかを述べてください。

回答は日本語で、各見出しを**太字**にして、読みやすい構造化された形式でお願いします。
"""
    return prompt

def send_images_to_claude(prompt: str, images: List[str]) -> str:
    """
    Claudeに画像を送信する
    """
    try:
        logger.info(f"Claudeに画像を送信中... ({len(images)} ページ)")
        
        # メッセージの内容を構築
        content = [
            {
                "type": "text",
                "text": prompt
            }
        ]
        
        # 各画像を追加（最大10ページまで）
        max_pages = min(len(images), 10)  # Claude APIの制限を考慮
        for i in range(max_pages):
            content.append({
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/jpeg",
                    "data": images[i]
                }
            })
        
        message = anthropic.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4000,
            messages=[
                {
                    "role": "user",
                    "content": content
                }
            ]
        )
        
        logger.info("Claudeからの応答を受信")
        return message.content[0].text
        
    except Exception as e:
        logger.error(f"Claude API呼び出しエラー: {str(e)}")
        raise e 