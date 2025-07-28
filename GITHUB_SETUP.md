# GitHubリポジトリ作成手順

## 1. GitHubでリポジトリを作成

1. [GitHub](https://github.com) にログイン
2. 右上の「+」ボタンをクリック → 「New repository」を選択
3. 以下の設定でリポジトリを作成：
   - **Repository name**: `testprjv2`
   - **Description**: `中学受験過去問PDF管理システム - FastAPI + React`
   - **Visibility**: Public
   - **Initialize this repository with**: チェックしない（既存のコードがあるため）

## 2. リモートリポジトリを追加

GitHubでリポジトリを作成した後、以下のコマンドを実行：

```bash
# リモートリポジトリを追加
git remote add origin https://github.com/YOUR_USERNAME/testprjv2.git

# メインブランチをプッシュ
git branch -M main
git push -u origin main
```

## 3. 確認

プッシュが完了したら、GitHubのリポジトリページでコードが表示されることを確認してください。

## 注意事項

- `YOUR_USERNAME` を実際のGitHubユーザー名に置き換えてください
- 初回プッシュ時は `-u` オプションを使用して、ローカルブランチとリモートブランチを関連付けます 