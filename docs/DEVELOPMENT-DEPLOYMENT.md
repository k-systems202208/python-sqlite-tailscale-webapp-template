# 開発・CI・ローカル反映・デプロイ運用

> **この文書の役割：作った変更をどう管理・検証・反映するか**
>
> 開発開始後の日常運用を扱います。GitHub Desktop、Commit / Push、Pull Request、GitHub Actions（CI）、ローカル稼働PCへのPull、Release、将来の自動デプロイが対象です。
>
> **前の段階**：まだ自分用リポジトリや初回起動ができていない → [新規開発スタートガイド](GETTING-STARTED.md)
>
> **別の話**：DB・業務処理・API・画面をどう実装するか → [カスタマイズガイド](CUSTOMIZE.md)

---

## 1. 3つのガイドの境界

```text
GETTING-STARTED.md
  開発を始める準備
        ↓
CUSTOMIZE.md
  アプリ機能を作る・変更する
        ↓
DEVELOPMENT-DEPLOYMENT.md ← この文書
  変更をGitHubで管理し、CIで検証し、稼働PCへ反映する
```

この文書では「在庫項目をどう作るか」のような機能設計は扱いません。**完成した変更を安全に次の状態へ進める方法**に集中します。

---

## 2. GitHubとローカルPCの役割

```text
GitHub
  ├─ 正式なソースコード
  ├─ 変更履歴
  ├─ Branch / Pull Request
  ├─ GitHub Actions（CI）
  └─ Release（将来の正式配布単位）

開発PC
  ├─ ソース編集
  ├─ ローカルテスト
  └─ Commit / Push

稼働PC
  ├─ Python / Flask
  ├─ SQLite（data/app.db）
  ├─ .env
  ├─ Tailscale Serve
  └─ 実際に利用するWebアプリ
```

開発PCと稼働PCが同じPCでも構いません。役割として分けて考えると、GitHub上の変更が自動的に稼働アプリへ反映されるわけではないことが分かりやすくなります。

---

## 3. 日常の標準開発サイクル

```text
GitHubからPull
   ↓
ChatGPT / Codex / 手動で変更
   ↓
ローカルでテスト・動作確認
   ↓
Commit
   ↓
Push
   ↓
GitHub Actions（CI）
   ↓
CI成功
   ↓
必要ならレビュー・mainへマージ
   ↓
稼働PCでPull
   ↓
再起動・実機確認
```

「何を変更するか」は [カスタマイズガイド](CUSTOMIZE.md)、「変更後どう流すか」がこの文書です。

---

## 4. GitHub Desktopの役割

Gitコマンドに慣れていない場合はGitHub Desktopを推奨します。

```text
GitHub Desktop
  Clone / Fetch / Pull / Branch / Commit / Push

ChatGPT / Codex / VS Code等
  要件整理 / ソース編集 / テスト支援

PowerShell / Terminal
  アプリ起動 / pytest
```

GitHub Desktopは開発ツールそのものではなく、ローカルとGitHubの変更を管理する役割と考えると分かりやすくなります。

---

## 5. Push前にローカルテストする

可能な限りPush前にpytestを実行します。

Windows:

```powershell
.\.venv\Scripts\python.exe -m pytest
```

macOS / Linux:

```bash
.venv/bin/python -m pytest
```

画面変更がある場合はブラウザでも確認します。CIだけでは実際の画面操作を完全には確認できません。

---

## 6. Commit / Pushする

GitHub Desktopなら変更内容を確認し、意味のある単位でCommitします。

```text
変更確認
  ↓
Commit
  ↓
Push origin
```

Commitメッセージは、あとから見て変更目的が分かる内容にします。

例：

```text
feat: 備品登録機能を追加
docs: 初期設定手順を更新
fix: 他利用者データの更新を拒否
```

`.env`、`data/app.db`、秘密情報などが含まれていないことも確認してください。

---

## 7. CIで確認する

現在の `.github/workflows/ci.yml` はPushまたはPull Requestで自動実行されます。

CIではUbuntu上で次のPythonバージョンを使ってpytestを実行します。

```text
Python 3.11
Python 3.12
Python 3.13
```

基本処理は次です。

```text
checkout
  ↓
Pythonセットアップ
  ↓
依存ライブラリをインストール
  ↓
pytest
```

3バージョンすべて成功すればCI成功です。

CI失敗時は、失敗したJob / Stepのログを確認し、ChatGPT / Codexへ調査・修正を依頼できます。

---

## 8. Branch / Pull Requestを使う

小規模な初期開発ではmainへの直接変更でも運用できますが、アプリが成長したらBranchとPull Requestを推奨します。

```text
mainからfeatureブランチ作成
       ↓
      修正
       ↓
ローカルテスト
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

これにより、開発中の変更と正式なmainを分けられます。

---

## 9. ChatGPT等がGitHubを直接変更した場合

ChatGPTなどがGitHub上を直接修正した場合は次の状態になります。

```text
ChatGPT
   ↓
GitHubを変更・Commit
   ↓
CI

GitHub：新版
ローカルPC：旧版
```

**GitHubの更新はローカルPCへ自動反映されません。**

ローカル側で未Commitの変更がある場合は、いきなりPullせず変更内容を確認してください。競合する可能性があります。

---

## 10. GitHubからローカルPCへ反映する

GitHub Desktopでは次を実行します。

```text
Fetch origin
   ↓
Pull origin
```

コマンドラインなら次です。

```bash
git pull
```

依存ライブラリが変更された場合は必要に応じて `bootstrap` を再実行します。その後アプリを再起動し、ブラウザで確認します。

この時点で初めてGitHub上の新版がローカル稼働環境へ反映されます。

---

## 11. DB変更を含む反映は特に注意する

SQLite構造を変更するリリースでは、単純にPullして起動するだけでは不十分になることがあります。

```text
DBバックアップ
   ↓
新版を取得
   ↓
必要なDBマイグレーション
   ↓
アプリ起動
   ↓
動作確認
```

DBの実装・マイグレーション設計そのものは [カスタマイズガイド](CUSTOMIZE.md) の範囲ですが、**本番データへ適用する順序**はデプロイ運用としてこの流れを守ります。

---

## 12. なぜ最初は自動デプロイしないのか

CI成功と「今すぐ稼働環境へ反映して安全」は同じではありません。

特に次の変更では人による確認が重要です。

- SQLiteテーブル変更
- Python依存ライブラリ変更
- `.env` 設定追加・変更
- 起動方法変更
- セキュリティ設定変更

そのため初期段階では、**CI成功 → 人が確認 → Pull → 実機確認** を標準とします。

---

## 13. 開発版と正式リリースを分ける

アプリが安定してきたら、mainの最新版と実際に配布・稼働させる正式版を分けます。

```text
開発・修正
   ↓
main
   ↓
CI成功
   ↓
人がリリース判断
   ↓
GitHub Release
   ↓
正式版として反映
```

将来自動更新する場合も、**CI成功そのものではなくGitHub Releaseを更新の境界にする**ことを推奨します。

---

## 14. 自動デプロイは段階的に導入する

```text
Phase 1  手動Pull
Phase 2  新バージョン通知
Phase 3  利用者が実行する半自動更新
Phase 4  自動更新 + ヘルスチェック + ロールバック
```

最初からPhase 4を目指す必要はありません。実運用で更新手順が固まってから自動化します。

---

## 15. 将来の安全な自動更新イメージ

```text
新Releaseを検知
      ↓
アプリ・DBをバックアップ
      ↓
新バージョン取得
      ↓
依存ライブラリ更新
      ↓
必要ならDBマイグレーション
      ↓
アプリ再起動
      ↓
/healthz
      ↓
成功 → 新版で継続
失敗 → 旧版へロールバック
```

このテンプレートには `/healthz` があるため、将来の自動デプロイの正常性確認に利用できます。

---

## 16. 自動デプロイ導入前のチェック

- CIが安定している
- 必要な自動テストが揃っている
- SQLiteバックアップ方法が確立している
- DBマイグレーション方法が確立している
- アプリ再起動方法が決まっている
- `/healthz` で正常性を確認できる
- ロールバック方法がある
- GitHub Releaseで正式版を識別できる

これらが揃ってから自動化を検討します。

---

## 17. この文書のまとめ

このガイドが担当するのは次の範囲です。

```text
変更済みソース
   ↓
ローカルテスト
   ↓
Commit / Push
   ↓
CI
   ↓
レビュー / Release判断
   ↓
Pull / デプロイ
   ↓
実機確認
```

アプリそのものをどう変更するかは [カスタマイズガイド](CUSTOMIZE.md)、新しいリポジトリをどう準備するかは [新規開発スタートガイド](GETTING-STARTED.md) を参照してください。

**「作り始める」「作る」「変更を運ぶ」の3段階を分ける**ことが、このテンプレートのドキュメント構成です。
