# Vercel デプロイ手順

## 1. Vercel CLI のインストール

```bash
npm install -g vercel
```

## 2. Vercel にログイン

```bash
vercel login
```

## 3. 環境変数の設定

VercelダッシュボードまたはCLIで環境変数を設定：

```bash
vercel env add REACT_APP_API_URL
# バックエンドのURLを入力（例: https://your-backend.railway.app）
```

## 4. デプロイ

```bash
# 開発環境へのデプロイ
vercel

# 本番環境へのデプロイ
vercel --prod
```

## 5. トラブルシューティング

### 404エラーが発生する場合

1. **Vercelダッシュボードで設定確認**
   - Functions → Settings → General
   - "Include source files outside of the Root Directory" を有効にする

2. **環境変数の確認**
   ```bash
   vercel env ls
   ```

3. **ビルドログの確認**
   ```bash
   vercel logs
   ```

### ルーティングエラーの場合

1. **vercel.jsonの確認**
   - rewrites設定が正しいか確認
   - 全てのルートが`/index.html`にリダイレクトされているか確認

2. **React Routerの設定確認**
   - BrowserRouterが正しく設定されているか確認
   - 404ページの設定が含まれているか確認

## 6. カスタムドメインの設定

1. Vercelダッシュボードでプロジェクトを選択
2. Settings → Domains
3. カスタムドメインを追加
4. DNS設定を更新

## 7. 自動デプロイの設定

GitHubリポジトリと連携：

1. Vercelダッシュボードでプロジェクトを選択
2. Settings → Git
3. GitHubリポジトリを接続
4. ブランチごとのデプロイ設定を確認

## 8. パフォーマンス最適化

1. **画像最適化**
   - 画像をWebP形式に変換
   - 適切なサイズにリサイズ

2. **コード分割**
   - React.lazy()を使用
   - 動的インポートを活用

3. **キャッシュ設定**
   - 静的ファイルのキャッシュ設定
   - CDNの活用 