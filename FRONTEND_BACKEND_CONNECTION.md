# フロントエンドとRenderバックエンドの接続設定

## 🚀 接続設定手順

### 1. 現在の状況
- ✅ **バックエンド**: Renderでデプロイ成功
- ✅ **フロントエンド**: Vercelでデプロイ済み
- 🔧 **接続**: 環境変数設定が必要

### 2. Vercelでの環境変数設定

#### 2.1 Vercelダッシュボードにアクセス
1. [Vercel Dashboard](https://vercel.com/dashboard) にアクセス
2. プロジェクト `reactapp-zeta` を選択

#### 2.2 環境変数を設定
1. **Settings** タブをクリック
2. **Environment Variables** セクションを開く
3. 以下の環境変数を追加：

```
Name: REACT_APP_API_URL
Value: https://testprjv2-backend.onrender.com
Environment: Production
```

#### 2.3 デプロイを実行
1. **Deployments** タブをクリック
2. **Redeploy** をクリックして新しい環境変数で再デプロイ

### 3. ローカル開発環境での設定

#### 3.1 開発用環境変数ファイル
```bash
# frontend/react_app/.env.development
REACT_APP_API_URL=http://localhost:8000
```

#### 3.2 本番用環境変数ファイル
```bash
# frontend/react_app/.env.production
REACT_APP_API_URL=https://testprjv2-backend.onrender.com
```

### 4. 接続確認

#### 4.1 フロントエンドからバックエンドへの接続テスト
1. フロントエンドにアクセス: `https://reactapp-zeta.vercel.app`
2. PDFアップロード機能をテスト
3. バックエンドAPIが正常に応答することを確認

#### 4.2 確認すべきエンドポイント
- `GET /pdfs/` - PDF一覧取得
- `POST /upload_pdf/` - PDFアップロード
- `POST /download_pdf/` - PDFダウンロード
- `GET /docs` - APIドキュメント

### 5. トラブルシューティング

#### 5.1 CORSエラーが発生した場合
バックエンドのCORS設定を確認：
```python
# backend/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://reactapp-zeta.vercel.app",
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### 5.2 接続タイムアウトが発生した場合
- Renderの無料プランでは15分間アクセスがないとスリープ
- 初回アクセス時に少し時間がかかる場合がある

#### 5.3 環境変数が反映されない場合
1. Vercelで再デプロイを実行
2. ブラウザのキャッシュをクリア
3. 開発者ツールでネットワークタブを確認

### 6. 本番環境での注意点

#### 6.1 セキュリティ
- HTTPS通信を使用
- 適切なCORS設定
- 環境変数の適切な管理

#### 6.2 パフォーマンス
- 大きなファイルのアップロード時のタイムアウト設定
- AI分析の長時間処理への対応

### 7. 確認方法

#### 7.1 正常に接続できている場合
- PDFアップロードが成功
- PDF一覧が表示される
- AI分析が実行できる

#### 7.2 エラーが発生した場合
- ブラウザの開発者ツールでエラーログを確認
- ネットワークタブでAPIリクエストの状況を確認
- Renderのログでバックエンドの状況を確認

## 🎯 次のステップ

1. **Vercelで環境変数を設定**
2. **フロントエンドを再デプロイ**
3. **接続テストを実行**
4. **機能テストを実施**

接続が完了したら、フロントエンドからバックエンドの全機能が利用できるようになります！ 