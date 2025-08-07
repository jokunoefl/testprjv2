FROM python:3.9-slim

# システムパッケージのインストール
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 依存関係のインストール
COPY requirements-render.txt .
RUN pip install --no-cache-dir -r requirements-render.txt

# アプリケーションコードのコピー
COPY . .

# アップロードディレクトリの作成
RUN mkdir -p uploaded_pdfs

# ポートの公開
EXPOSE 8080

# アプリケーション起動
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"] 