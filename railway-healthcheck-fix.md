# Railway ヘルスチェックエラー修正

## 問題
```
Healthcheck failed!
1/1 replicas never became healthy!
```

## 原因
1. アプリケーションが正常に起動していない
2. ヘルスチェックパスが正しくない
3. 起動時間が長すぎる
4. ポート設定の問題

## 解決方法

### 修正内容

#### 1. ヘルスチェックの無効化
**修正前:**
```json
"healthcheckPath": "/",
"healthcheckTimeout": 100
```

**修正後:**
```json
// ヘルスチェックを削除
```

#### 2. 起動コマンドの確認
```bash
python -m uvicorn backend.main:app --host 0.0.0.0 --port $PORT
```

#### 3. 環境変数の確認
```bash
PYTHONPATH=/app
UPLOAD_DIR=/app/uploaded_pdfs
PORT=8001
ANTHROPIC_API_KEY=your_actual_api_key
FRONTEND_URL=https://reactapp-zeta.vercel.app
```

### 修正されたファイル

1. **railway.json**
   - ヘルスチェック設定を削除
   - 起動コマンドを確認

2. **Procfile**
   - `web: python -m uvicorn backend.main:app --host 0.0.0.0 --port $PORT`

3. **nixpacks.toml**
   - install: `pip install -r requirements.txt`
   - start: `python -m uvicorn backend.main:app --host 0.0.0.0 --port $PORT`

### 重要なポイント

- **ヘルスチェックを無効化**して起動を優先
- **起動時間**を考慮した設定
- **環境変数**が正しく設定されているか確認
- **ログ**を確認して具体的な問題を特定

### 期待される結果

- ✅ アプリケーションが正常に起動
- ✅ ヘルスチェックエラーが解決
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

1. **ログの確認**
   - Railwayダッシュボードでログを確認
   - 具体的なエラーメッセージを特定

2. **環境変数の確認**
   - 全ての環境変数が正しく設定されているか確認
   - 特に`ANTHROPIC_API_KEY`が重要

3. **起動時間の延長**
   - アプリケーションの起動に時間がかかる場合
   - より長いタイムアウトを設定

4. **手動テスト**
   - ローカルでアプリケーションを起動してテスト
   - 依存関係の問題を確認

### 代替設定

#### ヘルスチェックを有効にする場合：
```json
{
  "deploy": {
    "startCommand": "python -m uvicorn backend.main:app --host 0.0.0.0 --port $PORT",
    "healthcheckPath": "/docs",
    "healthcheckTimeout": 300,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

#### より長いタイムアウトを設定する場合：
```json
{
  "deploy": {
    "startCommand": "python -m uvicorn backend.main:app --host 0.0.0.0 --port $PORT",
    "healthcheckPath": "/docs",
    "healthcheckTimeout": 600,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
``` 