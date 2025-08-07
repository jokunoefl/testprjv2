# Render Docker デプロイ手順書

## 🐳 Dockerfileを使用したRenderデプロイ

### 1. 前提条件
- Renderアカウント
- GitHubリポジトリとの連携
- Dockerfile.renderファイル（準備済み）

### 2. Renderダッシュボードでの設定

#### 2.1 新しいWeb Service作成
1. Renderダッシュボードで「New +」→「Web Service」
2. GitHubリポジトリ `jokunoefl/testprjv2` を選択

#### 2.2 サービス設定
```
Name: testprjv2-backend
Root Directory: backend
Runtime: Docker
Dockerfile: Dockerfile.render
```

#### 2.3 環境変数設定
```
ANTHROPIC_API_KEY=your_actual_api_key
FRONTEND_URL=https://reactapp-zeta.vercel.app
UPLOAD_DIR=/app/uploaded_pdfs
PYTHONPATH=/app
```

### 3. Dockerfile.renderの内容

```dockerfile
FROM python:3.9-slim

# システムパッケージのインストール
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 依存関係のインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードのコピー
COPY . .

# アップロードディレクトリの作成
RUN mkdir -p uploaded_pdfs

# ポートの公開
EXPOSE 8080

# アプリケーション起動
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
```

### 4. デプロイ実行
1. 「Create Web Service」をクリック
2. Dockerイメージのビルドが開始されます
3. ビルド完了後、自動的にデプロイされます

### 5. 利点
- ✅ システム依存関係（tesseract-ocr, poppler-utils）が含まれる
- ✅ 完全に制御された環境
- ✅ ビルドエラーが少ない
- ✅ 本番環境との一貫性

### 6. 注意点
- ビルド時間が若干長くなる
- イメージサイズが大きくなる
- 無料プランでは月間使用量に制限がある

### 7. トラブルシューティング

#### ビルドエラーが発生した場合
1. ログを確認
2. システムパッケージのインストール状況を確認
3. 必要に応じてDockerfileを修正

#### アプリケーションが起動しない場合
1. ポート設定を確認
2. 環境変数の設定を確認
3. ログを詳細に確認

### 8. 確認方法
デプロイ完了後、以下で確認：
- アプリケーションURL: `https://your-app-name.onrender.com`
- APIドキュメント: `https://your-app-name.onrender.com/docs`
- ヘルスチェック: `https://your-app-name.onrender.com/health`

## 🎯 次のステップ
1. デプロイ完了を確認
2. フロントエンドとの連携テスト
3. 本格運用開始 