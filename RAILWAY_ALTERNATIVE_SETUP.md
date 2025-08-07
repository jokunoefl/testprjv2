# Railway 代替設定手順（Root Directory設定なし）

## 問題
RailwayダッシュボードでRoot Directory設定が見つからない場合の対処法

## 解決方法

### 方法1: プロジェクトルートからの設定（推奨）

#### Step 1: 設定ファイルの配置
プロジェクトルートに以下のファイルを配置：
- `railway.json` - Railway設定
- `Procfile` - 起動コマンド
- `nixpacks.toml` - ビルド設定

#### Step 2: 起動コマンドの修正
```bash
cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT
```

#### Step 3: 環境変数の設定
Railwayダッシュボードで以下を設定：
```bash
ANTHROPIC_API_KEY=your_actual_api_key
FRONTEND_URL=https://reactapp-zeta.vercel.app
PYTHONPATH=/app/backend
UPLOAD_DIR=/app/uploaded_pdfs
```

### 方法2: 新しいプロジェクトの作成

#### Step 1: 現在のプロジェクトを削除
1. Railwayダッシュボードで現在のプロジェクトを削除
2. 新しいプロジェクトを作成

#### Step 2: GitHubリポジトリの連携
1. 「Deploy from GitHub repo」を選択
2. `jokunoefl/testprjv2` を選択
3. デプロイを開始

#### Step 3: 環境変数の設定
デプロイ後、環境変数を設定

### 方法3: 手動ファイルアップロード

#### Step 1: backendフォルダの準備
```bash
# backendフォルダの内容を確認
ls -la backend/
```

#### Step 2: Railwayへのアップロード
1. Railwayダッシュボードで「Upload Files」を選択
2. `backend`フォルダの内容をアップロード
3. 環境変数を設定
4. デプロイ

### 方法4: Railway CLIの使用

#### Step 1: Railway CLIのインストール
```bash
npm install -g @railway/cli
```

#### Step 2: ログイン
```bash
railway login
```

#### Step 3: プロジェクトの初期化
```bash
cd backend
railway init
```

#### Step 4: デプロイ
```bash
railway up
```

## 期待される結果

### 修正後
- ✅ アプリケーションが正しいポートで起動
- ✅ 502エラーが解決
- ✅ フロントエンドからの接続が可能

### 確認方法
```bash
curl -I https://testprjv2-production.up.railway.app
# 期待されるレスポンス: HTTP/2 200
```

## トラブルシューティング

### よくある問題
1. **依存関係のインストール失敗**
   - `requirements.txt`のパスを確認
   - Pythonバージョンの確認

2. **ポート設定の問題**
   - `$PORT`環境変数の確認
   - 起動コマンドの確認

3. **環境変数の未設定**
   - Railwayダッシュボードで環境変数を確認
   - 特に`ANTHROPIC_API_KEY`が重要

### ログの確認ポイント
- ビルドログで依存関係のインストールが成功しているか
- 起動ログで正しいポートで起動しているか
- エラーログで具体的な問題を特定

## 推奨アクション

**方法1（プロジェクトルートからの設定）**を試してください。これが最も確実で簡単な方法です。 