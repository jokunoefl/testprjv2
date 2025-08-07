# Railway cdコマンドエラー修正

## 問題
```
Container failed to start
The executable `cd` could not be found.
```

## 原因
Railwayのコンテナ環境で`cd`コマンドが利用できない

## 解決方法

### 修正内容

#### 1. 起動コマンドの変更
**修正前:**
```bash
cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT
```

**修正後:**
```bash
uvicorn backend.main:app --host 0.0.0.0 --port $PORT
```

#### 2. 依存関係インストールの変更
**修正前:**
```bash
cd backend && pip install -r requirements.txt
```

**修正後:**
```bash
pip install -r backend/requirements.txt
```

#### 3. PYTHONPATHの変更
**修正前:**
```bash
PYTHONPATH=/app/backend
```

**修正後:**
```bash
PYTHONPATH=/app
```

### 修正されたファイル

1. **railway.json**
   - startCommand: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
   - PYTHONPATH: `/app`

2. **Procfile**
   - `web: uvicorn backend.main:app --host 0.0.0.0 --port $PORT`

3. **nixpacks.toml**
   - install: `pip install -r backend/requirements.txt`
   - start: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`

### 期待される結果

- ✅ コンテナが正常に起動
- ✅ アプリケーションが正しいポートで起動
- ✅ 502エラーが解決
- ✅ フロントエンドからの接続が可能

### 確認方法

デプロイ後、以下のURLでアクセス確認：
```bash
curl -I https://testprjv2-production.up.railway.app
# 期待されるレスポンス: HTTP/2 200
```

### 重要なポイント

- Railwayでは`cd`コマンドを使用しない
- モジュールパスでディレクトリを指定
- PYTHONPATHを正しく設定
- 依存関係のパスを相対パスで指定 