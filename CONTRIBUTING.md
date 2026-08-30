# コントリビューションガイド

このテンプレートへの改善提案・バグ修正・機能改善を歓迎します。

## 必須ルール

変更の大小にかかわらず、次のルールを守ります。

1. **mainへの直接Commit / Pushは禁止します。**
2. **mainへ取り込む変更単位ごとにIssueを作成します。**
3. **Issueのタイトル・本文は日本語で記載します。**
4. Issueに対応する作業ブランチを作成します。
5. **ブランチ名にはIssue番号を含めます。**
6. 作業ブランチで変更・テスト・Commit / Pushします。
7. **必ずPull Requestを作成します。**
8. PR本文からIssueを `Closes #番号` で関連付けます。
9. CI成功と差分を確認してからmainへ取り込みます。
10. **mainへの取り込みは原則Squash Mergeとします。**
11. Merge後は対応IssueをCloseし、作業ブランチを削除します。
12. READMEや関連docsへの影響がある場合は同じPRで最新化します。

READMEの誤字、コメント、軽微な文言変更、ドキュメントだけの変更も例外ではありません。

```text
日本語Issue
   ↓
Issue番号入りBranch
   ↓
実装・テスト
   ↓
Commit / Push
   ↓
Pull Request
   ↓
CI・差分確認
   ↓
Squash Merge
   ↓
Issue Close
   ↓
Branch削除
```

## Issue

Issueは変更理由と完了条件を残す作業票です。GitHubで新規Issueを作成するときは `.github/ISSUE_TEMPLATE/change-request.md` を使用します。

原則として **1 Issue = 1 PR** とします。大きな変更は複数Issueへ分割し、1つのPRへ無関係な変更をまとめません。

## ブランチ命名規則

ブランチ名にはIssue番号を必ず含めます。

```text
feat/12-inventory-search
fix/18-user-isolation
docs/23-update-readme
refactor/31-item-service
test/42-add-auth-tests
```

推奨プレフィックス：

- `feat/`：機能追加
- `fix/`：不具合修正
- `docs/`：ドキュメント
- `refactor/`：内部整理
- `test/`：テスト
- `chore/`：設定・依存関係・保守

## Pull Request

PR作成時は `.github/pull_request_template.md` が表示されます。対応Issue、変更内容、テスト、影響範囲、DB・設定・セキュリティ影響、ドキュメント更新状況を記載してください。

PR本文では原則次を使います。

```text
Closes #123
```

これにより、PRがmainへMergeされたとき対応Issueを自動Closeできます。

## Merge方式

**原則Squash Mergeを使用します。**

作業ブランチ内で複数Commitがあっても、mainにはPR単位の1Commitとして取り込みます。これによりmainの履歴をIssue / PR単位で読みやすく保ちます。

例：

```text
PR #24 在庫一覧に検索機能を追加
  ├─ feat: 検索API追加
  ├─ test: テスト追加
  └─ docs: README更新

        ↓ Squash Merge

main
  └─ 在庫一覧に検索機能を追加 (#24)
```

特殊な理由がない限りMerge Commit / Rebase Mergeは使用しません。

## Merge前チェック

- 対応する日本語Issueがある
- ブランチ名にIssue番号が含まれている
- PRとIssueが関連付いている
- mainへの直接Commitではない
- 意図しないファイル変更がない
- `.env` や実データが含まれていない
- 必要なテストが追加・更新されている
- CIが成功している
- 認証・認可を弱めていない
- 他利用者のデータへアクセスできる変更になっていない
- `0.0.0.0` へのbind変更がない
- CSRFやセキュリティヘッダーを壊していない
- DB変更時は既存データへの影響を確認した
- READMEや関連docsが最新になっている
- Squash Mergeを選択している

## Merge後

Merge後は次を行います。

```text
Issue Close（Closesで通常は自動）
   ↓
作業ブランチ削除
   ↓
ローカルmainへ切り替え
   ↓
Fetch / Pull
```

GitHubリポジトリ設定で **Automatically delete head branches** を有効にすることを推奨します。

## GitHub側で推奨するmain保護

ドキュメント上のルールだけでなく、GitHub側でもmainを保護することを推奨します。

最低限、次を設定します。

- Pull Request経由の変更を必須にする
- required status checksでCI成功を必須にする
- conversation resolutionを必須にする
- force pushを禁止する
- branch deletionを禁止する

リポジトリの権限やプランによって表示される設定項目が異なる場合があります。詳細は [docs/DEVELOPMENT-DEPLOYMENT.md](docs/DEVELOPMENT-DEPLOYMENT.md) を参照してください。

## テスト

Windows:

```powershell
.\.venv\Scripts\python.exe -m pytest
```

macOS / Linux:

```bash
.venv/bin/python -m pytest
```

特にlocalhost制約、利用者識別、利用者間データ分離、CSRF、セキュリティヘッダーを壊していないことを確認します。

## Gitへ登録してはいけないもの

```text
.env
data/
SQLiteデータベースファイル
生成された秘密鍵
個人・組織固有のtailnet情報
その他の秘密情報
```

## 変更するときの考え方

このプロジェクトは、誰でも自分用のアプリへ流用できる**小さく分かりやすいテンプレート**であることを重視しています。

便利な機能であっても、すべての利用者が必要としない大きな依存ライブラリや複雑な仕組みを共通基盤へ追加する場合は、その必要性を十分に検討してください。

詳しい構成は [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)、カスタマイズ方法は [docs/CUSTOMIZE.md](docs/CUSTOMIZE.md)、Issue・Pull Request・CI・デプロイ運用は [docs/DEVELOPMENT-DEPLOYMENT.md](docs/DEVELOPMENT-DEPLOYMENT.md)、セキュリティ方針は [docs/SECURITY.md](docs/SECURITY.md) を参照してください。
