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
作業ブランチを作成
   ↓
ChatGPT / Codex / 手動で変更
   ↓
ローカルでテスト・動作確認
   ↓
Commit
   ↓
Push
   ↓
Pull Requestを作成
   ↓
GitHub Actions（CI）
   ↓
レビュー・確認
   ↓
mainへマージ
   ↓
稼働PCでPull
   ↓
再起動・実機確認
```

小規模な個人開発ではmainへ直接Pushすることもできますが、機能追加や影響範囲の大きな変更ではPull Requestを使う方が安全です。

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

# Pull Request（プルリクエスト）を使う

## 8. Pull Requestとは何か

Pull Request（PR）は、**作業ブランチで行った変更をmainへ取り込む前に、変更内容・テスト結果・影響をまとめて確認する仕組み**です。

単に「別の人にレビューしてもらう機能」ではありません。1人で開発している場合でも、次のメリットがあります。

- mainを直接変更せずに開発できる
- 変更したファイルと差分をまとめて確認できる
- CI結果を確認してからmainへ取り込める
- 「なぜこの変更をしたか」を記録として残せる
- ChatGPT / Codexが行った複数ファイル変更を人が確認しやすい
- 問題がある変更をmainへ入れる前に止められる
- 後から過去の変更理由を追いやすい

このテンプレートでは、**ある程度まとまった変更はPRを経由してmainへ入れる運用**を推奨します。

---

## 9. main・作業ブランチ・PRの関係

基本形は次です。

```text
main
  │
  └─ feature/inventory-search を作成
          │
          ├─ 修正
          ├─ Commit
          ├─ Push
          │
          └─ Pull Request
                 │
                 ├─ 差分確認
                 ├─ CI
                 ├─ レビュー
                 └─ 問題なければmainへMerge
```

`main` は「現在の基準となる安定したソース」、作業ブランチは「開発途中の変更を置く場所」と考えると分かりやすくなります。

---

## 10. どんな変更でPRを使うべきか

次のような変更ではPRを推奨します。

- 新機能追加
- 複数ファイルにまたがる変更
- DBスキーマ変更
- 認証・認可変更
- Tailscaleやネットワーク設定に関わる変更
- 依存ライブラリ追加・更新
- セキュリティ変更
- 大きな画面変更
- リファクタリング
- ChatGPT / Codexによるまとまった自動修正

一方、個人開発で次のような非常に小さな変更ならmainへ直接Commitしても構いません。

- READMEの誤字修正
- コメント修正
- 動作に影響しない軽微な文言変更

ただし、迷ったらPRを使う方が安全です。

---

## 11. 作業ブランチを作る

作業開始前にmainを最新化します。

GitHub Desktopの場合：

```text
mainを選択
  ↓
Fetch origin
  ↓
Pull origin
```

その後、新しいブランチを作成します。

```text
Current branch
  ↓
New branch
  ↓
feature/inventory-search
```

ブランチ名は変更内容が分かる名前にします。

例：

```text
feature/inventory-search
feature/user-role
fix/csrf-error
docs/update-getting-started
refactor/item-service
```

1つのブランチに無関係な変更を大量に混ぜないことが重要です。

---

## 12. 作業ブランチで開発する

ブランチを作成したら、通常どおりChatGPT / Codex / エディターで修正します。

```text
作業ブランチ
   ↓
実装
   ↓
ローカル動作確認
   ↓
pytest
   ↓
変更内容確認
   ↓
Commit
```

複数のCommitになっても問題ありません。

たとえば：

```text
feat: 在庫検索APIを追加
feat: 在庫検索画面を追加
test: 在庫検索テストを追加
```

PRではこれらを1つの変更単位として確認できます。

---

## 13. 作業ブランチをPushする

GitHub Desktopでは **Publish branch** または **Push origin** を実行します。

```text
ローカル作業ブランチ
       ↓
Push origin
       ↓
GitHub上にも同じブランチが作成される
```

Pushしただけではmainは変更されません。

この段階では、変更はまだ作業ブランチ上にあります。

---

## 14. Pull Requestを作成する

GitHub上で作業ブランチをPushすると、通常 **Compare & pull request** が表示されます。

PR作成時は次を確認します。

```text
base: main
compare: feature/xxxx
```

意味は次です。

```text
compare側の変更を
        ↓
base側へ取り込みたい
```

このテンプレートでは通常、`main ← feature/...` の形です。

---

## 15. PRタイトルの書き方

タイトルだけで変更内容が分かるようにします。

良い例：

```text
在庫検索機能を追加
利用者権限チェックを追加
SQLiteマイグレーション処理を追加
READMEの開発手順を整理
```

分かりにくい例：

```text
修正
更新
対応しました
変更
```

後からPR一覧を見たときに内容を判断できるタイトルを付けます。

---

## 16. PR本文に書く内容

最低限、次を記載します。

```markdown
## 変更内容
- 在庫一覧に検索欄を追加
- 名前とカテゴリで部分一致検索できるようにした

## 変更理由
在庫件数が増えると一覧から目的のデータを探しにくいため。

## テスト
- pytest実行済み
- PCブラウザで検索確認済み
- スマートフォン表示確認済み

## 影響範囲
- app/routes.py
- app/services/inventory.py
- app/templates/index.html
- tests/

## 注意事項
DBスキーマ変更なし
```

DB、`.env`、依存ライブラリ、認証・セキュリティなどに影響がある場合は明記します。

例：

```text
DB変更あり
.env.example変更あり
requirements.txt変更あり
認証処理変更あり
```

これはローカル稼働PCへ反映するときの重要な情報になります。

---

## 17. Draft Pull Requestを使う場合

まだ完成していない変更でも、早めに差分やCIを確認したい場合はDraft PRを使えます。

```text
作業途中
   ↓
Draft Pull Request
   ↓
CI・差分確認
   ↓
追加修正をPush
   ↓
完成
   ↓
Ready for review
```

Draftの間は「まだmainへマージする状態ではない」という意思表示になります。

大きな変更やAIによる複数ファイル修正では便利です。

---

## 18. PRを作るとCIはどうなるか

このテンプレートではPRでもGitHub Actionsが実行されます。

```text
PR作成 / PRブランチへPush
       ↓
GitHub Actions
       ↓
Python 3.11 / 3.12 / 3.13
       ↓
pytest
```

修正を追加して同じ作業ブランチへPushすると、PRへ自動的に追加され、CIも再実行されます。

**PRを作り直す必要はありません。**

---

## 19. PRで確認するポイント

マージ前に少なくとも次を確認します。

- Files changedに意図しない変更がない
- `.env` や実データが含まれていない
- 変更目的と差分が一致している
- 必要なテストが追加・更新されている
- CIが成功している
- 認証・認可を弱めていない
- 他利用者のデータへアクセスできる変更になっていない
- `0.0.0.0` へのbind変更がない
- CSRFやセキュリティヘッダーを壊していない
- DB変更がある場合、既存データへの影響を確認した
- READMEや関連docsの更新が必要なら反映されている

ChatGPT / CodexへPR差分をレビューさせる場合も、最終的にはこの観点で確認します。

---

## 20. レビューで修正が必要になったら

PRを閉じたり作り直したりする必要はありません。

同じ作業ブランチを修正します。

```text
レビュー指摘
   ↓
作業ブランチを修正
   ↓
Commit
   ↓
Push
   ↓
既存PRへ自動反映
   ↓
CI再実行
```

PRは「1回のCommit」ではなく「ブランチ全体の変更をmainへ取り込むための窓口」です。

---

## 21. mainが先に更新された場合

PR作業中にmainへ別の変更が入ることがあります。

その場合、GitHub上で競合が表示されたり、作業ブランチがmainより古くなったりします。

基本的にはmainの最新版を作業ブランチへ取り込み、再度テストします。

GitHub Desktopでは状況に応じてmainをPullした後、作業ブランチへmainをMergeする方法があります。

競合（Conflict）が発生した場合は、どちらの変更を残すか人が確認して解消します。内容を理解せず機械的に片方を選ばないでください。

---

## 22. PRをMergeする

差分確認・CI・レビューが完了したらmainへMergeします。

```text
PR
 ↓
CI成功
 ↓
差分確認
 ↓
Merge pull request
 ↓
main更新
```

GitHubには代表的に次のマージ方法があります。

### Merge commit

作業ブランチの履歴を残したまま、mainへマージ用Commitを追加します。

### Squash and merge

PR内の複数Commitを1つにまとめてmainへ取り込みます。

### Rebase and merge

Commitをmainの先頭へ並べ直す形で取り込みます。

小規模な個人開発では、**Squash and merge** はmainの履歴を1PR＝1Commitに整理しやすいため分かりやすい選択肢です。ただし、プロジェクトの運用ルールがある場合はそれに従います。

---

## 23. Merge後に作業ブランチを削除する

PRをmainへマージしたら、不要になった作業ブランチは削除して構いません。

```text
PR Merge
  ↓
Delete branch
```

mainへ変更は残っているため、作業ブランチを削除してもマージ済みのソースは消えません。

ローカル側の不要ブランチも、作業完了後に整理できます。

---

## 24. Merge後にローカルPCを最新化する

PRをMergeしただけでは、ローカルPCのmainは自動更新されません。

GitHub Desktopでmainへ切り替えます。

```text
Current branch → main
       ↓
Fetch origin
       ↓
Pull origin
```

その後、必要に応じてアプリを再起動します。

```text
PRをMerge
   ↓
GitHubのmainが最新版
   ↓
ローカルPCでPull
   ↓
ローカルも最新版
```

---

## 25. ChatGPT / CodexとPRを組み合わせる

AIを使った開発でもPRの考え方は同じです。

おすすめは、AIへ大きな変更をmainへ直接入れさせるのではなく、**作業ブランチ → PR → CI → 確認 → Merge** の流れにすることです。

```text
要件整理
   ↓
作業ブランチ
   ↓
ChatGPT / Codexが実装
   ↓
テスト
   ↓
Push
   ↓
PR
   ↓
CI
   ↓
人が差分確認
   ↓
Merge
```

特に次の場合はPRを使う価値が高くなります。

- AIが複数ファイルを変更した
- DBを変更した
- 認証・権限を変更した
- セキュリティ関連を変更した
- 自分が変更内容を完全には追えていない

AIが作ったコードでも、PRを「人が最終確認する境界」として利用できます。

---

## 26. PRでよくある勘違い

### PRを作るとmainが変更されますか？

いいえ。PRを作っただけではmainは変更されません。Mergeして初めてmainへ入ります。

### PR作成後に修正できますか？

はい。同じ作業ブランチへCommit / PushすればPRへ自動追加されます。

### PRごとに新しいリポジトリを作りますか？

いいえ。同じリポジトリ内でブランチを作ります。

### 1人開発でもPRは必要ですか？

必須ではありませんが、まとまった変更の確認・CI・履歴管理に有効です。

### PRをMergeしたらローカルPCも変わりますか？

いいえ。GitHub上のmainが変わるだけです。ローカルPCではPullが必要です。

### PRとCIは同じものですか？

違います。PRは変更をmainへ取り込むための確認単位、CIはその変更を自動テストする仕組みです。PRの中でCIを実行する、という関係です。

---

## 27. このテンプレートで推奨するPR運用

基本ルールをまとめると次のとおりです。

```text
小さな文言修正
  → main直接でも可

通常の機能追加・修正
  → 作業ブランチ
  → PR
  → CI
  → 差分確認
  → Merge

DB・認証・セキュリティ等の重要変更
  → 必ず作業ブランチ
  → PR本文へ影響を明記
  → CI
  → 人が詳細確認
  → Merge
```

PRは手続きを増やすためではなく、**mainへ入れる前の安全確認ポイントを作るための仕組み**として利用します。

---

# GitHubからローカルへ反映する

## 28. ChatGPT等がGitHubを直接変更した場合

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

## 29. GitHubからローカルPCへ反映する

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

## 30. DB変更を含む反映は特に注意する

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

# リリース・デプロイ

## 31. なぜ最初は自動デプロイしないのか

CI成功と「今すぐ稼働環境へ反映して安全」は同じではありません。

特に次の変更では人による確認が重要です。

- SQLiteテーブル変更
- Python依存ライブラリ変更
- `.env` 設定追加・変更
- 起動方法変更
- セキュリティ設定変更

そのため初期段階では、**CI成功 → 人が確認 → Pull → 実機確認** を標準とします。

---

## 32. 開発版と正式リリースを分ける

アプリが安定してきたら、mainの最新版と実際に配布・稼働させる正式版を分けます。

```text
開発・修正
   ↓
PR
   ↓
CI成功
   ↓
mainへMerge
   ↓
人がリリース判断
   ↓
GitHub Release
   ↓
正式版として反映
```

将来自動更新する場合も、**CI成功そのものではなくGitHub Releaseを更新の境界にする**ことを推奨します。

---

## 33. 自動デプロイは段階的に導入する

```text
Phase 1  手動Pull
Phase 2  新バージョン通知
Phase 3  利用者が実行する半自動更新
Phase 4  自動更新 + ヘルスチェック + ロールバック
```

最初からPhase 4を目指す必要はありません。実運用で更新手順が固まってから自動化します。

---

## 34. 将来の安全な自動更新イメージ

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

## 35. 自動デプロイ導入前のチェック

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

## 36. この文書のまとめ

このガイドが担当するのは次の範囲です。

```text
変更済みソース
   ↓
ローカルテスト
   ↓
作業ブランチ
   ↓
Commit / Push
   ↓
Pull Request
   ↓
CI / レビュー
   ↓
mainへMerge
   ↓
Release判断
   ↓
Pull / デプロイ
   ↓
実機確認
```

アプリそのものをどう変更するかは [カスタマイズガイド](CUSTOMIZE.md)、新しいリポジトリをどう準備するかは [新規開発スタートガイド](GETTING-STARTED.md) を参照してください。

**「作り始める」「作る」「変更を運ぶ」の3段階を分け、その中でPRをmainへ入れる前の安全確認ポイントとして使う**ことが、このテンプレートの推奨運用です。
