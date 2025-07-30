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
以下のPDFファイルの画像を詳細に分析してください。

**PDF情報:**
- 学校: {school}
- 科目: {subject}
- 年度: {year}

**詳細分析要求:**
以下の項目について、見出しを**太字**で、具体的で詳細な内容を構造化して回答してください：

**1. PDF概要・基本情報**
- 試験の種類（入学試験、定期試験、模擬試験など）
- 試験時間と配点構成
- 出題形式（記述式、選択式、混合など）
- ページ数と問題数
- 特徴的な要素や注意点

**2. 問題構成の詳細分析**
- 大問ごとの詳細な分析：
  - 各大問のテーマ・分野
  - 問題数と配点
  - 出題形式（記述、選択、計算など）
  - 特徴的な問題パターン
- 問題の流れと構成の特徴
- 基礎問題と応用問題のバランス
- 時事的要素の有無と内容

**3. 難易度の詳細評価**
- 全体の難易度レベル（易しい・普通・難しい・非常に難しい）
- 分野別難易度分析：
  - 各分野の難易度レベル
  - 特に難しい問題の特徴
  - 基礎知識を問う問題の割合
- 問題の段階的難易度（易→難の流れ）
- 受験生の平均正答率予想

**4. 問題の質の評価（5段階）**
このPDFに含まれる問題の質を以下の5段階で詳細に評価してください：
- **5点（優秀）**: 非常に良質で教育的価値が高い問題
- **4点（良好）**: 良質で学習効果が期待できる問題
- **3点（普通）**: 標準的な質の問題
- **2点（やや低い）**: 質に改善の余地がある問題
- **1点（低い）**: 質が低く教育的価値が限定的な問題

評価の根拠：
- 問題の独創性とオリジナリティ
- 思考力を問う要素の有無
- 実生活との関連性
- 基礎知識と応用力のバランス
- 問題文の明確性と適切性

**5. 学習上の重要ポイント**
- 重点的に学習すべき分野・単元
- 頻出テーマと重要概念
- 苦手分野になりやすいポイント
- 効率的な学習方法の提案
- 過去問との比較・傾向分析

**6. 教育的価値と活用方法**
- この問題集の教育的意義
- どのような学習段階で活用すべきか
- 教師・指導者向けの活用アドバイス
- 生徒・受験生向けの学習アドバイス
- 他校の入試問題との比較優位性

**7. 受験対策・学習戦略**
- この問題を解くために必要な準備
- 推奨される学習期間
- 重点的に取り組むべき問題タイプ
- 時間配分のアドバイス
- 類似問題の探し方・対策法

**8. 総合評価と適性**
- このPDFの総合的な評価（A+〜F）
- どのような生徒に適しているか
- 使用するのに最適な時期
- 期待される学習効果
- 改善点や注意点

**9. 詳細な問題分析**
- 特に印象的な問題の詳細分析
- 良問・悪問の具体例
- 問題作成者の意図の推測
- 受験生が間違いやすいポイント

分析結果は日本語で、各項目を具体的で実用的な内容で詳細に回答してください。数値や具体例を多用し、実際の学習・指導に活用できる情報を提供してください。
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
            max_tokens=8000,  # 詳細分析のためにトークン数を増加
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