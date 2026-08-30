# 新規開発スタートガイド

このドキュメントは、このテンプレートから自分のアプリ用リポジトリを作成し、ローカルPCへ配置して、ChatGPT / Codexを使った開発を開始するまでの手順を説明します。

GitやPythonに詳しくない作業者でも進められることを前提にしています。

---

## 1. 全体の流れ

新しいアプリを作るときの基本フローは次のとおりです。

```text
このテンプレート
   ↓
自分のGitHubリポジトリを作成
   ↓
GitHub DesktopでローカルPCへClone
   ↓
初期セットアップ・起動確認
   ↓
ChatGPT / Codexで開発
   ↓
GitHubへCommit / Push
   ↓
GitHub Actions（CI）
   ↓
CI成功
   ↓
ローカルPCへPull
   ↓
実機確認
```

重要なのは、**GitHubをソースコードの基準点にすること**です。

ChatGPT、Codex、自分での編集など、どの方法で変更した場合でも、GitHubへ反映してCIを通したソースを正式な最新版として扱います。

---

## 2. 自分のアプリ用GitHubリポジトリを作る

元テンプレートを直接編集するのではなく、自分のアプリ専用リポジトリを作成します。

たとえば在庫管理アプリなら、次のような名前にします。

```text
my-home-inventory
```

### Template repositoryとして利用できる場合

GitHubのテンプレート画面から **Use this template** を選び、自分のGitHubアカウントに新しいリポジトリを作成します。

この方法では、テンプレートのファイル一式を新しいリポジトリの初期状態として利用できます。

### Template repositoryとして利用しない場合

通常の `git clone` から開始することもできますが、初心者にはTemplate repository方式を推奨します。

---

## 3. GitHub DesktopでローカルPCへCloneする

GitHub Desktopを起動します。

```text
File
 ↓
Clone repository
 ↓
GitHub.com
 ↓
自分の新しいリポジトリを選択
```

Windowsでは、たとえば次のような場所へCloneします。

```text
C:\Users\ユーザー名\Documents\GitHub\my-home-inventory
```

このフォルダーがローカル開発環境のソースコードになります。

実際に稼働するPythonアプリも、このローカルPC上で動作します。

---

## 4. 初回セットアップ

### Windows

対象リポジトリのフォルダーでPowerShellを開きます。

最初にPython仮想環境と必要なライブラリを準備します。

```powershell
.\scripts\bootstrap.ps1
```

次に設定ファイルを作ります。

```powershell
Copy-Item .env.example .env
```

`.env` を自分のアプリ用に変更します。

```text
APP_NAME=自宅在庫管理
LOCAL_OWNER_EMAIL=yourname@example.com
LOCAL_OWNER_NAME=山田太郎
```

アプリを起動します。

```powershell
.\scripts\start.ps1
```

ブラウザで次を開きます。

```text
http://127.0.0.1:8000
```

サンプル画面が表示されれば初期セットアップ成功です。

### macOS / Linux

```bash
./scripts/bootstrap.sh
cp .env.example .env
./scripts/start.sh
```

その後、ブラウザで次を開きます。

```text
http://127.0.0.1:8000
```

---

## 5. `.env` とSQLiteデータはGitHubへ登録しない

ローカルPCには、GitHubへ登録しない情報があります。

代表的なものは次のとおりです。

```text
.env
data/app.db
.venv/
```

`.env` には環境固有の設定や秘密情報が入る可能性があります。

`data/app.db` は実際のアプリデータです。

これらはGitHubへPushせず、各ローカル環境で管理します。

---

## 6. ChatGPT / Codexを使えるようにする

### ChatGPTからGitHubを直接操作する場合

ChatGPTのGitHub連携で、新しく作成したリポジトリへのアクセスを許可します。

GitHub側でChatGPT / Codex Connectorのリポジトリアクセスを限定している場合は、新しいリポジトリを対象へ追加してください。

ChatGPTからリポジトリを確認できれば、README修正、設計確認、ソース修正、CI調査などをGitHub上で進められます。

### Codexで開発する場合

Codexでは、自分の新しいリポジトリを対象として開発します。

ローカル環境を利用する場合は、GitHub DesktopでCloneしたプロジェクトフォルダーを作業対象にします。

Codexに作業を依頼するときも、最初に「このテンプレートをベースにしたアプリである」ことを伝えると、既存の設計意図を維持しやすくなります。

---

## 7. 最初にAIへ伝える内容

新規開発開始時は、いきなりソースを変更するより、まずリポジトリ構成と要件を確認させることを推奨します。

依頼例：

```text
python-sqlite-tailscale-webapp-templateを元に作成した
このリポジトリで新しいアプリを開発します。

Python + Flask + SQLite + Tailscaleの基本構成は維持してください。
まず既存のソースとドキュメントを確認し、
変更すべき箇所と開発方針を整理してください。
```

その後、作りたいアプリを伝えます。

```text
このアプリを自宅在庫管理システムとして開発します。
サンプルのitems機能を在庫管理機能へ置き換えます。
```

---

## 8. 実装前に決めておくこと

AIに実装を依頼する前に、最低限次の内容を整理すると後戻りを減らせます。

- アプリの目的
- 誰が利用するか
- 登録するデータ項目
- 必要な画面
- 検索・絞り込み条件
- 登録・編集・削除のルール
- 利用者ごとにデータを分離するか
- 全利用者で共通データを使うか
- スマートフォンから利用するか
- Tailscaleを利用するか

ChatGPTを要件整理に使い、その結果をCodexへ実装指示として渡す方法も有効です。

---

## 9. サンプル `items` を自分の機能へ置き換える

このテンプレートの `items` は動作確認用サンプルです。

たとえば在庫管理なら、次のように置き換えます。

```text
items
 ↓
inventory
```

主に変更する場所は次のとおりです。

```text
app/schema.sql
app/services/
app/routes.py
app/templates/
app/static/
tests/
```

一方、次の共通基盤は理由なく削除・弱体化しないことを推奨します。

```text
app/auth.py
app/csrf.py
app/security.py
run.py
```

特に次の仕組みは維持してください。

- localhost限定
- Tailscale利用者識別
- 認証・認可
- 利用者単位のデータ分離
- CSRF対策
- セキュリティヘッダー

詳しくは [カスタマイズガイド](CUSTOMIZE.md) と [セキュリティ設計](SECURITY.md) を参照してください。

---

## 10. ChatGPT中心で開発する場合

ChatGPTは、要件整理や設計相談だけでなく、GitHub連携を利用してソースコードを直接修正する用途にも利用できます。

```text
要件をChatGPTへ伝える
       ↓
設計・変更内容を確認
       ↓
ChatGPTがGitHubを修正
       ↓
Commit
       ↓
GitHub Actions
       ↓
CI確認
```

軽微な修正、ドキュメント変更、CIエラーの調査などにも向いています。

ChatGPTがGitHub上を変更した場合、ローカルPCは自動更新されない点に注意してください。

---

## 11. Codex中心で開発する場合

実装範囲が広い場合や複数ファイルをまとめて変更する場合は、Codexを利用する方法があります。

依頼例：

```text
このリポジトリのitemsサンプルをinventory機能へ置き換えてください。
既存の認証、CSRF、セキュリティ構造、localhost限定の設計は維持してください。
必要なテストも修正・追加し、テストが通ることを確認してください。
```

Codexでローカルソースを変更した場合は、変更内容とテスト結果を確認したうえでGitHubへCommit / Pushします。

---

## 12. ChatGPTとCodexを併用する場合

どちらか一方へ統一する必要はありません。

たとえば次のように使い分けられます。

| 作業 | 主な利用先 |
| --- | --- |
| 要件整理 | ChatGPT |
| DB・画面・API設計相談 | ChatGPT |
| 小さなGitHub修正 | ChatGPT |
| ドキュメント整備 | ChatGPT / Codex |
| 本格的な実装 | Codex |
| 複数ファイル変更 | Codex |
| ローカルテスト | Codex / 手動 |
| CI失敗原因の調査 | ChatGPT / Codex |

重要なのは、どちらを使ったかではなく、**最終的にGitHubへ反映しCIで確認すること**です。

```text
ChatGPT ─┐
         ├──→ GitHub ─→ CI
Codex ───┤
         │
手動編集 ┘
```

---

## 13. ローカルでテストする

GitHubへPushする前に、可能な限りローカルでもpytestを実行します。

Windows:

```powershell
.\.venv\Scripts\python.exe -m pytest
```

macOS / Linux:

```bash
.venv/bin/python -m pytest
```

テストが失敗した場合は、その内容をChatGPTまたはCodexへ渡して原因を調査できます。

---

## 14. GitHubへ反映する

ローカルで変更した場合は、GitHub Desktopを利用するとGit操作を分かりやすく行えます。

```text
変更内容を確認
   ↓
Commit
   ↓
Push origin
```

規模が大きくなったら、mainへ直接Pushせず作業ブランチとPull Requestを利用することを推奨します。

```text
featureブランチ
   ↓
修正
   ↓
Push
   ↓
Pull Request
   ↓
CI
   ↓
レビュー
   ↓
mainへマージ
```

---

## 15. CIを確認する

GitHubへPushまたはPull Requestを作成すると、GitHub ActionsのCIが自動実行されます。

現在のテンプレートでは次のPythonバージョンでpytestを実行します。

```text
Python 3.11
Python 3.12
Python 3.13
```

GitHubの **Actions → CI** から結果を確認します。

失敗した場合は、失敗したJobやStepのログを確認します。

ChatGPT / Codexへ「最新CIが失敗しているので原因を確認して修正してください」と依頼して調査することもできます。

---

## 16. GitHub上の変更をローカルPCへ反映する

ChatGPTがGitHubを直接修正した場合など、GitHubの方がローカルPCより新しくなることがあります。

GitHub Desktopで次を実行します。

```text
Fetch origin
   ↓
Pull origin
```

コマンドラインの場合は次のとおりです。

```bash
git pull
```

依存ライブラリが変更された場合は、必要に応じてセットアップを再実行します。

Windows:

```powershell
.\scripts\bootstrap.ps1
```

その後、アプリを再起動します。

```powershell
.\scripts\start.ps1
```

---

## 17. CI成功後も実機確認する

CI成功は重要ですが、それだけで画面や実際の操作がすべて正しいことを保証するものではありません。

ローカルPCでアプリを起動し、ブラウザから実際に確認します。

確認例：

- 画面が正常に表示される
- 登録できる
- 編集できる
- 削除できる
- 検索・絞り込みが正しい
- エラー表示が適切
- 他利用者のデータが見えない
- スマートフォン表示が崩れていない

問題があれば、その現象をChatGPT / Codexへ伝えて次の修正へ進みます。

---

## 18. 開発中の標準サイクル

初期開発では次のサイクルを繰り返します。

```text
要件整理
   ↓
ChatGPT / Codex
   ↓
実装
   ↓
ローカルテスト
   ↓
GitHub
   ↓
CI
   ↓
ローカルへPull
   ↓
実機確認
   ↓
次の要件・修正
```

ChatGPTでGitHubを直接変更した場合は「ローカルテスト」と「GitHub」の順番が前後することがあります。その場合もCI成功後にローカルへPullし、実機確認してください。

---

## 19. 開発が安定した後

初期段階ではCI成功後もローカルPCへ手動でPullする運用を推奨します。

アプリが安定し、テスト、バックアップ、DBマイグレーション、ロールバック方法が確立した後は、更新通知、半自動更新、自動デプロイへ段階的に発展させることができます。

詳しくは [開発・CI・ローカル反映・デプロイ運用](DEVELOPMENT-DEPLOYMENT.md) を参照してください。

---

## 20. 最初に読むドキュメント

初めてこのテンプレートを利用する場合は、次の順で読むことを推奨します。

```text
README.md
   ↓
GETTING-STARTED.md（このドキュメント）
   ↓
CUSTOMIZE.md
   ↓
DEVELOPMENT-DEPLOYMENT.md
   ↓
SECURITY.md
```

構成の背景まで理解したい場合は [ARCHITECTURE.md](ARCHITECTURE.md) も参照してください。

---

## まとめ

このテンプレートでは、開発ツールを一つに固定しません。

```text
ChatGPT
Codex
VS Code等による手動編集
        ↓
      GitHub
        ↓
       CI
        ↓
   ローカルPC
        ↓
     実機確認
```

ChatGPTとCodexを用途に応じて使い分けながら、**GitHubをソースコードの基準点とし、CIと実機確認を通して品質を確認する**ことを標準的な開発方法とします。
