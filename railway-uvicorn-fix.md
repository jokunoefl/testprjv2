# Railway uvicornエラー修正

## 問題
```
The executable `uvicorn` could not be found.
```

## 原因
1. uvicornが正しくインストールされていない
2. Pythonパスの問題
3. 依存関係のインストールパスが間違っている

## 解決方法

### 修正内容

#### 1. 起動コマンドの変更
**修正前:**
```bash
uvicorn backend.main:app --host 0.0.0.0 --port $PORT
```

**修正後:**
```bash
python -m uvicorn backend.main:app --host 0.0.0.0 --port $PORT
```

#### 2. 依存関係インストールの変更
**修正前:**
```bash
pip install -r backend/requirements.txt
```

**修正後:**
```bash
pip install -r requirements.txt
```

#### 3. 環境変数の追加
```bash
PORT=8001
```

### 修正されたファイル

1. **railway.json**
   - startCommand: `python -m uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
   - 環境変数: `PORT=8001`

2. **Procfile**
   - `web: python -m uvicorn backend.main:app --host 0.0.0.0 --port $PORT`

3. **nixpacks.toml**
   - install: `pip install -r requirements.txt`
   - start: `python -m uvicorn backend.main:app --host 0.0.0.0 --port $PORT`

### 重要なポイント

- **`python -m uvicorn`**を使用してモジュールとして実行
- **requirements.txt**はプロジェクトルートにある
- **PYTHONPATH**を正しく設定
- **PORT**環境変数を明示的に設定

### 期待される結果

- ✅ uvicornが正しく実行される
- ✅ アプリケーションが正常に起動
- ✅ 502エラーが解決
- ✅ フロントエンドからの接続が可能

### 確認方法

デプロイ後、以下のURLでアクセス確認：
```bash
curl -I https://testprjv2-production.up.railway.app
# 期待されるレスポンス: HTTP/2 200
```

### トラブルシューティング

#### もしまだエラーが発生する場合：

1. **依存関係の確認**
   - requirements.txtにuvicornが含まれているか確認
   - バージョンの互換性を確認

2. **Pythonバージョンの確認**
   - Python 3.9が使用されているか確認
   - 必要に応じてバージョンを変更

3. **手動インストール**
   ```bash
   pip install uvicorn fastapi
   ```

4. **代替起動方法**
   ```bash
   python backend/main.py
   ``` 