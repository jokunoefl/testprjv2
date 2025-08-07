# Railway デバッグ手順

## 現在の問題
- 502エラーが発生
- アプリケーションが起動しない
- ModuleNotFoundErrorが解決されていない

## 最新の問題（2025-08-07）
- バックエンドは起動している（ログ確認済み）
- しかし502エラーが発生
- Railwayのルーティング問題の可能性

### ポート設定の問題
Railwayログ:
```
INFO:     Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)
```

問題: Railwayは`$PORT`環境変数を使用するが、アプリケーションが8001で起動している

### 解決方法
1. **環境変数の確認**
   - Railwayで`PORT`環境変数が設定されているか確認
   - 通常、Railwayは自動的に`PORT`を設定する

2. **アプリケーションの修正**
   - `main.py`でポート設定を確認
   - `$PORT`環境変数を使用するように修正

3. **Railway設定の確認**
   - Root Directoryが正しく設定されているか
   - ビルドコマンドが正しいか

## 解決手順

### 1. Railwayダッシュボードでの確認
1. [Railway.app](https://railway.app) にアクセス
2. プロジェクト `testprjv2` を選択
3. 「Deployments」タブで最新のデプロイを確認
4. ログを確認してエラーメッセージを特定

### 2. 環境変数の確認
Railwayダッシュボードで以下の環境変数が設定されているか確認：

```bash
ANTHROPIC_API_KEY=your_actual_api_key
FRONTEND_URL=https://reactapp-zeta.vercel.app
PYTHONPATH=/app
UPLOAD_DIR=/app/uploaded_pdfs
PORT=8001  # Railwayが自動設定
```

### 3. 手動デプロイ
Railwayダッシュボードで：
1. 「Settings」タブを選択
2. 「Redeploy」ボタンをクリック
3. デプロイログを監視

### 4. 代替設定
もし上記で解決しない場合：

#### 方法A: ルートディレクトリ変更
- Railwayプロジェクト設定で「Root Directory」を `backend` に設定

#### 方法B: カスタムビルド
- 「Settings」→「Build & Deploy」→「Custom Build Command」
- `cd backend && pip install -r requirements.txt`

#### 方法C: 手動ファイルアップロード
- `backend` フォルダの内容を直接Railwayにアップロード

### 5. ログの確認ポイント
- ビルドログで依存関係のインストールが成功しているか
- 起動ログでPythonパスが正しく設定されているか
- アプリケーションが正常に起動しているか
- **ポート設定が正しいか**

### 6. 緊急時の対処法
1. Railwayプロジェクトを削除
2. 新しいプロジェクトを作成
3. GitHubリポジトリを再連携
4. 環境変数を再設定
5. 手動デプロイ

## 期待される結果
- アプリケーションが正常に起動
- `/docs` エンドポイントがアクセス可能
- フロントエンドからのAPI呼び出しが成功 