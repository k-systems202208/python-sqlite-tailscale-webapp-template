# Python + SQLite + Tailscale ローカルWebアプリ テンプレート

**Python・SQLite・Tailscaleを使って、家庭内・社内・個人用のクローズドなWebアプリを作るためのテンプレートです。**

このリポジトリを元に、在庫管理、予約管理、チェックリスト、家計管理、設備管理、メディア管理など、用途に合わせたローカルWebアプリを開発できます。

## 開発時の重要ルール

このテンプレートでは、変更履歴と変更理由を確実に残すため、**mainへの直接Commit / Pushを禁止**します。READMEの誤字修正など、どんなに軽微な変更も例外ではありません。

```text
日本語Issueを作成
   ↓
Issue対応の作業ブランチ
   ↓
実装・テスト
   ↓
Commit / Push
   ↓
Pull Request
   ↓
CI・差分確認
   ↓
mainへMerge
```

mainへ取り込む変更単位ごとにIssueを作成し、**Issueのタイトルと本文は日本語で記載**します。PR本文から `Closes #Issue番号` などでIssueを関連付けます。

詳しいルールは [開発・CI・ローカル反映・デプロイ運用](docs/DEVELOPMENT-DEPLOYMENT.md) と [コントリビューションガイド](CONTRIBUTING.md) を参照してください。

---

## 基本構成

```mermaid
flowchart LR
    B[PC / スマートフォンのブラウザ] -->|HTTPS / Tailscale| TS[Tailscale Serve]
    TS -->|localhostへ転送| APP[Python / Flask\n127.0.0.1:8000]
    APP --> DB[(SQLite)]
    APP --> UI[HTML / CSS / JavaScript]
```

- **Python / Flask**：Webアプリ本体
- **SQLite**：データ保存
- **HTML / CSS / JavaScript**：ブラウザ画面
- **Tailscale Serve**：許可した端末・ユーザーからの接続

アプリは初期状態では `127.0.0.1` のみに公開されます。Tailscaleを有効にすると、同じtailnetに参加しているスマートフォンや別PCからHTTPSでアクセスできます。

---

## このテンプレートの特徴

- クラウドDB不要
- SQLiteなのでDBサーバーの構築不要
- ルーターのポート開放不要
- `0.0.0.0` への公開を禁止
- Tailscale Funnelは使用しない
- データはアプリを動かすPC内に保存
- Tailscale利用者を識別可能
- 利用者ごとのデータ分離に対応
- CSRF対策・CSPなど基本的なWebセキュリティ対策を実装済み
- pytestによる自動テスト付き
- GitHub ActionsによるCI付き
- Issue / Branch / PRによる変更管理
- MIT License

---

## 新しいアプリを開発するときの3段階

```text
① 作り始める
GETTING-STARTED.md
  自分用リポジトリ作成 → Clone → 初回起動 → AIへ最初の依頼
        ↓
② 作る
CUSTOMIZE.md
  データ設計 → SQLite → 業務処理 → API → 画面 → テスト
        ↓
③ 変更を運ぶ
DEVELOPMENT-DEPLOYMENT.md
  日本語Issue → Branch → Commit / Push → PR → CI → mainへMerge → Pull
```

| 今やりたいこと | 読むガイド |
| --- | --- |
| 新しいアプリを作り始めたい | **[① 新規開発スタートガイド](docs/GETTING-STARTED.md)** |
| サンプル `items` を自分の機能へ作り替えたい | **[② カスタマイズガイド](docs/CUSTOMIZE.md)** |
| Issue / PR / CI / Pull / Releaseを知りたい | **[③ 開発・CI・ローカル反映・デプロイ運用](docs/DEVELOPMENT-DEPLOYMENT.md)** |

### その他のドキュメント

| ドキュメント | 内容 |
| --- | --- |
| [アーキテクチャ](docs/ARCHITECTURE.md) | Python / Flask / SQLite / Tailscaleの役割と全体構成 |
| [セキュリティ設計](docs/SECURITY.md) | localhost、Tailscale利用者識別、CSRF、認証・認可など |
| [コントリビューションガイド](CONTRIBUTING.md) | Issue / Branch / PR / テスト等の必須ルール |
| [ライセンス](LICENSE) | MIT License |

---

## 必要なもの

- Git
- Python 3.11以上
- 開発・稼働用PC
- 外部端末から利用する場合はTailscale

---

## テンプレートを試す

```text
git clone https://github.com/k-systems202208/python-sqlite-tailscale-webapp-template.git
cd python-sqlite-tailscale-webapp-template
```

新しいアプリを開発する場合は、元テンプレートを直接編集せず、自分用リポジトリを作成してください。詳しくは [新規開発スタートガイド](docs/GETTING-STARTED.md) を参照してください。

### Windows

```powershell
.\scripts\bootstrap.ps1
Copy-Item .env.example .env
.\scripts\start.ps1
```

### macOS / Linux

```bash
./scripts/bootstrap.sh
cp .env.example .env
./scripts/start.sh
```

ブラウザで `http://127.0.0.1:8000` を開きます。

---

## 初期設定 `.env`

```text
APP_NAME=Local Web App
LOCAL_OWNER_EMAIL=owner@example.local
LOCAL_OWNER_NAME=Local Owner
```

`.env`、`data/app.db`、`.venv/` はGitHubへ登録しません。

---

## Tailscaleで別端末から使う

```text
tailscale serve --bg 8000
tailscale serve status
```

表示されたHTTPS URLを、同じtailnetに参加している端末から開きます。

**Pythonアプリを `0.0.0.0` へ変更しないでください。** Pythonは `127.0.0.1` のみに待ち受け、Tailscale Serveを入口にします。

---

## サンプル機能

動作確認用の `items` 管理機能があります。登録、完了状態切替、削除、利用者ごとのデータ分離を確認できます。

実際のアプリへ置き換える方法は [カスタマイズガイド](docs/CUSTOMIZE.md) を参照してください。

---

## フォルダー構成

```text
python-sqlite-tailscale-webapp-template/
├─ app/
│  ├─ auth.py
│  ├─ config.py
│  ├─ csrf.py
│  ├─ db.py
│  ├─ routes.py
│  ├─ schema.sql
│  ├─ security.py
│  ├─ services/
│  ├─ templates/
│  └─ static/
├─ docs/
│  ├─ GETTING-STARTED.md
│  ├─ CUSTOMIZE.md
│  ├─ DEVELOPMENT-DEPLOYMENT.md
│  ├─ ARCHITECTURE.md
│  └─ SECURITY.md
├─ scripts/
├─ tests/
├─ .env.example
├─ CONTRIBUTING.md
├─ LICENSE
├─ requirements.txt
└─ run.py
```

---

## セキュリティの基本方針

- Pythonは `127.0.0.1` のみにbind
- `0.0.0.0` など外部IPへのbindを拒否
- 外部接続はTailscale Serve経由
- Tailscale Funnelは使用しない
- CORSは初期状態で有効化しない
- 更新リクエストにCSRF対策
- `HttpOnly` / `SameSite=Strict` Cookie
- Content Security Policy等のセキュリティヘッダー
- 利用者単位のデータ分離

詳しくは [セキュリティ設計](docs/SECURITY.md) を参照してください。

---

## テスト

Windows:

```powershell
.\.venv\Scripts\python.exe -m pytest
```

macOS / Linux:

```bash
.venv/bin/python -m pytest
```

GitHubへ作業ブランチをPushするとCIが実行されます。CI成功後、PRの差分を確認してmainへMergeします。

---

## よくある質問

### 小さなREADME修正だけならmainへ直接Commitしてよいですか？

**いいえ。禁止です。** 日本語Issueを作成し、作業ブランチで修正してPRからmainへMergeします。

### Issueは不具合のときだけ必要ですか？

いいえ。新機能、修正、リファクタリング、テスト、ドキュメント、誤字修正を含め、mainへ取り込むすべての変更単位でIssueを作成します。

### Issueは英語でもよいですか？

このテンプレートの運用では、Issueタイトルと本文は日本語で記載します。

### ChatGPT / CodexがGitHubを変更する場合も同じですか？

はい。同じです。AIから変更する場合も、先に日本語Issueを作成し、Issue対応ブランチへ変更し、PR・CIを経由してmainへMergeします。

### GitHubの変更はローカルPCへ自動反映されますか？

いいえ。PRをMergeしたあと、稼働PCでmainをPullして反映します。

---

## ライセンス

MIT License
