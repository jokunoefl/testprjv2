# Railway 正しい設定手順

## 問題の特定
バックエンドは起動しているが、502エラーが発生している。

### 原因
RailwayのRoot Directory設定が正しくない可能性があります。

## 解決手順

### 1. Railwayダッシュボードでの設定確認

#### Step 1: プロジェクト設定
1. [Railway.app](https://railway.app) にアクセス
2. プロジェクト `testprjv2` を選択
3. 「Settings」タブを選択

#### Step 2: Root Directory設定
1. 「General」セクションを確認
2. **「Root Directory」** を `backend` に設定
3. これにより、Railwayは`backend`フォルダをルートとして扱う

#### Step 3: 環境変数の確認
以下の環境変数が設定されているか確認：
```bash
ANTHROPIC_API_KEY=your_actual_api_key
FRONTEND_URL=https://reactapp-zeta.vercel.app
PYTHONPATH=/app
UPLOAD_DIR=/app/uploaded_pdfs
```

### 2. 再デプロイ
1. 「Settings」タブで「Redeploy」ボタンをクリック
2. デプロイログを監視
3. 以下のログを確認：
   ```
   INFO:     Uvicorn running on http://0.0.0.0:$PORT
   ```

### 3. 期待される結果
- アプリケーションが`$PORT`環境変数で起動
- 502エラーが解決
- フロントエンドからの接続が可能

### 4. トラブルシューティング

#### もしRoot Directory設定で解決しない場合：
1. **新しいプロジェクトを作成**
   - Railwayで新しいプロジェクトを作成
   - GitHubリポジトリを連携
   - Root Directoryを`backend`に設定
   - 環境変数を設定
   - デプロイ

2. **手動ファイルアップロード**
   - `backend`フォルダの内容を直接アップロード
   - 環境変数を設定
   - デプロイ

### 5. 確認方法
デプロイ後、以下のURLでアクセス確認：
```bash
curl -I https://your-railway-url.railway.app
curl -I https://your-railway-url.railway.app/docs
```

期待されるレスポンス：
```
HTTP/2 200
```

## 重要なポイント
- **Root Directory**: `backend`に設定
- **ポート**: `$PORT`環境変数を使用
- **環境変数**: 全て正しく設定
- **デプロイ**: 手動で再デプロイ 