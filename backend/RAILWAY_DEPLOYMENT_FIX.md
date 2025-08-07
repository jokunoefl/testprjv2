# Railway デプロイ修正ガイド

## 修正内容

### 1. 設定ファイルの修正

#### railway.json
- ヘルスチェックパスを `/docs` に変更
- タイムアウトを300秒に延長
- 起動コマンドを `./start.sh` に変更

#### nixpacks.toml
- 必要なシステムパッケージを追加（tesseract, poppler_utils）
- pipのアップグレードを追加
- アップロードディレクトリの作成を追加

#### main.py
- Railway環境用の設定クラスを追加
- エラーハンドリングを強化
- 環境変数の詳細ログを追加

### 2. 起動スクリプトの追加

`start.sh` スクリプトを作成：
- 環境変数の確認
- アップロードディレクトリの作成
- アプリケーションの起動

## デプロイ手順

### 1. Railwayダッシュボードでの設定

1. **Root Directory設定**
   - Railwayプロジェクトの設定で「Root Directory」を `backend` に設定

2. **環境変数の設定**
   ```
   ANTHROPIC_API_KEY=your_actual_api_key
   FRONTEND_URL=https://your-frontend-url.vercel.app
   PYTHONPATH=/app
   UPLOAD_DIR=/app/uploaded_pdfs
   PORT=8000
   ```

### 2. デプロイ実行

1. Railwayダッシュボードで「Deploy」をクリック
2. デプロイログを監視
3. 以下のログを確認：
   ```
   Railway起動スクリプト開始
   アプリケーション起動中...
   アプリケーション起動完了
   ```

### 3. 動作確認

デプロイ後、以下のURLでアクセス確認：
```bash
curl -I https://your-railway-url.railway.app/docs
```

期待されるレスポンス：
```
HTTP/2 200
```

## トラブルシューティング

### よくあるエラーと解決方法

1. **ModuleNotFoundError**
   - 原因：依存関係のインストール失敗
   - 解決：nixpacks.tomlでpipアップグレードを追加済み

2. **Permission Denied**
   - 原因：start.shの実行権限不足
   - 解決：`chmod +x start.sh` で実行権限を付与済み

3. **Port Already in Use**
   - 原因：ポート設定の問題
   - 解決：`$PORT`環境変数を使用するように修正済み

4. **Database Connection Error**
   - 原因：データベース初期化エラー
   - 解決：エラーハンドリングを追加済み

### ログ確認方法

Railwayダッシュボードで「Deployments」→「View Logs」で詳細ログを確認できます。

## 重要なポイント

- **Root Directory**: `backend`に設定
- **環境変数**: 全て正しく設定
- **起動スクリプト**: `./start.sh`を使用
- **ヘルスチェック**: `/docs`エンドポイントを使用
- **エラーハンドリング**: 強化済み

## 次のステップ

1. Railwayでデプロイを実行
2. ログを確認してエラーがないかチェック
3. フロントエンドからの接続をテスト
4. AI機能の動作確認（APIキー設定後） 