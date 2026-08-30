# コントリビューションガイド

このテンプレートへの改善提案・バグ修正・機能改善を歓迎します。

## 必須ルール

変更の大小にかかわらず、次のルールを守ります。

1. **mainへの直接Commit / Pushは禁止します。**
2. **mainへ取り込む変更単位ごとにIssueを作成します。**
3. **Issueのタイトル・本文は日本語で記載します。**
4. Issueに対応する作業ブランチを作成します。
5. 作業ブランチで変更・テスト・Commit / Pushします。
6. **必ずPull Requestを作成します。**
7. PR本文からIssueを `Closes #番号` などで関連付けます。
8. CI成功と差分を確認してからmainへMergeします。
9. READMEや関連docsへの影響がある場合は同じPRで最新化します。

READMEの誤字、コメント、軽微な文言変更、ドキュメントだけの変更も例外ではありません。

```text
日本語Issue
   ↓
作業Branch
   ↓
Commit / Push
   ↓
Pull Request
   ↓
CI・確認
   ↓
mainへMerge
```

## Issueの書き方

Issueは変更理由と完了条件を残す作業票として使います。

```markdown
## 目的
なぜ変更するのか。

## 対応内容
- 変更内容

## 影響範囲
- 対象機能
- DB / 設定 / セキュリティへの影響

## 完了条件
- 完了と判断できる条件
- 必要なテスト
- 必要なドキュメント更新
```

原則として1 Issueに対して1 PRでmainへ取り込みます。

## Pull Requestで最低限記載すること

```markdown
## 対応Issue
Closes #123

## 変更内容
- 何を変更したか

## テスト
- 実行したテスト
- 手動確認内容

## 影響範囲
- 主な変更ファイル
- 影響する機能

## 注意事項
- DB変更の有無
- .env.example変更の有無
- requirements変更の有無
- 認証・セキュリティへの影響

## ドキュメント
- README更新の要否
- 関連docs更新の要否
```

## Merge前チェック

- 対応する日本語Issueがある
- PRとIssueが関連付いている
- mainへの直接Commitではない
- 意図しないファイル変更がない
- `.env` や実データが含まれていない
- 必要なテストが追加・更新されている
- CIが成功している
- 認証・認可を弱めていない
- 他利用者のデータへアクセスできる変更になっていない
- `0.0.0.0` へのbind変更がない
- CSRFやセキュリティヘッダーを壊していない
- DB変更時は既存データへの影響を確認した
- READMEや関連docsが最新になっている

## テスト

Windows:

```powershell
.\.venv\Scripts\python.exe -m pytest
```

macOS / Linux:

```bash
.venv/bin/python -m pytest
```

特にlocalhost制約、利用者識別、利用者間データ分離、CSRF、セキュリティヘッダーを壊していないことを確認します。

## Gitへ登録してはいけないもの

```text
.env
data/
SQLiteデータベースファイル
生成された秘密鍵
個人・組織固有のtailnet情報
その他の秘密情報
```

## 変更するときの考え方

このプロジェクトは、誰でも自分用のアプリへ流用できる**小さく分かりやすいテンプレート**であることを重視しています。

便利な機能であっても、すべての利用者が必要としない大きな依存ライブラリや複雑な仕組みを共通基盤へ追加する場合は、その必要性を十分に検討してください。

詳しい構成は [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)、カスタマイズ方法は [docs/CUSTOMIZE.md](docs/CUSTOMIZE.md)、Issue・Pull Request・CI・デプロイ運用は [docs/DEVELOPMENT-DEPLOYMENT.md](docs/DEVELOPMENT-DEPLOYMENT.md)、セキュリティ方針は [docs/SECURITY.md](docs/SECURITY.md) を参照してください。
