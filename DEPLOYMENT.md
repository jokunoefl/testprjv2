# デプロイ手順書

## 🚀 デプロイオプション

### 1. Vercel + Render (推奨)

#### フロントエンド（Vercel）

1. **Vercelアカウント作成**
   ```bash
   npm install -g vercel
   vercel login
   ```

2. **フロントエンドデプロイ**
   ```bash
   cd frontend/react_app
   vercel --prod
   ```

3. **環境変数設定**
   - Vercelダッシュボードで `REACT_APP_API_URL` を設定
   - バックエンドのURLを指定（例: `https://your-backend.onrender.com`）

#### バックエンド（Render）

1. **Renderアカウント作成**
   - [Render.com](https://render.com) にサインアップ

2. **プロジェクト作成**
   - Renderダッシュボードで「New Web Service」を選択
   - GitHubリポジトリを接続

3. **環境変数設定**
   - Renderダッシュボードで以下を設定：
     - `ANTHROPIC_API_KEY`: your_api_key
     - `FRONTEND_URL`: https://your-frontend.vercel.app

4. **デプロイ**
   - 自動デプロイが開始されます

5. **トラブルシューティング**
   - ビルドエラーが発生した場合：
     - Renderダッシュボードでログを確認
   - 依存関係の問題：
     - `requirements.txt`の内容を確認

### 2. Docker + AWS/GCP/Azure

#### AWS EC2 + Docker

1. **EC2インスタンス作成**
   - Ubuntu 20.04 LTS
   - t3.medium以上推奨

2. **Docker環境構築**
   ```bash
   sudo apt update
   sudo apt install docker.io docker-compose
   sudo usermod -aG docker $USER
   ```

3. **アプリケーションデプロイ**
   ```bash
   git clone https://github.com/your-repo/testprjv2.git
   cd testprjv2
   
   # 環境変数設定
   export ANTHROPIC_API_KEY=your_api_key
   export FRONTEND_URL=https://your-domain.com
   
   # Docker Compose起動
   docker-compose up -d
   ```

#### Google Cloud Run

1. **Google Cloud SDK設定**
   ```bash
   gcloud auth login
   gcloud config set project your-project-id
   ```

2. **Dockerイメージビルド・プッシュ**
   ```bash
   docker build -t gcr.io/your-project-id/testprjv2 .
   docker push gcr.io/your-project-id/testprjv2
   ```

3. **Cloud Runデプロイ**
   ```bash
   gcloud run deploy testprjv2 \
     --image gcr.io/your-project-id/testprjv2 \
     --platform managed \
     --region asia-northeast1 \
     --allow-unauthenticated \
     --set-env-vars ANTHROPIC_API_KEY=your_api_key
   ```

### 3. Heroku

#### フロントエンド（Heroku Static Buildpack）

1. **Herokuアプリ作成**
   ```bash
   heroku create your-app-name
   heroku buildpacks:set https://github.com/heroku/heroku-buildpack-static
   ```

2. **static.json設定**
   ```json
   {
     "root": "frontend/react_app/build",
     "routes": {
       "/**": "index.html"
     }
   }
   ```

3. **デプロイ**
   ```bash
   cd frontend/react_app
   npm run build
   git add build/
   git commit -m "Build for production"
   git push heroku main
   ```

#### バックエンド（Heroku）

1. **Herokuアプリ作成**
   ```bash
   heroku create your-backend-name
   ```

2. **環境変数設定**
   ```bash
   heroku config:set ANTHROPIC_API_KEY=your_api_key
   heroku config:set FRONTEND_URL=https://your-frontend.herokuapp.com
   ```

3. **デプロイ**
   ```bash
   cd backend
   git push heroku main
   ```

## 🔧 環境変数設定

### 必須環境変数

- `ANTHROPIC_API_KEY`: Anthropic Claude APIキー
- `FRONTEND_URL`: フロントエンドのURL（CORS設定用）

### オプション環境変数

- `DATABASE_URL`: データベース接続URL
- `UPLOAD_DIR`: アップロードディレクトリパス
- `LOG_LEVEL`: ログレベル

## 📊 監視・ログ

### ログ確認

```bash
# Docker
docker-compose logs -f

# Heroku
heroku logs --tail

# Render
# Renderダッシュボードでログを確認

# Cloud Run
gcloud logging read "resource.type=cloud_run_revision"
```

### ヘルスチェック

- フロントエンド: `https://your-domain.com`
- バックエンド: `https://your-backend.com/docs`

## 🔒 セキュリティ

### SSL/TLS証明書

- Vercel/Railway: 自動でSSL証明書が発行
- 独自ドメイン: Let's Encryptを使用

### 環境変数管理

- 本番環境では必ず環境変数を使用
- APIキーは絶対にコードにハードコーディングしない

## 📈 スケーリング

### 自動スケーリング

- Vercel: 自動スケーリング
- Railway: 手動スケーリング設定可能
- Cloud Run: 自動スケーリング（0-1000インスタンス）

### パフォーマンス最適化

- CDN使用（Vercel/Railway）
- 画像最適化
- コード分割
- キャッシュ戦略

## 🚨 トラブルシューティング

### よくある問題

1. **CORSエラー**
   - フロントエンドURLが正しく設定されているか確認
   - バックエンドのCORS設定を確認

2. **APIキーエラー**
   - 環境変数が正しく設定されているか確認
   - APIキーの権限を確認

3. **データベース接続エラー**
   - データベースURLが正しいか確認
   - ネットワーク接続を確認

### ログ確認方法

```bash
# アプリケーションログ
docker-compose logs app

# Nginxログ
docker-compose exec app tail -f /var/log/nginx/access.log
``` 