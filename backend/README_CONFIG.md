# 設定ファイルの設定方法

## 1. APIキーの取得

1. [Anthropic Console](https://console.anthropic.com/) にアクセス
2. アカウントを作成またはログイン
3. APIキーを生成
4. 生成されたAPIキーをコピー

## 2. 設定ファイルの作成

### 方法1: config.pyを直接編集

`backend/config.py`を開いて、以下の行を編集：

```python
ANTHROPIC_API_KEY: str = "sk-ant-api03-..."  # 実際のAPIキーを設定
```

### 方法2: 環境変数を使用

ターミナルで環境変数を設定：

```bash
export ANTHROPIC_API_KEY="sk-ant-api03-..."
```

### 方法3: .envファイルを使用（推奨）

1. `backend/.env`ファイルを作成
2. 以下の内容を追加：

```
ANTHROPIC_API_KEY=sk-ant-api03-...
```

## 3. 設定の確認

アプリケーション起動時に設定が正しく読み込まれているか確認されます。

## 4. セキュリティ注意事項

- APIキーをGitにコミットしないでください
- `.env`ファイルは`.gitignore`に追加してください
- 本番環境では環境変数を使用してください

## 5. トラブルシューティング

### 設定エラーが表示される場合

1. APIキーが正しく設定されているか確認
2. 環境変数が正しく設定されているか確認
3. アプリケーションを再起動

### APIキーが無効な場合

1. Anthropic ConsoleでAPIキーの状態を確認
2. 必要に応じて新しいAPIキーを生成 