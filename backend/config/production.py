from .base import BaseConfig

class ProductionConfig(BaseConfig):
    """本番環境設定"""
    
    # デバッグ設定
    DEBUG: bool = False
    LOG_LEVEL: str = "WARNING"
    
    # データベース設定（本番用）
    DATABASE_URL: str = "sqlite:///./production_pdfs.db"
    
    # ファイルアップロード設定（本番用）
    UPLOAD_DIR: str = "/app/uploaded_pdfs"
    
    # CORS設定（本番用）
    FRONTEND_URL: str = "https://testprjv2.vercel.app"
    
    # セキュリティ設定（本番用）
    SECRET_KEY: str = None  # 環境変数から取得
    
    # API設定（本番用）
    ANTHROPIC_API_KEY: str = None  # 環境変数から取得
    
    # ファイルサイズ制限（本番用）
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100MB
    
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
