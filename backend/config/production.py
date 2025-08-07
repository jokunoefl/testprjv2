import os
from .base import BaseConfig

class ProductionConfig(BaseConfig):
    """本番環境設定"""
    
    def __init__(self):
        super().__init__()
        
        # デバッグ設定
        self.DEBUG = False
        self.LOG_LEVEL = "WARNING"
        
        # データベース設定（本番用）
        self.DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./production_pdfs.db")
        
        # ファイルアップロード設定（本番用）
        self.UPLOAD_DIR = os.getenv("UPLOAD_DIR", "/app/uploaded_pdfs")
        
        # CORS設定（本番用）
        self.FRONTEND_URL = os.getenv("FRONTEND_URL", "https://testprjv2.vercel.app")
        
        # セキュリティ設定（本番用）
        self.SECRET_KEY = os.getenv("SECRET_KEY")  # 環境変数から取得
        
        # API設定（本番用）
        self.ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")  # 環境変数から取得
        
        # ファイルサイズ制限（本番用）
        max_size_mb = int(os.getenv("MAX_FILE_SIZE", "100"))
        self.MAX_FILE_SIZE = max_size_mb * 1024 * 1024
    
    def validate(self) -> bool:
        """本番環境設定の妥当性をチェック"""
        if not self.ANTHROPIC_API_KEY:
            print("本番環境: ANTHROPIC_API_KEYが設定されていません")
            return False
        
        if not self.SECRET_KEY or self.SECRET_KEY == "dev-secret-key-change-in-production":
            print("本番環境: SECRET_KEYが適切に設定されていません")
            return False
        
        return True

# 本番環境設定のインスタンス
production_config = ProductionConfig()
