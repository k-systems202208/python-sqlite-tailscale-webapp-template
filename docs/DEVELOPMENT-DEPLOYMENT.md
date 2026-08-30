# 開発・CI・ローカル反映・デプロイ運用

> **この文書の役割：作った変更をどう管理・検証・反映するか**
>
> 開発開始後の日常運用を扱います。GitHub Desktop、Issue、Branch、Commit / Push、Pull Request、GitHub Actions（CI）、mainへのMerge、ローカル稼働PCへのPull、Release、将来の自動デプロイが対象です。
>
> **前の段階**：まだ自分用リポジトリや初回起動ができていない → [新規開発スタートガイド](GETTING-STARTED.md)
>
> **別の話**：DB・業務処理・API・画面をどう実装するか → [カスタマイズガイド](CUSTOMIZE.md)

---

## 1. 最重要ルール

このテンプレートを使った開発では、次を必須ルールとします。

1. **mainへの直接Commit / Pushは禁止する。**
2. **変更の大小にかかわらず、mainへ取り込む変更単位ごとにIssueを作成する。**
3. **Issueのタイトルと本文は日本語で記載する。**
4. Issueに対応する作業ブランチを作成する。
5. 変更は作業ブランチへCommit / Pushする。
6. **必ずPull Requestを作成してmainへ取り込む。**
7. PRから対応Issueを参照し、原則として `Closes #Issue番号` を記載する。
8. CI成功、差分、影響範囲、関連ドキュメントを確認してからmainへMergeする。

READMEの誤字、コメント、1文字の修正、ドキュメントだけの変更なども例外ではありません。

```text
禁止
main → 直接Commit / Push

必須
日本語Issue
   ↓
作業ブランチ
   ↓
Commit / Push
   ↓
Pull Request
   ↓
CI・レビュー
   ↓
mainへMerge
```

---

## 2. 3つのガイドの境界

```text
GETTING-STARTED.md
  開発を始める準備
        ↓
CUSTOMIZE.md
  アプリ機能を作る・変更する
        ↓
DEVELOPMENT-DEPLOYMENT.md ← この文書
  IssueからMerge・稼働PC反映までを管理する
```

---

## 3. GitHubとローカルPCの役割

```text
GitHub
  ├─ 正式なソースコード（main）
  ├─ 日本語Issue
  ├─ 作業Branch
  ├─ Pull Request
  ├─ GitHub Actions（CI）
  └─ Release

開発PC
  ├─ ソース編集
  ├─ ローカルテスト
  └─ 作業ブランチへのCommit / Push

稼働PC
  ├─ Python / Flask
  ├─ SQLite（data/app.db）
  ├─ .env
  ├─ Tailscale Serve
  └─ 実際に利用するWebアプリ
```

mainは常にPRを経由して更新します。開発PCと稼働PCが同じでも、この役割は分けて考えます。

---

## 4. 標準開発サイクル

すべての変更で次の流れを使います。

```text
mainを最新化
   ↓
日本語Issueを作成
   ↓
Issue対応の作業ブランチを作成
   ↓
ChatGPT / Codex / 手動で変更
   ↓
ローカルテスト・動作確認
   ↓
作業ブランチへCommit
   ↓
Push
   ↓
Pull Requestを作成
   ↓
IssueをPRへ関連付け
   ↓
GitHub Actions（CI）
   ↓
差分・影響範囲・docsを確認
   ↓
mainへMerge
   ↓
IssueをClose
   ↓
稼働PCでmainをPull
   ↓
再起動・実機確認
```

---

# Issue運用

## 5. Issueは変更の開始点

Issueは「不具合だけを書く場所」ではありません。この運用では、**mainへ入れる変更の目的と完了条件を記録する作業票**として使います。

対象には次を含みます。

- 新機能
- 不具合修正
- リファクタリング
- DB変更
- テスト追加
- README / docs更新
- 誤字修正
- コメント修正
- 設定変更
- 依存ライブラリ更新
- セキュリティ変更

軽微だからIssueを省略する、という例外は設けません。

---

## 6. Issueは日本語で書く

Issueタイトルと本文は日本語で記載します。

タイトル例：

```text
在庫一覧に検索機能を追加する
CSRFエラー発生時の表示を修正する
READMEの初期設定手順を修正する
Python依存ライブラリを更新する
```

本文の基本形：

```markdown
## 目的
なぜこの変更が必要なのかを記載する。

## 対応内容
- 変更する内容
- 追加する内容
- 削除する内容

## 影響範囲
- 対象機能
- DB変更の有無
- 設定変更の有無
- セキュリティへの影響

## 完了条件
- 何ができれば完了か
- 必要なテスト
- 必要なドキュメント更新
```

Issueの時点で実装方法が完全に決まっている必要はありませんが、「何のための変更か」と「何をもって完了か」は分かるようにします。

---

## 7. 1 Issueと1 PRの基本単位

原則として、1つのIssueに対して1つのPRでmainへ取り込みます。

```text
Issue #25
   ↓
feature/issue-25-inventory-search
   ↓
Pull Request
   ↓
main
```

大きすぎるIssueは複数Issueへ分割します。1つのPRへ無関係なIssueをまとめないようにします。

---

# Branch / Commit / Push

## 8. 作業ブランチを作る

Issue作成後にmainを最新化し、Issueに対応するブランチを作ります。

GitHub Desktop：

```text
main
 ↓
Fetch origin / Pull origin
 ↓
Current branch
 ↓
New branch
```

ブランチ名にはIssue番号を含めることを推奨します。

```text
feature/issue-25-inventory-search
fix/issue-31-csrf-error
docs/issue-42-readme-setup
refactor/issue-50-item-service
```

これによりIssue・Branch・PRの関係を追いやすくなります。

---

## 9. main上で作業を始めてしまった場合

mainへ直接Commitしてはいけません。Commit前に気づいた場合は作業ブランチを作り、変更をそのブランチへ移してからCommitします。

すでにmainへローカルCommitしてしまった場合も、そのままPushせず作業ブランチへ移し、mainを元の状態へ戻してからPRを作成します。

---

## 10. 作業ブランチへCommit / Pushする

ローカルテスト後、作業ブランチへCommitします。

```text
変更確認
  ↓
Commit
  ↓
Push origin
```

Commit例：

```text
feat: 在庫検索APIを追加
test: 在庫検索テストを追加
docs: 在庫検索の説明を追加
```

`.env`、`data/app.db`、秘密情報を含めないことを確認します。

---

# Pull Request運用

## 11. Pull Requestとは

Pull Request（PR）は、作業ブランチの変更をmainへ取り込む前に、差分・CI・影響範囲・変更理由を確認するための正式な入口です。

このプロジェクトではPRは「推奨」ではなく**必須**です。

1人開発でも次の価値があります。

- mainを直接変更しない
- Issueと実装結果を結び付ける
- 差分をまとめて確認する
- CI成功後だけmainへ取り込む
- AIによる変更を人が確認する
- 後から変更理由を追跡する

---

## 12. PRを作成する

作業ブランチをPushしたらPRを作ります。

```text
base: main
compare: feature/issue-25-inventory-search
```

`compare` の変更を `base` へ取り込む、という意味です。

---

## 13. PRタイトルと本文

PRタイトルは変更内容が分かる日本語を推奨します。

```text
在庫一覧に検索機能を追加
READMEの初期設定手順を修正
```

本文には対応Issueを必ず記載します。

```markdown
## 対応Issue
Closes #25

## 変更内容
- 在庫一覧に検索欄を追加
- 名前とカテゴリで部分一致検索できるようにした

## テスト
- pytest実行済み
- PCブラウザで確認済み

## 影響範囲
- app/routes.py
- app/services/inventory.py
- tests/

## 注意事項
- DB変更なし
- .env.example変更なし
- requirements変更なし
- 認証・セキュリティ変更なし

## ドキュメント
- README更新：不要
- 関連docs更新：不要
```

`Closes #25` のように記載すると、PRがmainへMergeされたとき対応Issueを自動的にCloseできます。

---

## 14. Draft PR

作業途中で差分やCIを確認したい場合はDraft PRを利用できます。ただしDraftのままmainへMergeしません。

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
Merge
```

---

# CI・レビュー・Merge

## 15. CIで確認する

`.github/workflows/ci.yml` はPushまたはPull Requestで自動実行されます。

現在はUbuntu上で次をテストします。

```text
Python 3.11
Python 3.12
Python 3.13
```

**CIが失敗しているPRはmainへMergeしません。**

---

## 16. PRで確認すること

Merge前に最低限次を確認します。

- 対応する日本語Issueが存在する
- PR本文からIssueを参照している
- 意図しないファイル変更がない
- `.env` や実データが含まれていない
- 必要なテストがある
- CIが成功している
- DB変更の影響を確認した
- 認証・認可を弱めていない
- localhost制約を壊していない
- CSRF・セキュリティヘッダーを壊していない
- README / docsを最新化した

---

## 17. PRへ追加修正する

レビューやCIで問題が見つかった場合、新しいPRを作り直す必要はありません。同じ作業ブランチを修正してPushします。

```text
PR
 ↓
問題発見
 ↓
同じBranchを修正
 ↓
Commit / Push
 ↓
PRが自動更新
 ↓
CI再実行
```

---

## 18. Mergeする

すべての条件を満たしてからmainへMergeします。

推奨条件：

```text
日本語Issueあり
      ＋
PRとIssueの関連付けあり
      ＋
CI成功
      ＋
差分確認済み
      ＋
必要なREADME / docs更新済み
      ↓
Merge
```

PR単位でmainへ入るため、mainの履歴とIssue / PRの履歴を対応させられます。

---

## 19. Merge後

`Closes #番号` を使っていればIssueは自動Closeされます。自動Closeされない場合は、PRがmainへMergeされたことを確認してIssueをCloseします。

不要になった作業ブランチは削除して構いません。

ローカルPCではmainへ戻してPullします。

```text
mainへ切り替え
   ↓
Fetch origin
   ↓
Pull origin
```

---

# ローカル反映・デプロイ

## 20. GitHub上の変更はローカルへ自動反映されない

ChatGPT / Codex / GitHub上の操作でPRをMergeしても、稼働PCは自動更新されません。

```text
GitHub main：新版
ローカルPC：旧版
```

稼働PCでmainをPullして初めて新版が反映されます。

---

## 21. DB変更を含む場合

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

DB設計そのものは [カスタマイズガイド](CUSTOMIZE.md) を参照してください。

---

## 22. なぜ最初は自動デプロイしないのか

CI成功と「今すぐ稼働環境へ反映して安全」は同じではありません。SQLite、依存ライブラリ、`.env`、起動方法、セキュリティ設定などの変更があるため、初期段階では次を標準とします。

```text
Issue
 ↓
PR
 ↓
CI成功
 ↓
Merge
 ↓
人が確認
 ↓
Pull
 ↓
実機確認
```

---

## 23. 正式リリースと将来の自動デプロイ

アプリが安定したらmainの最新版と正式リリースを分けます。

```text
Issue / PR
   ↓
main
   ↓
CI成功
   ↓
リリース判断
   ↓
GitHub Release
   ↓
正式版として反映
```

自動化は段階的に導入します。

```text
Phase 1  手動Pull
Phase 2  新バージョン通知
Phase 3  半自動更新
Phase 4  自動更新 + ヘルスチェック + ロールバック
```

将来の自動更新では、CI成功そのものではなくGitHub Releaseを更新の境界にすることを推奨します。

---

## 24. 自動デプロイ導入前のチェック

- CIが安定している
- 必要な自動テストが揃っている
- SQLiteバックアップ方法が確立している
- DBマイグレーション方法が確立している
- アプリ再起動方法が決まっている
- `/healthz` で正常性を確認できる
- ロールバック方法がある
- GitHub Releaseで正式版を識別できる

---

## 25. この文書のまとめ

このプロジェクトの変更管理は、変更の大小にかかわらず次へ統一します。

```text
日本語Issue
   ↓
Issue対応Branch
   ↓
実装・テスト
   ↓
Commit / Push
   ↓
Pull Request
   ↓
CI・レビュー
   ↓
mainへMerge
   ↓
Issue Close
   ↓
稼働PCへPull
   ↓
実機確認
```

**mainへの直接Commit / Pushは禁止です。軽微な変更を含むすべての変更をIssueとPRで追跡します。**
