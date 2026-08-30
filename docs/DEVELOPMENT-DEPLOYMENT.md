# 開発・CI・ローカル反映・デプロイ運用

この文書では、このテンプレートを使って実際にアプリを開発するときの流れと、GitHub・ローカルPC・CIの役割分担を説明します。

## 1. アプリ本体はどこにあるのか

実際に稼働するアプリ本体はローカルPC上にあります。

```text
GitHub
  ├─ ソースコードの保管
  ├─ 変更履歴
  ├─ Pull Request
  └─ GitHub Actions（CI）

ローカルPC
  ├─ Python / Flask
  ├─ SQLite（data/app.db）
  ├─ .env
  ├─ Tailscale Serve
  └─ 実際に稼働するWebアプリ
```

GitHubは通常、アプリそのものを実行する場所ではありません。このテンプレートでは、GitHubで管理したソースコードをローカルPCへ取得し、そのPC上でアプリを実行します。

## 2. GitHub Desktopを使った開発

Gitコマンドに慣れていない場合はGitHub Desktopの利用を推奨します。

役割を分けると次のようになります。

```text
GitHub Desktop
  └─ Clone / Pull / Commit / Push / Branch

VS Code / Codex等
  └─ ソースコード編集

PowerShell / Terminal
  └─ アプリ起動 / pytest
```

基本的な開発フローは次のとおりです。

```text
GitHub
   ↓ Clone / Pull
ローカルPC
   ↓
ソースを編集
   ↓
ローカルで起動・テスト
   ↓
GitHub Desktopで変更確認
   ↓ Commit
   ↓ Push
GitHub
   ↓
GitHub Actions（CI）
```

## 3. CIの実行

現在の `.github/workflows/ci.yml` は、pushまたはPull Requestを契機に自動実行されます。

CIではUbuntu上で次のPythonバージョンを使ってテストします。

```text
Python 3.11
Python 3.12
Python 3.13
```

処理の流れは次のとおりです。

```text
ソースをcheckout
   ↓
Pythonをセットアップ
   ↓
pipを更新
   ↓
requirements-dev.txtをインストール
   ↓
pytestを実行
```

3バージョンすべて成功すればCI成功です。

ローカルPCでもpush前にpytestを実行することを推奨します。

Windows:

```powershell
.\.venv\Scripts\python.exe -m pytest
```

macOS / Linux:

```bash
.venv/bin/python -m pytest
```

## 4. ChatGPT / Codex等からGitHubを直接修正した場合

GitHub連携された開発支援ツールからソースコードを修正した場合、GitHub上のソースとCIは更新できますが、ローカルPCのファイルは自動的には更新されません。

```text
ChatGPT / Codex等
   ↓
GitHub上のソースを修正
   ↓
Commit
   ↓
GitHub Actions
   ↓
CI成功
   ↓
GitHubは最新版

【この時点ではローカルPCは旧版のまま】
```

これは正常な動作です。

## 5. GitHubからローカルPCへ反映する

GitHub側で変更・CIが完了したら、ローカルPCで最新版を取得します。

GitHub Desktopを使う場合は、対象リポジトリを開いて次を実行します。

```text
Fetch origin
   ↓
Pull origin
```

コマンドラインなら次のように取得できます。

```text
git pull
```

その後、必要に応じてアプリを再起動します。

現在の基本運用は次の形です。

```text
開発支援ツール / ローカル開発
        ↓
      GitHub
        ↓
       CI
        ↓
     CI成功
        ↓
GitHub DesktopでPull
        ↓
   ローカルPCへ反映
        ↓
   アプリを起動
```

## 6. なぜ最初は自動デプロイしないのか

CI成功と、稼働環境へ即時反映してよいことは同じではありません。

特に次のような変更では注意が必要です。

- SQLiteのテーブル変更
- Python依存ライブラリの変更
- `.env` 設定項目の変更
- 起動方法の変更
- セキュリティ設定の変更

そのため、テンプレートの初期段階では **CI成功後に人が確認し、Pullして反映する運用** を標準とします。

## 7. Pull Requestを使う場合の推奨フロー

アプリが成長してきたら、mainを直接変更するのではなく作業ブランチとPull Requestを利用すると安全です。

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
レビュー・確認
      ↓
mainへマージ
      ↓
ローカルPCでPull
```

## 8. 将来的な自動デプロイ

リリースを重ねてアプリが安定した後は、ローカル環境への自動デプロイを導入することも可能です。

ただし、最初から完全自動化するのではなく段階的な導入を推奨します。

```text
Phase 1
手動Pull

Phase 2
新バージョンの更新通知

Phase 3
利用者が実行する半自動更新

Phase 4
自動デプロイ + ヘルスチェック + ロールバック
```

## 9. 自動デプロイでは「CI成功＝即反映」にしない

将来的な自動化では、mainへのpushをそのまま本番ローカルPCへ反映するより、正式なリリースを境界にする方法を推奨します。

```text
修正
 ↓
GitHub
 ↓
CI成功
 ↓
GitHub Release作成
 ↓
ローカルPCが新Releaseを検知
 ↓
自動更新
```

これにより、「開発中の最新版」と「正式に配布してよいバージョン」を分けられます。

## 10. 将来の安全な自動更新イメージ

自動デプロイを実装する場合は、単純な `git pull` だけではなく、次のような流れを想定します。

```text
新Releaseを検知
      ↓
現在のアプリ・DBをバックアップ
      ↓
新バージョン取得
      ↓
依存ライブラリ更新
      ↓
必要ならDBマイグレーション
      ↓
アプリ再起動
      ↓
/healthz でヘルスチェック
      ↓
成功 ──→ 新版で継続
      |
      └ 失敗 ──→ 旧版へロールバック
```

このテンプレートには `/healthz` があるため、将来の自動デプロイでも稼働確認に利用できます。

## 11. 自動デプロイ導入前に整えておくもの

完全自動化へ進む前に、最低限次の仕組みを安定させることを推奨します。

- CIが安定して成功する
- 必要な自動テストが揃っている
- SQLiteのバックアップ方法が確立している
- DBマイグレーション方法が確立している
- アプリの再起動方法が決まっている
- `/healthz` で正常性を確認できる
- 更新失敗時のロールバック方法がある
- GitHub Release等で正式版を識別できる

## 12. このテンプレートの基本方針

初期状態では安全性と分かりやすさを優先します。

```text
開発
  ↓
GitHub
  ↓
CI
  ↓
人が確認
  ↓
ローカルPCへ反映
```

そしてアプリが成熟した後に、必要な利用者だけが次の段階へ進める設計とします。

```text
開発
  ↓
CI
  ↓
Release
  ↓
バックアップ
  ↓
自動デプロイ
  ↓
ヘルスチェック
  ↓
必要ならロールバック
```

**手動運用から始め、安定性を確認してから自動化する**ことを、このテンプレートの推奨運用とします。
