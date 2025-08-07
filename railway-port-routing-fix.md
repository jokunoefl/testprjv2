# Railway ポートルーティング問題修正

## 問題
- バックエンドは正常に起動（ポート8001）
- しかし502エラーが発生
- フロントエンドからの接続エラー

## 原因
Railwayは`$PORT`環境変数を使用してアプリケーションを起動し、そのポートでルーティングを行います。固定ポートを使用すると、Railwayのルーティングシステムと競合します。

## 解決方法

### 修正内容

#### 1. 起動コマンドの修正
**修正前:**
```bash
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8001
```

**修正後:**
```bash
python -m uvicorn backend.main:app --host 0.0.0.0 --port $PORT
```

#### 2. Railwayダッシュボードでの設定
Railwayダッシュボードで以下の環境変数を確認：

**必須環境変数:**
```bash
ANTHROPIC_API_KEY=your_actual_api_key
FRONTEND_URL=https://reactapp-zeta.vercel.app
PYTHONPATH=/app
UPLOAD_DIR=/app/uploaded_pdfs
```

**注意:** `PORT`環境変数は手動で設定しない（Railwayが自動設定）

### 修正されたファイル

1. **railway.json**
   - 起動コマンド: `python -m uvicorn backend.main:app --host 0.0.0.0 --port $PORT`

2. **Procfile**
   - `web: python -m uvicorn backend.main:app --host 0.0.0.0 --port $PORT`

3. **nixpacks.toml**
   - start: `python -m uvicorn backend.main:app --host 0.0.0.0 --port $PORT`

### 重要なポイント

- **Railwayは`$PORT`環境変数を使用してルーティング**
- **固定ポートは使用しない**
- **Railwayが自動的にPORT環境変数を設定**
- **手動でPORT環境変数を設定すると競合が発生**

### 期待される結果

- ✅ バックエンドがRailwayの正しいポートで起動
- ✅ 502エラーが解決
- ✅ フロントエンドからの接続が可能
- ✅ Railwayのルーティングが正常に動作

### 確認方法

デプロイ後、以下のURLでアクセス確認：
```bash
curl -I https://testprjv2-production.up.railway.app
curl -I https://testprjv2-production.up.railway.app/docs
# 期待されるレスポンス: HTTP/2 200
```

### Railway環境変数の設定手順

#### Step 1: Railwayダッシュボードにアクセス
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
- `PORT`環境変数が手動設定されている場合は削除
- Railwayが自動的に設定するため

#### Step 4: 再デプロイ
1. 「Deployments」タブを選択
2. 「Redeploy」をクリック

### トラブルシューティング

#### もしまだエラーが発生する場合：

1. **ログの確認**
   - Railwayダッシュボードでログを確認
   - 実際の起動ポートを確認

2. **環境変数の確認**
   - `PORT`環境変数が手動設定されていないか確認
   - 他の環境変数が正しく設定されているか確認

3. **起動コマンドの確認**
   - ログで実際の起動コマンドを確認
   - `$PORT`が正しく展開されているか確認

4. **Railwayの設定確認**
   - Railwayダッシュボードでプロジェクト設定を確認
   - ルーティング設定を確認

### 成功の指標

- ✅ バックエンドが正常に起動
- ✅ Railwayのルーティングが動作
- ✅ フロントエンドからAPI接続が可能
- ✅ PDFアップロード機能が動作
- ✅ AI分析機能が動作

### 重要な注意点

**Railwayの動作原理:**
1. Railwayは`$PORT`環境変数を自動設定
2. アプリケーションは`$PORT`で起動
3. Railwayはそのポートでルーティング
4. 固定ポートを使用すると競合が発生

**正しい設定:**
- 起動コマンド: `--port $PORT`
- 環境変数: `PORT`は手動設定しない
- Railwayが自動的に管理 