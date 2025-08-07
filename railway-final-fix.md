# Railway 最終修正（固定ポート使用）

## 問題
```
Error: Invalid value for '--port': '$PORT' is not a valid integer.
```

## 原因
Railwayの環境変数展開が正しく動作していない

## 解決方法

### 修正内容

#### 1. 固定ポートの使用
**修正前:**
```bash
python -m uvicorn backend.main:app --host 0.0.0.0 --port $PORT
```

**修正後:**
```bash
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8001
```

#### 2. 環境変数の簡素化
Railwayダッシュボードで以下の環境変数のみ設定：
```bash
ANTHROPIC_API_KEY=your_actual_api_key
FRONTEND_URL=https://reactapp-zeta.vercel.app
PYTHONPATH=/app
UPLOAD_DIR=/app/uploaded_pdfs
```

**注意**: `PORT`環境変数は設定しない

### 修正されたファイル

1. **railway.json**
   - 起動コマンド: `python -m uvicorn backend.main:app --host 0.0.0.0 --port 8001`

2. **Procfile**
   - `web: python -m uvicorn backend.main:app --host 0.0.0.0 --port 8001`

3. **nixpacks.toml**
   - start: `python -m uvicorn backend.main:app --host 0.0.0.0 --port 8001`

### 重要なポイント

- **固定ポート8001を使用**
- **環境変数の展開に依存しない**
- **確実に動作する設定**
- **Railwayの環境変数問題を回避**

### 期待される結果

- ✅ PORT環境変数エラーが解決
- ✅ アプリケーションが正常に起動
- ✅ 502エラーが解決
- ✅ フロントエンドからの接続が可能

### 確認方法

デプロイ後、以下のURLでアクセス確認：
```bash
curl -I https://testprjv2-production.up.railway.app
curl -I https://testprjv2-production.up.railway.app/docs
# 期待されるレスポンス: HTTP/2 200
```

### Railway環境変数の設定

#### 設定すべき環境変数
```bash
ANTHROPIC_API_KEY=your_actual_api_key
FRONTEND_URL=https://reactapp-zeta.vercel.app
PYTHONPATH=/app
UPLOAD_DIR=/app/uploaded_pdfs
```

#### 設定しない環境変数
```bash
PORT  # 固定ポートを使用するため不要
```

### デプロイ手順

#### Step 1: Railwayダッシュボードでの設定
1. [Railway.app](https://railway.app) にアクセス
2. プロジェクト `testprjv2` を選択
3. 「Variables」タブを選択

#### Step 2: 環境変数の確認
以下の環境変数が設定されているか確認：
- `ANTHROPIC_API_KEY`
- `FRONTEND_URL`
- `PYTHONPATH`
- `UPLOAD_DIR`

#### Step 3: 不要な環境変数の削除
- `PORT`環境変数が設定されている場合は削除

#### Step 4: 再デプロイ
1. 「Deployments」タブを選択
2. 「Redeploy」をクリック

### トラブルシューティング

#### もしまだエラーが発生する場合：

1. **ログの確認**
   - Railwayダッシュボードでログを確認
   - 具体的なエラーメッセージを特定

2. **環境変数の確認**
   - 全ての環境変数が正しく設定されているか確認
   - 特に`ANTHROPIC_API_KEY`が重要

3. **起動時間の確認**
   - アプリケーションの起動に時間がかかる場合
   - ログで起動状況を確認

4. **手動テスト**
   - ローカルでアプリケーションを起動してテスト
   - 依存関係の問題を確認

### 最終確認

デプロイ成功後、以下の点を確認：

1. **バックエンドの動作確認**
   ```bash
   curl -I https://testprjv2-production.up.railway.app
   ```

2. **フロントエンドの接続確認**
   - ブラウザでフロントエンドにアクセス
   - API接続が正常に動作するか確認

3. **ログの確認**
   - Railwayダッシュボードでログを確認
   - エラーがないか確認

### 成功の指標

- ✅ バックエンドが正常に起動
- ✅ フロントエンドからAPI接続が可能
- ✅ PDFアップロード機能が動作
- ✅ AI分析機能が動作 