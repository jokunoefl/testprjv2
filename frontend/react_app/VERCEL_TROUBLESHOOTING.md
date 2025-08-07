# Vercel 404エラー トラブルシューティング

## 現在の状況
Vercelで404エラーが発生している場合の対処法

## 1. Vercelダッシュボードでの設定確認

### Functions → Settings → General
- "Include source files outside of the Root Directory" を **有効** にする
- "Install Command" を確認: `npm install`
- "Build Command" を確認: `npm run build`
- "Output Directory" を確認: `build`

## 2. 環境変数の確認

```bash
# 環境変数を確認
vercel env ls

# 環境変数を設定
vercel env add REACT_APP_API_URL
```

## 3. 手動デプロイ

```bash
# 現在のディレクトリを確認
pwd

# フロントエンドディレクトリに移動
cd frontend/react_app

# 依存関係を再インストール
rm -rf node_modules package-lock.json
npm install

# ビルドテスト
npm run build

# Vercelにデプロイ
vercel --prod
```

## 4. 代替設定ファイル

### vercel.json の代替案

```json
{
  "version": 2,
  "builds": [
    {
      "src": "package.json",
      "use": "@vercel/static-build",
      "config": {
        "distDir": "build"
      }
    }
  ],
  "routes": [
    {
      "src": "/static/(.*)",
      "dest": "/static/$1"
    },
    {
      "src": "/(.*)",
      "dest": "/index.html"
    }
  ]
}
```

## 5. デバッグ手順

### 1. ビルドログの確認
```bash
vercel logs
```

### 2. ローカルビルドテスト
```bash
npm run build
ls -la build/
```

### 3. ファイル構造の確認
```bash
tree build/ -I node_modules
```

## 6. よくある問題と解決策

### 問題1: ビルドが失敗する
**解決策**: 
- Node.jsバージョンを確認
- 依存関係を再インストール
- キャッシュをクリア

### 問題2: ルーティングが動作しない
**解決策**:
- vercel.jsonの設定を確認
- _redirectsファイルの確認
- React Routerの設定確認

### 問題3: 静的ファイルが読み込めない
**解決策**:
- ファイルパスの確認
- ビルド出力の確認
- キャッシュのクリア

## 7. 緊急時の対処法

### 完全リセット
```bash
# Vercelプロジェクトを削除
vercel remove --yes

# 再デプロイ
vercel --prod
```

### 手動ファイルアップロード
1. `npm run build` でビルド
2. `build/` フォルダの内容を手動でVercelにアップロード

## 8. サポート情報

- Vercelドキュメント: https://vercel.com/docs
- React Router: https://reactrouter.com/
- Create React App: https://create-react-app.dev/ 