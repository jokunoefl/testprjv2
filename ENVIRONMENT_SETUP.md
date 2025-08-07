# 環境分離セットアップ手順

このドキュメントでは、開発環境と本番環境を分離するための手順を説明します。

## 📁 プロジェクト構造

```
testprjv2/
├── backend/
│   ├── config/
│   │   ├── __init__.py      # 環境設定の初期化
│   │   ├── base.py          # 基本設定クラス
│   │   ├── development.py   # 開発環境設定
│   │   └── production.py    # 本番環境設定
│   ├── main.py              # 更新済み（環境設定を使用）
│   └── ...
├── frontend/
│   └── react_app/
│       ├── env.development.example
│       ├── env.production.example
│       └── ...
├── scripts/
│   ├── start-dev.sh         # 開発環境起動スクリプト
│   └── start-prod.sh        # 本番環境起動スクリプト
├── docker-compose.dev.yml   # 開発環境用Docker Compose
├── docker-compose.prod.yml  # 本番環境用Docker Compose
├── env.development.example  # 開発環境環境変数サンプル
├── env.production.example   # 本番環境環境変数サンプル
└── ...
```

## 🚀 開発環境セットアップ

### 1. 環境変数ファイルの作成

```bash
# 開発環境用の環境変数ファイルを作成
cp env.development.example .env
```

### 2. 開発環境の起動

#### 方法1: スクリプトを使用
```bash
# スクリプトに実行権限を付与
chmod +x scripts/start-dev.sh

# 開発環境を起動
./scripts/start-dev.sh
```

#### 方法2: 手動で起動
```bash
# 仮想環境の作成とアクティベート
python3 -m venv venv
source venv/bin/activate

# 依存関係のインストール
pip install -r requirements.txt

# 開発用ディレクトリの作成
mkdir -p dev_uploaded_pdfs

# データベースの初期化
cd backend
python -c "import database; database.init_db()"

# 開発サーバーの起動
uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

#### 方法3: Dockerを使用
```bash
# 開発環境用Docker Composeで起動
docker-compose -f docker-compose.dev.yml up --build
```

### 3. フロントエンド開発環境の設定

```bash
cd frontend/react_app

# 開発環境用の環境変数ファイルを作成
cp env.development.example .env

# 依存関係のインストール
npm install

# 開発サーバーの起動
npm start
```

## 🏭 本番環境セットアップ

### 1. 環境変数の設定

本番環境では、以下の環境変数を設定する必要があります：

```bash
# 必須環境変数
ENVIRONMENT=production
ANTHROPIC_API_KEY=your_actual_api_key_here
SECRET_KEY=your_secure_secret_key_here

# データベース設定
DATABASE_URL=sqlite:///./production_pdfs.db

# ファイルアップロード設定
UPLOAD_DIR=/app/uploaded_pdfs

# CORS設定
FRONTEND_URL=https://testprjv2.vercel.app

# ログ設定
LOG_LEVEL=WARNING
DEBUG=false
```

### 2. Renderでの本番環境デプロイ

1. **Renderダッシュボードで環境変数を設定**
   - `ENVIRONMENT`: `production`
   - `ANTHROPIC_API_KEY`: 実際のAPIキー
   - `SECRET_KEY`: セキュアなシークレットキー
   - `FRONTEND_URL`: `https://testprjv2.vercel.app`

2. **デプロイ設定**
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### 3. Vercelでのフロントエンドデプロイ

1. **Vercelダッシュボードで環境変数を設定**
   - `REACT_APP_API_URL`: `https://testprjv2-backend.onrender.com`
   - `REACT_APP_ENVIRONMENT`: `production`

### 4. ローカル本番環境のテスト

```bash
# 本番環境用の環境変数ファイルを作成
cp env.production.example .env

# 本番環境スクリプトで起動
chmod +x scripts/start-prod.sh
./scripts/start-prod.sh
```

## 🔧 環境設定の詳細

### 開発環境設定 (`backend/config/development.py`)

- **デバッグ**: 有効
- **ログレベル**: DEBUG
- **データベース**: `dev_pdfs.db`
- **アップロードディレクトリ**: `dev_uploaded_pdfs`
- **APIキー**: 任意（なくても起動可能）
- **セキュリティ**: 緩い設定

### 本番環境設定 (`backend/config/production.py`)

- **デバッグ**: 無効
- **ログレベル**: WARNING
- **データベース**: `production_pdfs.db`
- **アップロードディレクトリ**: `/app/uploaded_pdfs`
- **APIキー**: 必須
- **セキュリティ**: 厳格な設定

## 🔍 環境確認方法

### バックエンド環境確認

```bash
cd backend
python -c "from config import config; print(f'環境: {config.__class__.__name__}'); print(f'DEBUG: {config.DEBUG}'); print(f'LOG_LEVEL: {config.LOG_LEVEL}')"
```

### フロントエンド環境確認

```javascript
// ブラウザのコンソールで実行
console.log('API URL:', process.env.REACT_APP_API_URL);
console.log('Environment:', process.env.REACT_APP_ENVIRONMENT);
console.log('Debug:', process.env.REACT_APP_DEBUG);
```

## 🚨 注意事項

### 開発環境

- APIキーがなくても起動可能
- デバッグ情報が詳細に出力される
- データベースは開発用のものを使用
- ファイルは開発用ディレクトリに保存

### 本番環境

- APIキーとシークレットキーが必須
- デバッグ情報は出力されない
- データベースは本番用のものを使用
- ファイルは本番用ディレクトリに保存
- セキュリティ設定が厳格

## 🔄 環境切り替え

### 開発環境から本番環境へ

```bash
# 環境変数を変更
export ENVIRONMENT=production

# または、.envファイルを変更
echo "ENVIRONMENT=production" > .env
```

### 本番環境から開発環境へ

```bash
# 環境変数を変更
export ENVIRONMENT=development

# または、.envファイルを変更
echo "ENVIRONMENT=development" > .env
```

## 📊 ログとモニタリング

### 開発環境ログ

```bash
# 詳細なログが出力される
tail -f backend/logs/dev.log
```

### 本番環境ログ

```bash
# 重要なログのみ出力される
tail -f backend/logs/prod.log
```

## 🛠️ トラブルシューティング

### よくある問題

1. **環境変数が読み込まれない**
   ```bash
   # .envファイルの存在確認
   ls -la .env
   
   # 環境変数の確認
   echo $ENVIRONMENT
   ```

2. **設定クラスが正しく読み込まれない**
   ```bash
   # 設定の確認
   cd backend
   python -c "from config import config; print(config.__class__.__name__)"
   ```

3. **データベースパスが正しくない**
   ```bash
   # データベースファイルの確認
   ls -la *.db
   ```

### デバッグ方法

```bash
# 環境設定の詳細確認
cd backend
python -c "from config import config; import json; print(json.dumps(config.dict(), indent=2, default=str))"
```
