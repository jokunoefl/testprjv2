import os
from .base import BaseConfig

class DevelopmentConfig(BaseConfig):
    """開発環境設定"""
    
    def __init__(self):
        super().__init__()
        
        # デバッグ設定
        self.DEBUG = True
        self.LOG_LEVEL = "DEBUG"
        
        # データベース設定（開発用）
        self.DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./dev_pdfs.db")
        
        # ファイルアップロード設定（開発用）
        self.UPLOAD_DIR = os.getenv("UPLOAD_DIR", "dev_uploaded_pdfs")
        
        # CORS設定（開発用）
        self.FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
        
        # セキュリティ設定（開発用）
        self.SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-for-development-only")
        
        # API設定（開発用）
        self.ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")  # 開発環境ではAPIキーがなくても起動可能
    
    def validate(self) -> bool:
        """開発環境設定の妥当性をチェック"""
        if not self.ANTHROPIC_API_KEY:
            print("開発環境: ANTHROPIC_API_KEYが設定されていません")
            print("AI機能は使用できませんが、アプリケーションは起動します")
        return True

# 開発環境設定のインスタンス
development_config = DevelopmentConfig()
