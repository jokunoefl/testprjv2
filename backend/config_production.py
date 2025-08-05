import os
from pydantic_settings import BaseSettings

class ProductionSettings(BaseSettings):
    # データベース設定
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./data/production.db")
    
    # アップロード設定
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "/app/uploaded_pdfs")
    
    # API設定
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY")
    
    # CORS設定
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")
    
    # セキュリティ設定
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    
    # ログ設定
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # ファイルサイズ制限
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", "50")) * 1024 * 1024  # 50MB
    
    def validate(self) -> bool:
        """設定の検証"""
        if not self.ANTHROPIC_API_KEY:
            print("警告: ANTHROPIC_API_KEYが設定されていません")
            return False
        return True

# 本番環境設定のインスタンス
production_settings = ProductionSettings() 