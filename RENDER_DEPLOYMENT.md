# Render デプロイ手順書

## 🚀 Renderでのデプロイ（推奨）

### 1. Renderアカウント作成
1. [Render.com](https://render.com) にアクセス
2. GitHubアカウントでサインアップ

### 2. 新しいWeb Service作成
1. Renderダッシュボードで「New +」→「Web Service」
2. GitHubリポジトリを連携
3. リポジトリ `jokunoefl/testprjv2` を選択

### 3. サービス設定
```
Name: testprjv2-backend
Root Directory: backend
Runtime: Python 3
Build Command: |
  python -m venv venv
  source venv/bin/activate
  pip install --upgrade pip
  pip install -r requirements.txt
  mkdir -p uploaded_pdfs
Start Command: |
  source venv/bin/activate
  uvicorn main:app --host 0.0.0.0 --port $PORT
```

**注意**: 
- `requirements.txt`はbackendディレクトリにコピー済みです
- 仮想環境を使用してrootユーザー警告を回避します

### 4. 環境変数設定
```
ANTHROPIC_API_KEY=your_actual_api_key
FRONTEND_URL=https://reactapp-zeta.vercel.app
UPLOAD_DIR=/opt/render/project/src/uploaded_pdfs
```

### 5. デプロイ実行
- 「Create Web Service」をクリック
- 自動デプロイが開始されます

## 🔧 Render用の設定ファイル

### render.yaml
```yaml
services:
  - type: web
    name: testprjv2-backend
    env: python
    plan: free
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: ANTHROPIC_API_KEY
        value: your_actual_api_key
      - key: FRONTEND_URL
        value: https://your-frontend-url.vercel.app
      - key: UPLOAD_DIR
        value: /opt/render/project/src/uploaded_pdfs
```

## 🌐 Herokuでのデプロイ

### 1. Herokuアカウント作成
1. [Heroku.com](https://heroku.com) にアクセス
2. アカウント作成

### 2. Heroku CLIインストール
```bash
# macOS
brew tap heroku/brew && brew install heroku

# ログイン
heroku login
```

### 3. アプリケーション作成
```bash
cd backend
heroku create your-app-name
```

### 4. 環境変数設定
```bash
heroku config:set ANTHROPIC_API_KEY=your_actual_api_key
heroku config:set FRONTEND_URL=https://your-frontend-url.vercel.app
heroku config:set UPLOAD_DIR=/app/uploaded_pdfs
```

### 5. デプロイ
```bash
git add .
git commit -m "Deploy to Heroku"
git push heroku main
```

## ☁️ Google Cloud Runでのデプロイ

### 1. Google Cloud SDK設定
```bash
# SDKインストール
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# プロジェクト設定
gcloud auth login
gcloud config set project your-project-id
```

### 2. Dockerfile作成
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8080
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
```

### 3. デプロイ
```bash
# イメージビルド
gcloud builds submit --tag gcr.io/your-project-id/testprjv2

# Cloud Runデプロイ
gcloud run deploy testprjv2 \
  --image gcr.io/your-project-id/testprjv2 \
  --platform managed \
  --region asia-northeast1 \
  --allow-unauthenticated \
  --set-env-vars ANTHROPIC_API_KEY=your_api_key
```

## 📊 各プラットフォームの比較

| プラットフォーム | 無料プラン | 難易度 | 安定性 | 推奨度 |
|----------------|-----------|--------|--------|--------|
| Render | ✅ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Heroku | ❌ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Google Cloud Run | ✅ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| Vercel | ✅ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |

## 🎯 推奨手順

1. **Render**でデプロイを試す（最も簡単）
2. 問題があれば**Heroku**に移行
3. 本格運用なら**Google Cloud Run**を検討

## 📞 サポート

デプロイで問題が発生した場合は、以下を確認してください：
- 環境変数の設定
- ポート設定
- 依存関係のインストール
- ログの確認

## ⚠️ よくある警告と対処法

### pip警告について
```
WARNING: Running pip as the 'root' user can result in broken permissions...
```
この警告は、Renderのビルド環境でrootユーザーとしてpipを実行する際に表示されます。上記の設定では仮想環境を使用することでこの警告を回避しています。この警告は実際のデプロイには影響しませんが、より適切な設定を推奨します。

**対処法**:
- 仮想環境を使用する（上記の設定で対応済み）
- `--user`フラグを使用する
- 警告は無視して問題なし 