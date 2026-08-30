# 開発・CI・ローカル反映・デプロイ運用

> **この文書の役割：作った変更をどう管理・検証・反映するか**
>
> 開発開始後の日常運用を扱います。Issue、Branch、Commit / Push、Pull Request、GitHub Actions（CI）、Squash Merge、ローカル稼働PCへのPull、Release、将来の自動デプロイが対象です。
>
> **前の段階**：自分用リポジトリや初回起動がまだ → [新規開発スタートガイド](GETTING-STARTED.md)
>
> **別の話**：DB・業務処理・API・画面をどう実装するか → [カスタマイズガイド](CUSTOMIZE.md)

---

## 1. 最重要ルール

このテンプレートでは次を必須とします。

1. **mainへの直接Commit / Pushは禁止する。**
2. **変更の大小にかかわらずIssueを作成する。**
3. **Issueのタイトルと本文は日本語で記載する。**
4. **ブランチ名にはIssue番号を含める。**
5. 変更・テスト・Commit / Pushは作業ブランチで行う。
6. **必ずPull Requestを作成する。**
7. PR本文から `Closes #Issue番号` でIssueを関連付ける。
8. CI成功、差分、影響範囲、README / docsを確認してから取り込む。
9. **mainへの取り込みは原則Squash Mergeとする。**
10. Merge後はIssueをCloseし、作業ブランチを削除する。

READMEの誤字、コメント、1文字の修正、ドキュメントだけの変更も例外ではありません。

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

---

## 2. なぜこの運用にするのか

目的は手順を増やすことではなく、mainを常に追跡可能な状態に保つことです。

```text
Issue    = なぜ変更するのか
Branch   = どの作業か
PR       = 何を変更したのか
CI       = 自動テストが通ったか
Merge    = 正式にmainへ入れた変更
```

ChatGPT、Codex、GitHub Desktop、手動編集など複数の作業経路があっても、GitHub上では同じ流れへ統一できます。

---

## 3. GitHubとローカルPCの役割

```text
GitHub
  ├─ main：正式なソースコード
  ├─ 日本語Issue：変更理由・完了条件
  ├─ 作業Branch：変更中のコード
  ├─ Pull Request：差分・レビュー単位
  ├─ GitHub Actions：CI
  └─ Release：将来の正式配布単位

開発PC
  ├─ ソース編集
  ├─ ローカルテスト
  └─ 作業BranchへのCommit / Push

稼働PC
  ├─ Python / Flask
  ├─ SQLite（data/app.db）
  ├─ .env
  ├─ Tailscale Serve
  └─ 実際に利用するWebアプリ
```

GitHub上の変更は稼働PCへ自動反映されません。Merge後にPullして初めてローカルへ反映されます。

---

# Issue運用

## 4. Issueは変更の開始点

Issueは不具合専用ではなく、**mainへ入れる変更の目的と完了条件を記録する作業票**として使います。

対象例：

- 新機能
- 不具合修正
- リファクタリング
- DB変更
- テスト追加
- README / docs更新
- 誤字修正
- 設定変更
- 依存ライブラリ更新
- セキュリティ変更

軽微だからIssueを省略する、という例外は設けません。

GitHubでIssueを作成するときは `.github/ISSUE_TEMPLATE/change-request.md` を利用します。

---

## 5. Issueは日本語で書く

タイトル例：

```text
在庫一覧に検索機能を追加する
CSRFエラー発生時の表示を修正する
READMEの初期設定手順を修正する
```

本文では最低限、次を明確にします。

```text
目的
対応内容
影響範囲
完了条件
```

実装方法が完全に決まっていなくても構いません。「なぜ変更するのか」「何をもって完了か」は分かるようにします。

---

## 6. 原則1 Issue = 1 PR

```text
Issue #25
   ↓
feat/25-inventory-search
   ↓
Pull Request
   ↓
Squash Merge
   ↓
main
```

大きすぎるIssueは分割します。1つのPRへ無関係な変更をまとめません。

---

# Branch / Commit / Push

## 7. ブランチ名にはIssue番号を入れる

ブランチ名の基本形：

```text
種別/Issue番号-短い説明
```

例：

```text
feat/25-inventory-search
fix/31-csrf-error
docs/42-readme-setup
refactor/50-item-service
test/61-user-isolation
chore/70-update-dependencies
```

推奨種別：

- `feat/`：機能追加
- `fix/`：不具合修正
- `docs/`：ドキュメント
- `refactor/`：内部整理
- `test/`：テスト
- `chore/`：設定・依存関係・保守

Issue番号が入っていることで、Branch → Issueをすぐ追跡できます。

---

## 8. GitHub Desktopでブランチを作る

```text
mainへ切り替え
   ↓
Fetch origin / Pull origin
   ↓
Current branch
   ↓
New branch
   ↓
feat/25-inventory-search などを作成
```

mainを最新化してからブランチを作ります。

---

## 9. main上で変更してしまった場合

Commit前なら、作業ブランチを作成してからCommitします。

ローカルmainへCommitしてしまっても、**そのままPushしません。** 作業ブランチへCommitを移し、mainをリモートと同じ状態へ戻してからPRを作ります。

---

## 10. Commit / Push

作業ブランチでローカルテスト後にCommitします。

例：

```text
feat: 在庫検索APIを追加
test: 在庫検索テストを追加
docs: 在庫検索の説明を追加
```

作業ブランチでは複数Commitになって構いません。最終的にSquash Mergeするため、mainにはPR単位の1Commitとして残ります。

`.env`、`data/app.db`、秘密情報を含めないことを必ず確認します。

---

# Pull Request運用

## 11. Pull Requestはmainへの唯一の入口

PRは作業ブランチをmainへ取り込むための正式な入口です。このテンプレートでは任意ではなく必須です。

1人開発でも次の価値があります。

- mainを直接変更しない
- Issueと実装を結び付ける
- 差分をまとめて確認する
- CI成功後だけmainへ取り込む
- ChatGPT / Codexによる変更も確認できる
- 後から変更理由を追跡できる

---

## 12. PRを作成する

```text
base: main
compare: feat/25-inventory-search
```

PR作成時は `.github/pull_request_template.md` が表示されます。

最低限、次を確認します。

- 対応Issue
- 変更内容
- テスト
- 影響範囲
- DB変更
- `.env.example` 変更
- requirements変更
- 認証・セキュリティ影響
- README / docs更新

---

## 13. IssueをPRへ関連付ける

原則としてPR本文へ次を記載します。

```text
Closes #25
```

PRがmainへMergeされるとIssueが自動Closeされます。

---

## 14. Draft PR

作業途中で差分やCIを確認したい場合はDraft PRを利用できます。

```text
Draft PR
   ↓
追加修正
   ↓
CI
   ↓
Ready for review
   ↓
最終確認
   ↓
Squash Merge
```

DraftのままMergeしません。

---

# CI・レビュー・Merge

## 15. CI

`.github/workflows/ci.yml` はPushまたはPull Requestで自動実行されます。

現在はUbuntu上で次をテストします。

```text
Python 3.11
Python 3.12
Python 3.13
```

**CI失敗中のPRはmainへMergeしません。**

---

## 16. Merge前チェック

- 対応する日本語Issueがある
- ブランチ名にIssue番号が含まれている
- PR本文からIssueを参照している
- CIが成功している
- 意図しないファイル変更がない
- `.env` や実データが含まれていない
- 必要なテストがある
- DB変更の影響を確認した
- 認証・認可を弱めていない
- localhost制約を壊していない
- CSRF・セキュリティヘッダーを壊していない
- README / docsを最新化した
- Merge方式がSquashになっている

---

## 17. レビューやCIで修正が必要になった場合

同じ作業ブランチへ追加Commit / Pushします。PRは自動更新され、CIも再実行されます。

```text
PR
 ↓
問題発見
 ↓
同じBranchを修正
 ↓
Commit / Push
 ↓
PR更新
 ↓
CI再実行
```

新しいPRを作り直す必要はありません。

---

## 18. Squash Mergeを標準にする

このテンプレートでは、mainへの取り込みは原則 **Squash Merge** とします。

```text
作業Branch
  ├─ feat: API追加
  ├─ test: テスト追加
  └─ docs: README更新

       ↓ Squash Merge

main
  └─ 在庫一覧に検索機能を追加 (#25)
```

利点：

- mainの履歴がPR単位になる
- 1 Commit = 1 Issue / PRに近づく
- 開発途中の細かなCommitをmainへ持ち込まない
- Revert対象を特定しやすい

特殊な理由がない限りMerge Commit / Rebase Mergeは使用しません。

---

## 19. Merge後

`Closes #番号` によりIssueは通常自動Closeされます。

続いて作業ブランチを削除します。

```text
Squash Merge
   ↓
Issue自動Close
   ↓
GitHub上の作業Branch削除
   ↓
ローカルmainへ切り替え
   ↓
Fetch / Pull
   ↓
不要なローカルBranch削除
```

GitHubリポジトリ設定で **Automatically delete head branches** を有効にすると、Merge後の作業ブランチ削除を自動化できます。

---

# GitHub側でルールを強制する

## 20. ドキュメントだけでなくmainを保護する

運用ルールを書くだけでは、誤操作でmainへ直接Pushできる可能性があります。可能ならGitHubの **Branch protection / Rulesets** でmainを物理的に保護します。

推奨設定：

- Pull Requestを経由しない変更を禁止
- required status checksでCI成功を必須化
- unresolved conversationがある場合はMerge不可
- force push禁止
- main削除禁止

リポジトリの権限やGitHubプランによって設定名・利用可能な項目が異なる場合があります。

### 設定画面の目安

GitHubリポジトリで次を開きます。

```text
Settings
  ↓
Rules
  ↓
Rulesets
```

または利用可能な場合：

```text
Settings
  ↓
Branches
  ↓
Branch protection rules
```

対象ブランチを `main` にし、PRとCIを必須にします。

> このリポジトリのドキュメント・テンプレートはルールを示しますが、GitHubアカウント側の保護設定はリポジトリ権限を持つ管理者が確認してください。

---

## 21. Merge後のブランチ自動削除

リポジトリ設定で次を有効にすることを推奨します。

```text
Settings
  ↓
General
  ↓
Pull Requests
  ↓
Automatically delete head branches
```

これにより、Merge済み作業ブランチが増え続けるのを防げます。

---

# ローカル反映

## 22. GitHub上の変更は自動反映されない

ChatGPTやCodexがGitHub上を直接修正しても、ローカルPCは自動更新されません。

```text
GitHub：新版
ローカルPC：旧版
```

Merge後にmainをPullします。

GitHub Desktop：

```text
mainへ切り替え
   ↓
Fetch origin
   ↓
Pull origin
```

CLI：

```bash
git switch main
git pull
```

依存ライブラリが変わった場合は必要に応じてbootstrapを再実行し、アプリを再起動します。

---

## 23. DB変更を含む反映

SQLite構造変更を含む場合は単純なPullだけで済ませません。

```text
DBバックアップ
   ↓
mainをPull
   ↓
必要なDBマイグレーション
   ↓
アプリ起動
   ↓
動作確認
```

DB実装・マイグレーション設計は [カスタマイズガイド](CUSTOMIZE.md) を参照してください。

---

# Release / 将来自動デプロイ

## 24. CI成功と正式リリースを分ける

CI成功は「自動テストを通った」という意味であり、「今すぐ稼働環境へ自動反映してよい」とは限りません。

アプリが安定したら次の流れを推奨します。

```text
Issue
  ↓
PR
  ↓
CI
  ↓
Squash Merge
  ↓
main
  ↓
人がリリース判断
  ↓
GitHub Release
  ↓
稼働PCへ反映
```

将来自動更新する場合も、CI成功そのものではなく **GitHub Release** を更新境界にすることを推奨します。

---

## 25. 自動デプロイは段階的に導入する

```text
Phase 1  手動Pull
Phase 2  新Release通知
Phase 3  利用者が実行する半自動更新
Phase 4  自動更新 + health check + rollback
```

Phase 4では次の流れを想定します。

```text
新Release検知
   ↓
アプリ・DBバックアップ
   ↓
新バージョン取得
   ↓
依存ライブラリ更新
   ↓
DBマイグレーション
   ↓
再起動
   ↓
/healthz
   ↓
成功 → 継続
失敗 → ロールバック
```

---

## 26. 標準フローまとめ

```text
日本語Issue
   ↓
Issue番号入りBranch
   ↓
ChatGPT / Codex / 手動で実装
   ↓
ローカルテスト
   ↓
Commit / Push
   ↓
Pull Request
   ↓
CI
   ↓
差分・影響範囲・docs確認
   ↓
Squash Merge
   ↓
Issue Close
   ↓
Branch削除
   ↓
稼働PCでmainをPull
   ↓
実機確認
```

**mainは完成したPRだけが入る場所**として扱います。これがこのテンプレートのGit運用の基本方針です。
