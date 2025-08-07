import os
from pathlib import Path
from typing import Optional

class BaseConfig:
    """基本設定クラス"""
    
    def __init__(self):
        # プロジェクトのルートディレクトリ
        self.BASE_DIR = Path(__file__).resolve().parent.parent
        
        # データベース設定
        self.DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./pdfs.db")
        
        # ファイルアップロード設定
        self.UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploaded_pdfs")
        
        # CORS設定
        self.FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
        
        # API設定
        self.ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
        
        # セキュリティ設定
        self.SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
        
        # ログ設定
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
        
        # ファイルサイズ制限
        max_size_mb = int(os.getenv("MAX_FILE_SIZE", "50"))
        self.MAX_FILE_SIZE = max_size_mb * 1024 * 1024
        
        # デバッグ設定
        self.DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    
    def validate(self) -> bool:
        """設定の妥当性をチェック"""
        return True
