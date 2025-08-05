# マルチステージビルド
FROM node:18-alpine AS frontend-builder

WORKDIR /app/frontend
COPY frontend/react_app/package*.json ./
RUN npm ci --only=production

COPY frontend/react_app/ ./
RUN npm run build

# バックエンドビルド
FROM python:3.9-slim AS backend-builder

WORKDIR /app/backend
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 本番環境
FROM python:3.9-slim

WORKDIR /app

# システム依存関係のインストール
RUN apt-get update && apt-get install -y \
    nginx \
    && rm -rf /var/lib/apt/lists/*

# バックエンドのコピー
COPY --from=backend-builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY backend/ ./backend/

# フロントエンドのコピー
COPY --from=frontend-builder /app/frontend/build ./frontend/build

# Nginx設定
COPY nginx.conf /etc/nginx/nginx.conf

# 起動スクリプト
COPY start.sh ./start.sh
RUN chmod +x ./start.sh

EXPOSE 80

CMD ["./start.sh"] 