# Vercelフロントエンドデプロイガイド

## 🚀 新規Vercelプロジェクト作成手順

### 1. Vercelダッシュボードでの設定

#### 1.1 プロジェクト作成
1. [Vercel Dashboard](https://vercel.com/dashboard) にアクセス
2. **New Project** をクリック
3. GitHubリポジトリ `jokunoefl/testprjv2` を選択

#### 1.2 プロジェクト設定
以下の設定でプロジェクトを作成：

```
Framework Preset: Create React App
Root Directory: frontend/react_app
Build Command: npm run build
Output Directory: build
Install Command: npm install
```

#### 1.3 環境変数設定
**Environment Variables** セクションで以下を追加：

```
Name: REACT_APP_API_URL
Value: https://testprjv2-backend.onrender.com
Environment: Production
```

### 2. デプロイ設定

#### 2.1 自動デプロイ
- **Auto Deploy**: 有効
- **Branch**: main
- **Framework Preset**: Create React App

#### 2.2 ビルド設定
- **Build Command**: `npm run build`
- **Output Directory**: `build`
- **Install Command**: `npm install`

### 3. プロジェクト構造

```
testprjv2/
├── frontend/
│   └── react_app/          # Vercelのルートディレクトリ
│       ├── src/
│       │   ├── services/
│       │   │   └── api.ts  # API設定
│       │   └── ...
│       ├── package.json
│       ├── vercel.json     # Vercel設定
│       └── ...
└── backend/                # Renderでデプロイ済み
```

### 4. 接続確認

#### 4.1 フロントエンドURL
デプロイ完了後、以下のURLでアクセス可能：
- `https://[project-name].vercel.app`

#### 4.2 バックエンド接続
- **バックエンドURL**: `https://testprjv2-backend.onrender.com`
- **API エンドポイント**: 
  - `GET /pdfs/` - PDF一覧取得
  - `POST /upload_pdf/` - PDFアップロード
  - `GET /docs` - APIドキュメント

### 5. トラブルシューティング

#### 5.1 ビルドエラー
- Node.jsバージョンの確認
- 依存関係のインストール確認
- TypeScriptエラーの修正

#### 5.2 接続エラー
- 環境変数 `REACT_APP_API_URL` の設定確認
- CORS設定の確認
- バックエンドの稼働状況確認

#### 5.3 デプロイエラー
- GitHubリポジトリの権限確認
- Vercelプロジェクトの設定確認
- ビルドログの確認

### 6. 確認方法

#### 6.1 正常に動作している場合
- ✅ フロントエンドが正常に表示される
- ✅ PDF一覧画面が表示される（空の状態）
- ✅ PDFアップロード機能が利用できる
- ✅ コンソールにAPI接続ログが表示される

#### 6.2 エラーが発生した場合
- ブラウザの開発者ツールでエラーログを確認
- Vercelのデプロイログを確認
- ネットワークタブでAPIリクエストの状況を確認

### 7. 次のステップ

1. **Vercelプロジェクト作成**
2. **環境変数設定**
3. **デプロイ実行**
4. **接続テスト**
5. **機能テスト**

## 🎯 期待される結果

デプロイ完了後、以下の機能が利用可能になります：

- **PDF管理**: アップロード、一覧表示、ダウンロード
- **AI分析**: PDFの内容分析
- **問題管理**: 問題の作成、編集、削除
- **ユーザー管理**: ログイン、権限管理

これで、フロントエンドとRenderバックエンドが完全に接続された本格的なWebアプリケーションが完成します！ 