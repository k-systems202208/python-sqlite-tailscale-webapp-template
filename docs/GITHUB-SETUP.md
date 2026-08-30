# GitHub初期設定ガイド

> **この文書の役割：テンプレートから作ったリポジトリへ推奨Git運用を設定する**
>
> main保護、Pull Request必須、CI必須、Squash Merge、Merge後の作業ブランチ自動削除を、できるだけ簡単に設定する方法を説明します。

---

## 1. 推奨方法

Windowsでは、リポジトリをCloneしたあとに次を実行します。

```powershell
.\scripts\setup-github.ps1
```

このスクリプトはGitHub CLI（`gh`）を使い、現在のClone先リポジトリを自動判定して設定します。

対象を明示する場合：

```powershell
.\scripts\setup-github.ps1 -Repository owner/repository
```

---

## 2. 事前準備

### GitHub CLIが入っているか確認

```powershell
gh --version
```

見つからない場合、Windowsで `winget` を利用できる環境では次で導入できます。

```powershell
winget install --id GitHub.cli
```

導入後にGitHubへログインします。

```powershell
gh auth login
```

対象リポジトリの設定変更には、そのリポジトリの管理権限が必要です。

---

## 3. 自動設定される内容

### Protect main Ruleset

`github/protect-main.ruleset.json` を使って、Default branch（通常は `main`）へ次を設定します。

- branch削除禁止
- force push禁止
- linear history必須
- Pull Request経由必須
- Required approvals = 0
- 未解決Conversationがある場合はMerge不可
- Merge方式はSquashのみ
- CI `test (3.11)` 必須
- CI `test (3.12)` 必須
- CI `test (3.13)` 必須
- Bypassなし

### Repository設定

次も自動設定します。

- Allow squash merging = ON
- Allow merge commits = OFF
- Allow rebase merging = OFF
- Allow auto-merge = OFF
- Automatically delete head branches = ON
- Always suggest updating pull request branches = ON

---

## 4. 既にProtect mainがある場合

同名の `Protect main` Rulesetが存在する場合、スクリプトは重複作成しません。

```text
Protect mainなし
   ↓
新規作成

Protect mainあり
   ↓
JSON定義で更新
```

そのため、テンプレート側の推奨設定が変わった場合にも、再度スクリプトを実行して設定を揃えられます。

---

## 5. 手動でRulesetをImportする場合

GitHub CLIを使わない場合は、次のJSONを利用できます。

```text
github/protect-main.ruleset.json
```

GitHubの対象リポジトリで、おおむね次の順に開きます。

```text
Settings
  ↓
Rules
  ↓
Rulesets
  ↓
New ruleset
  ↓
Import a ruleset
```

GitHubの画面構成は変更される可能性があります。

JSONをImportしただけでは、Merge方式やMerge後のbranch自動削除などリポジトリ全体の設定までは変更されません。手動の場合は `Settings -> General -> Pull Requests` で次も確認します。

```text
Allow merge commits                 OFF
Allow squash merging                ON
Allow rebase merging                OFF
Allow auto-merge                    OFF
Automatically delete head branches  ON
```

---

## 6. CI名を変更した場合

このテンプレートのRulesetは次のGitHub Actions jobを必須にしています。

```text
test (3.11)
test (3.12)
test (3.13)
```

`.github/workflows/ci.yml` のmatrixやjob名を変更した場合は、`github/protect-main.ruleset.json` 側も合わせて変更してください。

CI名だけを変更してRulesetを更新しないと、CIが成功していてもGitHubが必須チェックを見つけられずMergeできなくなる可能性があります。

---

## 7. エラーになった場合

### `gh` が見つからない

GitHub CLIを導入してください。

### GitHubへログインしていない

```powershell
gh auth login
```

### 管理権限がない

Rulesetの作成・更新には対象リポジトリの管理権限が必要です。リポジトリ所有者または管理者へ依頼してください。

### Ruleset APIでエラーになる

GitHubプラン、所有者種別、権限などによってRulesetsの利用条件が異なる場合があります。その場合は手動ImportまたはGitHub画面から設定してください。

---

## 8. 設定後の標準運用

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
CI 3環境成功
   ↓
Conversation解決
   ↓
Squash Merge
   ↓
Issue自動Close
   ↓
作業Branch自動削除
```

GitHubの設定を自動化しても、IssueやPRの内容確認そのものは省略しません。
