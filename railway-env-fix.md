# Railway 環境変数エラー修正

## 問題
```
Error: Invalid value for '--port': '${PORT:-8001}' is not a valid integer.
```

## 原因
1. Railwayの環境変数展開が正しく動作していない
2. PORT環境変数が設定されていない
3. Railwayの設定に問題がある

## 解決方法

### 修正内容

#### 1. 起動コマンドの簡素化
**修正前:**
```bash
python -m uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8001}
```

**修正後:**
```bash
python -m uvicorn backend.main:app --host 0.0.0.0 --port $PORT
```

#### 2. Railwayダッシュボードでの確認
1. [Railway.app](https://railway.app) にアクセス
2. プロジェクト `testprjv2` を選択
3. 「Variables」タブを確認
4. `PORT`環境変数が自動設定されているか確認

#### 3. 手動でPORT環境変数を設定
Railwayダッシュボードで：
1. 「Variables」タブを選択
2. 「New Variable」をクリック
3. 名前: `PORT`
4. 値: `8001`
5. 「Add」をクリック

### 修正されたファイル

1. **railway.json**
   - 起動コマンド: `python -m uvicorn backend.main:app --host 0.0.0.0 --port $PORT`

2. **Procfile**
   - `web: python -m uvicorn backend.main:app --host 0.0.0.0 --port $PORT`

3. **nixpacks.toml**
   - start: `python -m uvicorn backend.main:app --host 0.0.0.0 --port $PORT`

### 重要なポイント

- **Railwayは通常自動的にPORT環境変数を設定**
- **手動でPORT環境変数を設定する必要がある場合がある**
- **環境変数の展開方法を簡素化**
- **Railwayダッシュボードで環境変数を確認**

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

### トラブルシューティング

#### もしまだエラーが発生する場合：

1. **環境変数の確認**
   - RailwayダッシュボードでPORT環境変数を確認
   - 手動でPORT=8001を設定

2. **起動コマンドの確認**
   - ログで実際の起動コマンドを確認
   - ポート番号が正しく設定されているか確認

3. **代替設定**
   ```bash
   # 固定ポートを使用
   python -m uvicorn backend.main:app --host 0.0.0.0 --port 8001
   ```

4. **Railwayの設定確認**
   - Railwayダッシュボードで環境変数を確認
   - 不要な環境変数を削除

### Railway環境変数の設定手順

#### Step 1: Railwayダッシュボードにアクセス
1. [Railway.app](https://railway.app) にアクセス
2. プロジェクト `testprjv2` を選択

#### Step 2: 環境変数の確認
1. 「Variables」タブを選択
2. `PORT`環境変数が存在するか確認

#### Step 3: 手動設定（必要に応じて）
1. 「New Variable」をクリック
2. 名前: `PORT`
3. 値: `8001`
4. 「Add」をクリック

#### Step 4: 再デプロイ
1. 「Deployments」タブを選択
2. 「Redeploy」をクリック

### 代替設定

#### 固定ポートを使用する場合：
```bash
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8001
```

#### 環境変数の存在確認：
```bash
python -m uvicorn backend.main:app --host 0.0.0.0 --port $PORT
```

### 重要な環境変数

#### 設定すべき環境変数
```bash
PORT=8001
ANTHROPIC_API_KEY=your_actual_api_key
FRONTEND_URL=https://reactapp-zeta.vercel.app
PYTHONPATH=/app
UPLOAD_DIR=/app/uploaded_pdfs
``` 