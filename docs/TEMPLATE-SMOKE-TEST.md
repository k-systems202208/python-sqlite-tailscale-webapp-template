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

> **Use this templateで作成しても、元RepositoryのRulesetは引き継がれません。** 新Repository側で後述の `scripts/setup-github.ps1` を実行します。

ChatGPT / CodexからGitHub操作を行う場合、GitHub AppのRepository accessが `Only select repositories` になっている環境では、**新しく作成したRepositoryをGitHub連携のアクセス対象へ追加**します。追加しない場合、AIからIssue / Branch / Pull Request等を操作すると403になることがあります。

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

この手順はテンプレート本体ではなく、**Use this templateで作成した新RepositoryのローカルClone内から実行**します。別テンプレートの `setup-github.ps1` やRuleset JSONを流用しません。

確認事項:

- `Protect main` RulesetがActive
- Pull Request必須
- Python 3.11〜3.14とWindows PowerShell 5.1がRequired Check
- Conversation resolution必須
- Linear history
- Squash Merge only
- Force push禁止
- main削除禁止
- bypassなし

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

Migration versionはRepository全体で一意にします。itemsの `002_sample_items.sql` を**一度でも適用した可能性がある場合はversion 2を再利用せず、次の未使用version（例: `003_equipment.sql`）を使う**のが安全です。

最低限確認すること:

- feature固有処理を `app/core/` へ混ぜていない
- Route / Serviceの責務を分離している
- Migration versionが重複していない
- 所有者データではSQLにも認可条件がある
- CSRF / Securityを弱めていない
- feature固有テストを追加した
- `scripts/check` が成功する

### 7. アプリ名・READMEを独自アプリ向けに変更する

テンプレート名やitemsサンプルの説明をそのまま残さず、アプリ名・目的・主要URL・開発開始方法を独自アプリ向けに更新します。

ただしREADMEを短く作り直す場合でも、共通基盤の運用・拡張・受入手順への導線は残します。

最低限、次へのリンクを残すことを推奨します。

- `BEGINNER-GUIDE.md`
- `docs/OPERATIONS.md`
- `docs/EXTENDING.md`
- `docs/TEMPLATE-SMOKE-TEST.md`

共通契約テストがこれらの導線を確認しているため、独自アプリ化で不用意に削除するとCIが検出します。

### 8. Gitフローを1回通す

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
  ↓
main CI
```

PR CI成功後だけでなく、Squash Merge後のmain CIも成功することを確認します。

## 実地テストで確認できた注意点

実際にテンプレートから別Repositoryを作成して第三者利用フローを通した際、次の点が確認されました。

1. **RulesetはUse this templateでは引き継がれない**
   - 新Repositoryで `setup-github.ps1` を実行する必要がある
2. **AIのGitHub連携対象は新Repository作成だけでは増えない場合がある**
   - GitHub Appが選択Repository方式なら新Repositoryを追加する
3. **独自READMEへ置換すると共通ドキュメント導線を落としやすい**
   - `OPERATIONS.md` 等へのリンクが消えると契約テストが失敗する
4. **Migration versionの再利用は避ける**
   - sample versionを適用済みか不明なら次の未使用versionを使う
5. **テンプレートの共通基盤はsample削除後も成立した**
   - 独自feature追加後もPython 3.11〜3.14、Windows PowerShell 5.1、Coverage、sampleless smoke testを通過できた

これらは「失敗を避けるための追加機能」ではなく、テンプレートを第三者へ渡したときの実際の利用手順として維持します。

## Tailscale確認

別端末利用が必要なアプリでは、基本開発が成功した後にTailscale Serveも確認します。

```powershell
.\scripts\tailscale-serve.ps1
```

アプリのbind先を `0.0.0.0` へ変更して解決しません。

## 合格条件

- Use this templateから新しいRepositoryを作成できる
- 必要な場合は新RepositoryをChatGPT / CodexのGitHub連携対象へ追加できる
- 新Repositoryへ `Protect main` Rulesetを適用できる
- `python -m scripts.doctor` に致命的エラーがない
- 初期状態で `scripts/check` 成功
- items feature削除後も共通pytest + Coverage成功
- 独自feature追加後も `scripts/check` 成功
- 独自READMEに共通運用・拡張ドキュメントへの導線がある
- Pull Requestの5 Required Jobs成功
- Squash Mergeできる
- merge後main CIが成功する
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

README変更後だけ失敗する場合は、共通ドキュメントへのリンクを落としていないか確認します。

GitHub設定で詰まる場合は、**実行している `setup-github.ps1` が対象Repository自身のCloneに含まれるものか**、またGitHub App / `gh auth` が対象Repositoryへアクセスできるか確認します。

サンプルを残すことでテストを通すのではなく、共通基盤とsample featureの依存を切り離して修正してください。
