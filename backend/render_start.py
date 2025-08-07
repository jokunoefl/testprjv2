#!/usr/bin/env python3
"""
Render deployment startup script
"""
import os
import uvicorn

def main():
    # 環境変数の設定
    port = int(os.getenv('PORT', 8080))
    host = '0.0.0.0'
    
    print(f"Starting application on {host}:{port}")
    print(f"Environment: {os.getenv('ENVIRONMENT', 'production')}")
    
    # アプリケーション起動
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        log_level="info"
    )

if __name__ == "__main__":
    main() 