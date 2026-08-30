# 新規開発スタートガイド

> **この文書の役割：開発を始められる状態にするまで**
>
> テンプレートから自分用リポジトリを作り、ローカルPCでサンプルを起動し、ChatGPT / Codexへ最初の開発依頼を出せる状態までを扱います。
>
> **ここでは扱わないこと**
> - DB・画面・APIを具体的にどう作り替えるか → [カスタマイズガイド](CUSTOMIZE.md)
> - 日々のCommit / Push / CI / Pullやリリース運用 → [開発・CI・ローカル反映・デプロイ運用](DEVELOPMENT-DEPLOYMENT.md)

GitやPythonに詳しくない作業者でも、この文書を上から順に進めれば開発を開始できることを目標にしています。

---

## 1. 3つのガイドの使い分け

| 今やりたいこと | 読む文書 |
| --- | --- |
| 新しいアプリを作り始めたい | **この文書：GETTING-STARTED.md** |
| サンプル `items` を自分の機能へ変更したい | [CUSTOMIZE.md](CUSTOMIZE.md) |
| 開発中のGit・CI・Pull・リリース運用を知りたい | [DEVELOPMENT-DEPLOYMENT.md](DEVELOPMENT-DEPLOYMENT.md) |

```text
① 開発開始
GETTING-STARTED.md
  リポジトリ作成 / Clone / 初回起動 / AIへ最初の依頼
        ↓
② アプリを作る
CUSTOMIZE.md
  DB / 業務処理 / API / 画面 / テストを自分用へ変更
        ↓
③ 開発を回す・配布する
DEVELOPMENT-DEPLOYMENT.md
  Commit / Push / CI / Pull / Release / 将来の自動デプロイ
```

---

## 2. 開始前に準備するもの

- GitHubアカウント
- Git
- Python 3.11以上
- GitHub Desktop（推奨）
- 開発用PC
- ChatGPTまたはCodex
- Tailscale（他端末から利用するとき。初回ローカル確認だけなら不要）

---

## 3. 自分のアプリ用GitHubリポジトリを作る

元テンプレートを直接編集せず、自分のアプリ専用リポジトリを作成します。たとえば在庫管理アプリなら `my-home-inventory` のような名前にします。

### Template repositoryとして利用できる場合

GitHubで **Use this template** を選び、自分のGitHubアカウントに新しいリポジトリを作成します。テンプレートのファイル一式を初期状態として利用できるため、この方法を推奨します。

### Template repositoryとして利用しない場合

通常の `git clone` から開始することもできますが、Git履歴や接続先の整理が必要になるため、初心者にはTemplate repository方式を推奨します。

---

## 4. GitHub DesktopでローカルPCへCloneする

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

Windowsでは、たとえば次の場所へCloneします。

```text
C:\Users\ユーザー名\Documents\GitHub\my-home-inventory
```

このフォルダーが開発用ソースコードになります。

---

## 5. 初回セットアップとサンプル起動

### Windows

対象リポジトリのフォルダーでPowerShellを開きます。

```powershell
.\scripts\bootstrap.ps1
Copy-Item .env.example .env
```

`.env` を自分用に変更します。

```text
APP_NAME=自宅在庫管理
LOCAL_OWNER_EMAIL=yourname@example.com
LOCAL_OWNER_NAME=山田太郎
```

起動します。

```powershell
.\scripts\start.ps1
```

### macOS / Linux

```bash
./scripts/bootstrap.sh
cp .env.example .env
./scripts/start.sh
```

ブラウザで `http://127.0.0.1:8000` を開きます。サンプルの `items` 画面が表示されれば、テンプレートそのものが正常に動くことを確認できた状態です。

ここではまだサンプル機能を変更しません。

---

## 6. GitHubへ登録しないローカル情報を理解する

```text
.env
data/app.db
.venv/
```

- `.env`：PC固有設定や秘密情報を含む可能性がある
- `data/app.db`：実際のアプリデータ
- `.venv/`：そのPC用のPython仮想環境

これらは各PCで管理し、GitHubへPushしません。

---

## 7. ChatGPT / Codexからリポジトリを扱えるようにする

### ChatGPTからGitHubを直接扱う場合

ChatGPTのGitHub連携で、新しく作成したリポジトリへのアクセスを許可します。GitHub側でChatGPT / Codex Connectorの対象リポジトリを限定している場合は、新しいリポジトリを追加してください。

### Codexで作業する場合

自分の新しいリポジトリを作業対象にします。ローカル環境を利用する場合は、GitHub DesktopでCloneしたフォルダーを対象にします。

ChatGPTとCodexのどちらか一方へ統一する必要はありません。

```text
ChatGPT
  要件整理 / 設計相談 / GitHub上の軽微な変更 / CI調査

Codex
  本格的な実装 / 複数ファイル変更 / ローカルテスト
```

最終的にはGitHubへ反映するため、どちらを使っても同じ開発サイクルへ合流します。

---

## 8. 最初に作りたいものを整理する

AIへ実装を依頼する前に、最低限次を整理します。

- アプリの目的
- 誰が使うか
- 主に管理したいデータ
- 必要そうな画面
- 利用者ごとにデータを分けるか、共有するか
- スマートフォンから使うか

この段階ではDBの細かなSQLやファイル変更方法まで決める必要はありません。それらはカスタマイズ段階で詰めます。

---

## 9. AIへの最初の依頼

最初は、いきなり実装させるより既存構成を理解させます。

```text
python-sqlite-tailscale-webapp-templateを元に作成した
このリポジトリで新しいアプリを開発します。

Python + Flask + SQLite + Tailscaleの基本構成は維持してください。
まずREADMEとdocs、既存ソースを確認し、
このテンプレートの設計を理解してください。

そのうえで、これから○○アプリとして開発します。
まず要件と変更方針を整理してください。
```

ChatGPTで要件を整理してからCodexへ実装を依頼しても構いません。

---

## 10. ここまでできたらスタート準備完了

- [ ] 自分用GitHubリポジトリを作成した
- [ ] ローカルPCへCloneした
- [ ] `.venv` と `.env` を準備した
- [ ] `http://127.0.0.1:8000` でサンプルを起動できた
- [ ] `.env` / `data/app.db` をGitHubへ登録しないことを理解した
- [ ] ChatGPT / Codexから作業対象を扱える
- [ ] 作りたいアプリの目的を説明できる
- [ ] AIへ最初の要件整理を依頼できた

**ここから先は「準備」ではなく「アプリ開発」です。**

次に [カスタマイズガイド](CUSTOMIZE.md) へ進み、サンプル `items` を実際のアプリへ置き換えてください。

開発中のCommit / Push / CI / Pullについては、必要になった時点で [開発・CI・ローカル反映・デプロイ運用](DEVELOPMENT-DEPLOYMENT.md) を参照してください。
