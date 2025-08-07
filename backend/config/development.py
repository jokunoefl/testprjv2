from .base import BaseConfig

class DevelopmentConfig(BaseConfig):
    """開発環境設定"""
    
    # デバッグ設定
    DEBUG: bool = True
    LOG_LEVEL: str = "DEBUG"
    
    # データベース設定（開発用）
    DATABASE_URL: str = "sqlite:///./dev_pdfs.db"
    
    # ファイルアップロード設定（開発用）
    UPLOAD_DIR: str = "dev_uploaded_pdfs"
    
    # CORS設定（開発用）
    FRONTEND_URL: str = "http://localhost:3000"
    
    # セキュリティ設定（開発用）
    SECRET_KEY: str = "dev-secret-key-for-development-only"
    
    # API設定（開発用）
    ANTHROPIC_API_KEY: str = None  # 開発環境ではAPIキーがなくても起動可能
    
    def validate(self) -> bool:
        """開発環境設定の妥当性をチェック"""
        if not self.ANTHROPIC_API_KEY:
            print("開発環境: ANTHROPIC_API_KEYが設定されていません")
            print("AI機能は使用できませんが、アプリケーションは起動します")
        return True

# 開発環境設定のインスタンス
development_config = DevelopmentConfig()
