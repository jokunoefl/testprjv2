# 中学受験過去問PDF管理システム

中学受験の過去問PDFを指定したURLから抽出し、データベースに保存するWebアプリケーションです。

## 機能

- **PDFアップロード**: ファイルアップロード・URLダウンロード・Webサイトクローリング
- **PDF一覧表示**: 検索・フィルタリング機能付き
- **PDF表示**: ブラウザ内でPDFを直接表示
- **ファイル名重複チェック**: 同じファイル名のアップロードを防止
- **メタデータ管理**: 学校名・科目・年度の管理

## 技術スタック

### バックエンド
- **FastAPI**: Python Webフレームワーク
- **SQLite**: データベース
- **SQLAlchemy**: ORM
- **BeautifulSoup**: Webスクレイピング
- **httpx**: HTTPクライアント

### フロントエンド
- **React**: JavaScriptライブラリ
- **TypeScript**: 型安全なJavaScript
- **Axios**: HTTPクライアント

## セットアップ

### 前提条件
- Python 3.9+
- Node.js 16+
- npm

### 1. リポジトリのクローン
```bash
git clone <repository-url>
cd testprjv2
```

### 2. バックエンドのセットアップ
```bash
# 仮想環境の作成とアクティベート
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate  # Windows

# 依存関係のインストール
pip install -r requirements.txt

# データベースの初期化
cd backend
python -c "import database; database.init_db()"
```

### 3. フロントエンドのセットアップ
```bash
cd frontend/react_app
npm install
```

### 4. アプリケーションの起動

#### バックエンド（FastAPI）
```bash
cd backend
source ../venv/bin/activate
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

#### フロントエンド（React）
```bash
cd frontend/react_app
npm start
```

## 使用方法

### 開発環境

1. **ブラウザでアクセス**: `http://localhost:3000`
2. **PDFアップロード**: ファイルアップロードまたはURLからダウンロード
3. **Webサイトクローリング**: サイトURLを入力してPDFを自動抽出
4. **PDF一覧**: 保存されたPDFの一覧を表示・検索
5. **PDF表示**: ファイル名をクリックしてPDFを表示

### 本番環境

詳細なデプロイ手順は [DEPLOYMENT.md](./DEPLOYMENT.md) を参照してください。

#### 推奨デプロイ方法

1. **フロントエンド**: Vercel
2. **バックエンド**: Render
3. **データベース**: Render PostgreSQL

#### クイックデプロイ

```bash
# フロントエンド（Vercel）
cd frontend/react_app
vercel --prod

# バックエンド（Render）
# RenderダッシュボードでGitHubリポジトリを接続してデプロイ
```

## API エンドポイント

- `GET /pdfs/`: PDF一覧取得
- `POST /upload_pdf/`: PDFファイルアップロード
- `POST /download_pdf/`: URLからPDFダウンロード
- `POST /crawl_pdfs/`: WebサイトからPDF自動抽出
- `GET /pdfs/{pdf_id}`: 特定のPDFメタデータ取得
- `GET /pdfs/{pdf_id}/view`: PDFファイル表示

## プロジェクト構造

```
testprjv2/
├── backend/
│   ├── main.py          # FastAPIエントリポイント
│   ├── models.py        # SQLAlchemyモデル
│   ├── schemas.py       # Pydanticスキーマ
│   ├── crud.py          # CRUD操作
│   ├── database.py      # データベース接続
│   └── pdf_utils.py     # PDF処理ユーティリティ
├── frontend/
│   └── react_app/
│       ├── src/
│       │   ├── components/
│       │   │   ├── PDFUpload.tsx
│       │   │   ├── PDFList.tsx
│       │   │   └── PDFViewer.tsx
│       │   ├── services/
│       │   │   └── api.ts
│       │   └── types/
│       │       └── index.ts
│       └── package.json
├── uploaded_pdfs/       # アップロードされたPDFファイル
├── requirements.txt     # Python依存関係
└── README.md
```

## ライセンス

MIT License

## 貢献

プルリクエストやイシューの報告を歓迎します。 