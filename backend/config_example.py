"""
設定ファイルの例
このファイルをconfig.pyにコピーして、実際の値を設定してください。
"""

import os
from pathlib import Path

# プロジェクトのルートディレクトリ
BASE_DIR = Path(__file__).resolve().parent

# 環境変数から読み込み、デフォルト値を設定
class Settings:
    # Claude API設定
    # Anthropicのウェブサイトから取得したAPIキーを設定
    ANTHROPIC_API_KEY: str = "sk-ant-api03-..."  # 実際のAPIキーを設定
    
    # データベース設定
    DATABASE_URL: str = "sqlite:///./pdfs.db"
    
    # ファイルアップロード設定
    UPLOAD_DIR: str = "uploaded_pdfs"
    
    # その他の設定
    DEBUG: bool = False
    
    @classmethod
    def validate(cls):
        """設定の妥当性をチェック"""
        if not cls.ANTHROPIC_API_KEY or cls.ANTHROPIC_API_KEY == "sk-ant-api03-...":
            print("警告: ANTHROPIC_API_KEYが正しく設定されていません。")
            print("config.pyで実際のAPIキーを設定してください。")
            return False
        return True

# 設定インスタンス
settings = Settings() 