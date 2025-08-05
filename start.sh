#!/bin/bash

# バックエンドの起動
cd /app/backend
python -m uvicorn main:app --host 0.0.0.0 --port 8001 &

# Nginxの起動
nginx -g "daemon off;" 