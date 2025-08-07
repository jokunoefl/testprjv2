# Render デプロイ トラブルシューティング

## 🚨 デプロイ失敗の対処法

### 1. よくある問題と解決策

#### 問題1: システム依存関係エラー
```
Error: tesseract-ocr not found
Error: poppler-utils not found
```

**解決策**: `requirements-minimal.txt`を使用
```yaml
buildCommand: pip install -r requirements-minimal.txt
```

#### 問題2: ポート設定エラー
```
Error: Invalid value for '--port': '$PORT' is not a valid integer
```

**解決策**: `render_start.py`を使用
```yaml
startCommand: python render_start.py
```

#### 問題3: モジュールインポートエラー
```
Error: No module named 'main'
```

**解決策**: PYTHONPATHを設定
```yaml
envVars:
  - key: PYTHONPATH
    value: /opt/render/project/src
```

### 2. 段階的デプロイ戦略

#### ステップ1: 最小構成でデプロイ
```yaml
buildCommand: pip install -r requirements-minimal.txt
startCommand: uvicorn main:app --host 0.0.0.0 --port $PORT
```

#### ステップ2: システム依存関係を追加
```yaml
buildCommand: |
  apt-get update && apt-get install -y tesseract-ocr poppler-utils
  pip install -r requirements.txt
```

#### ステップ3: Dockerfile使用
```yaml
env: docker
dockerfile: Dockerfile.render
```

### 3. ログの確認方法

#### Render CLI
```bash
render logs
render services
```

#### Render Dashboard
1. サービスを選択
2. 「Logs」タブをクリック
3. エラーメッセージを確認

### 4. 環境変数の確認

必須環境変数：
- `ANTHROPIC_API_KEY`
- `FRONTEND_URL`
- `UPLOAD_DIR`
- `PYTHONPATH`

### 5. 推奨設定

#### 最も確実な設定
```yaml
services:
  - type: web
    name: testprjv2-backend
    env: python
    plan: free
    rootDir: backend
    buildCommand: |
      pip install --upgrade pip
      pip install -r requirements-minimal.txt
      mkdir -p uploaded_pdfs
    startCommand: python render_start.py
    envVars:
      - key: ANTHROPIC_API_KEY
        value: your_actual_api_key
      - key: FRONTEND_URL
        value: https://reactapp-zeta.vercel.app
      - key: UPLOAD_DIR
        value: /opt/render/project/src/uploaded_pdfs
      - key: PYTHONPATH
        value: /opt/render/project/src
      - key: ENVIRONMENT
        value: production
```

### 6. 緊急時の対処法

1. **設定をリセット**: 最もシンプルな設定に戻す
2. **ログを詳細確認**: エラーの根本原因を特定
3. **段階的デプロイ**: 機能を一つずつ追加
4. **代替プラットフォーム**: HerokuやGoogle Cloud Runを検討

## 📞 サポート

問題が解決しない場合は：
1. エラーログの詳細を確認
2. 設定ファイルの内容を再確認
3. 段階的デプロイを試行 