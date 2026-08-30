# コントリビューションガイド

このテンプレートへの改善提案・バグ修正・機能改善を歓迎します。

## 基本的な流れ

1. `main` を最新化します。
2. `main` から作業用ブランチを作成します。
3. 可能な限り、共通基盤の変更とサンプル機能の変更を分けます。
4. 認証・認可・利用者ごとのデータ分離に影響する変更では、テストを追加または更新します。
5. `python -m pytest` を実行してテストが成功することを確認します。
6. 作業ブランチをPushします。
7. Pull Requestを作成し、CI・差分・影響範囲を確認します。
8. 問題なければmainへMergeします。

Pull Requestの作り方、本文の書き方、Draft PR、CI、レビュー、Merge方法、Merge後のPullまでの詳しい手順は [docs/DEVELOPMENT-DEPLOYMENT.md](docs/DEVELOPMENT-DEPLOYMENT.md) を参照してください。

## Pull Requestで最低限記載すること

PR本文には、少なくとも次を記載してください。

```markdown
## 変更内容
- 何を変更したか

## 変更理由
- なぜ変更したか

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
```

特に次の変更では、影響を明記してください。

- SQLiteスキーマ
- `.env` / `.env.example`
- `requirements.txt`
- 認証・認可
- Tailscale / localhost制約
- CSRF
- セキュリティヘッダー

## Pull Requestで確認すること

Merge前に次を確認します。

- 意図しないファイル変更がない
- `.env` や実データが含まれていない
- 必要なテストが追加・更新されている
- CIが成功している
- 認証・認可を弱めていない
- 他利用者のデータへアクセスできる変更になっていない
- `0.0.0.0` へのbind変更がない
- CSRFやセキュリティヘッダーを壊していない
- DB変更時は既存データへの影響を確認した
- READMEや関連docsの更新が必要なら反映した

## テスト

Windows:

```powershell
.\.venv\Scripts\python.exe -m pytest
```

macOS / Linux:

```bash
.venv/bin/python -m pytest
```

特に次の動作を壊していないことを確認してください。

- localhostのみで待ち受けること
- 利用者を正しく識別できること
- 他の利用者のデータを参照・更新・削除できないこと
- 更新リクエストのCSRF対策が機能すること
- セキュリティヘッダーが維持されること

## Gitへ登録してはいけないもの

次のファイルや情報はコミットしないでください。

```text
.env
data/
SQLiteデータベースファイル
生成された秘密鍵
個人・組織固有のtailnet情報
その他の秘密情報
```

これらは実際の利用環境に固有の情報であり、公開リポジトリへ含めるべきではありません。

## 変更するときの考え方

このプロジェクトは、誰でも自分用のアプリへ流用できる**小さく分かりやすいテンプレート**であることを重視しています。

便利な機能であっても、すべての利用者が必要としない大きな依存ライブラリや複雑な仕組みを共通基盤へ追加する場合は、その必要性を十分に検討してください。

アプリ固有の機能は、できるだけサンプル／カスタマイズ可能な層へ配置することを推奨します。

詳しい構成は [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)、カスタマイズ方法は [docs/CUSTOMIZE.md](docs/CUSTOMIZE.md)、開発・CI・Pull Request・デプロイ運用は [docs/DEVELOPMENT-DEPLOYMENT.md](docs/DEVELOPMENT-DEPLOYMENT.md)、セキュリティ方針は [docs/SECURITY.md](docs/SECURITY.md) を参照してください。
