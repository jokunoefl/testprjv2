import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings

class BaseConfig(BaseSettings):
    """基本設定クラス"""
    
    # プロジェクトのルートディレクトリ
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    
    # データベース設定
    DATABASE_URL: str = "sqlite:///./pdfs.db"
    
    # ファイルアップロード設定
    UPLOAD_DIR: str = "uploaded_pdfs"
    
    # CORS設定
    FRONTEND_URL: str = "http://localhost:3000"
    
    # API設定
    ANTHROPIC_API_KEY: Optional[str] = None
    
    # セキュリティ設定
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    
    # ログ設定
    LOG_LEVEL: str = "INFO"
    
    # ファイルサイズ制限
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
    
    # デバッグ設定
    DEBUG: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    def validate(self) -> bool:
        """設定の妥当性をチェック"""
        return True
