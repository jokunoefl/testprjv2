# Railway PORT環境変数エラー修正

## 問題
```
Error: Invalid value for '--port': '$PORT' is not a valid integer.
```

## 原因
1. `$PORT`環境変数が正しく展開されていない
2. Railwayの環境変数設定に問題がある
3. 手動でPORT環境変数を設定したことによる競合

## 解決方法

### 修正内容

#### 1. PORT環境変数の削除
**修正前:**
```json
"variables": {
  "PORT": "8001"
}
```

**修正後:**
```json
"variables": {
  // PORT環境変数を削除（Railwayが自動設定）
}
```

#### 2. 起動コマンドの修正
**修正前:**
```bash
python -m uvicorn backend.main:app --host 0.0.0.0 --port $PORT
```

**修正後:**
```bash
python -m uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8001}
```

#### 3. デフォルト値の設定
`${PORT:-8001}` は、`PORT`環境変数が設定されていない場合に8001を使用する

### 修正されたファイル

1. **railway.json**
   - PORT環境変数を削除
   - 起動コマンド: `python -m uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8001}`

2. **Procfile**
   - `web: python -m uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8001}`

3. **nixpacks.toml**
   - start: `python -m uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8001}`

### 重要なポイント

- **Railwayは自動的にPORT環境変数を設定**
- **手動でPORTを設定すると競合が発生**
- **デフォルト値を使用して安全性を確保**
- **環境変数の展開方法を正しく使用**

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
   - RailwayダッシュボードでPORT環境変数が手動設定されていないか確認
   - 手動設定されている場合は削除

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

### Railway環境変数のベストプラクティス

#### 設定すべき環境変数
```bash
ANTHROPIC_API_KEY=your_actual_api_key
FRONTEND_URL=https://reactapp-zeta.vercel.app
PYTHONPATH=/app
UPLOAD_DIR=/app/uploaded_pdfs
```

#### 設定しない環境変数
```bash
PORT  # Railwayが自動設定
```

### 代替設定

#### 固定ポートを使用する場合：
```bash
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8001
```

#### 環境変数の存在確認：
```bash
python -m uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8001}
``` 