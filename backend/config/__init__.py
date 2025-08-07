import os
from .development import development_config
from .production import production_config

def get_config():
    """環境に応じた設定を取得"""
    environment = os.getenv("ENVIRONMENT", "development").lower()
    
    if environment == "production":
        return production_config
    else:
        return development_config

# 現在の環境設定
config = get_config()
