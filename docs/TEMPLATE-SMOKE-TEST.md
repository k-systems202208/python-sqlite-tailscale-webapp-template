# Template Smoke Test

このドキュメントは、このテンプレートを**第三者・初心者が新しいRepositoryとして使い始めても成立するか**を確認するための受入スモークテストです。

目的はitemsサンプル自体を守ることではありません。**`app/features/items/` を削除しても共通基盤だけでテストとCoverageが成立し、その後に独自featureを追加できること**を確認します。

## 自動CIで確認していること

通常のPython 3.11〜3.14 jobでは、doctor、Ruff、pytest + Coverageまでを確認します。

その後、CIの一時workspace上だけで次を削除します。

```text
app/features/items/
```

削除後に共通テストを再実行します。

```text
python -m pytest --cov=app --cov=scripts.db_tools --cov-report=term-missing --cov-fail-under=80
```

`tests/test_sample_items.py` はitems featureが無い場合にskipされ、core、認証、Migration、doctor、DB tools等が引き続き成功することを確認します。

## 手動で行う第三者利用テスト

テンプレートの大きな構成変更後や、初心者向け導線を変更したときは、以下を一度通すことを推奨します。

### 1. 新しいRepositoryを作る

GitHubで **Use this template** を選択し、テスト用の新しいRepositoryを作成します。

### 2. Cloneして最初の診断を行う

```powershell
python -m scripts.doctor
```

Git / GitHub Desktop自体が初めての場合は [../BEGINNER-GUIDE.md](../BEGINNER-GUIDE.md) を先に読みます。

### 3. GitHub推奨設定を適用する

Windows + GitHub CLI環境:

```powershell
gh auth login
.\scripts\setup-github.ps1
```

確認事項:

- Pull Request必須
- Python 3.11〜3.14とWindows PowerShell 5.1がRequired Check
- Conversation resolution必須
- Linear history
- Squash Merge only
- Force push禁止
- main削除禁止

詳細は [GITHUB-SETUP.md](GITHUB-SETUP.md) を参照してください。

### 4. 開発環境と基準状態を確認する

```powershell
.\scripts\bootstrap.ps1
Copy-Item .env.example .env
.\.venv\Scripts\python.exe -m scripts.doctor
.\scripts\check.ps1
```

必要なら起動します。

```powershell
.\scripts\start.ps1
```

確認URL:

```text
http://127.0.0.1:8000/
http://127.0.0.1:8000/healthz
http://127.0.0.1:8000/readyz
```

### 5. itemsサンプルを削除する

**新しいDBを初期化する前**に次を削除するのが最も分かりやすい確認方法です。

```text
app/features/items/
```

削除後:

```powershell
.\scripts\check.ps1
```

共通基盤だけで成功することを確認します。

> 既にDBへitems Migrationを適用した後にfeatureを削除しても、既存DBの`items`テーブルは自動削除されません。運用開始後のSchema変更は、適用済みMigrationを書き換えず新しいMigrationで行います。

### 6. 小さな独自featureを追加する

例:

```text
app/features/equipment/
├─ __init__.py
├─ routes.py
├─ service.py
├─ templates/equipment/
└─ migrations/
```

`__init__.py` に `register(app)` を用意するとfeature loaderが自動検出します。

設計の詳細は [EXTENDING.md](EXTENDING.md) を参照してください。

最低限確認すること:

- feature固有処理を `app/core/` へ混ぜていない
- Route / Serviceの責務を分離している
- Migration versionが重複していない
- 所有者データではSQLにも認可条件がある
- CSRF / Securityを弱めていない
- feature固有テストを追加した
- `scripts/check` が成功する

### 7. Gitフローを1回通す

```text
Issue
  ↓
Issue番号入りBranch
  ↓
Commit / Push
  ↓
Pull Request
  ↓
Python 3.11〜3.14 + Windows PowerShell 5.1 CI
  ↓
Squash Merge
```

## Tailscale確認

別端末利用が必要なアプリでは、基本開発が成功した後にTailscale Serveも確認します。

```powershell
.\scripts\tailscale-serve.ps1
```

アプリのbind先を `0.0.0.0` へ変更して解決しません。

## 合格条件

- Use this templateから新しいRepositoryを作成できる
- `python -m scripts.doctor` に致命的エラーがない
- 初期状態で `scripts/check` 成功
- items feature削除後も共通pytest + Coverage成功
- 独自feature追加後も `scripts/check` 成功
- Pull Requestの5 Required Jobs成功
- Squash Mergeできる
- 必要な場合はTailscale Serve経由でも利用できる

## 失敗した場合

items削除後に失敗した場合は、**共通基盤がitems固有コードやMigrationを参照していないか**を確認します。

特に確認する場所:

- `app/__init__.py`
- `app/features/__init__.py`
- `app/db.py`
- `tests/test_sample_items.py`
- `tests/test_template_lifecycle.py`
- README / docsの固定パス参照

サンプルを残すことでテストを通すのではなく、共通基盤とsample featureの依存を切り離して修正してください。
