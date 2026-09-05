# Security Policy

このRepositoryは、Python / SQLite / Tailscaleを使ったクローズドWebアプリ向けの公開テンプレートです。

アプリのセキュリティ設計・実装上の注意点は [../docs/SECURITY.md](../docs/SECURITY.md) を参照してください。このファイルは、テンプレート本体に関する脆弱性を安全に報告するためのポリシーです。

## Supported scope

原則として、次を対象にSecurity Issueを受け付けます。

- 現在の `main` に含まれる共通基盤
- 認証・認可、CSRF、Security Header、localhost bind、Tailscale Identity Headerの扱い
- SQLite Migration / Backup / Restoreにおける機密性・完全性
- GitHub Actions / setup script等、テンプレートのSupply Chainに関する問題

このテンプレートから作成した個別アプリに固有の脆弱性は、そのアプリの管理者へ報告してください。

## Reporting a vulnerability

脆弱性の詳細、秘密情報、実データ、認証情報、再現用token等をPublic Issueへ投稿しないでください。

GitHubのSecurityタブに **Report a vulnerability** が表示される場合は、Private Vulnerability Reportingを利用してください。

利用できない場合は、Public Issueには攻撃手順や秘密情報を書かず、**「Security issueについて非公開で連絡したい」ことだけ**を記載してください。安全な連絡方法を確立してから詳細を共有します。

報告には、可能な範囲で次を含めてください。

- 影響を受ける箇所・version / commit
- 想定される影響
- 再現条件
- 安全に共有できる最小限の再現手順
- 緩和策または修正案があればその内容

## Disclosure

修正前の脆弱性詳細をPublic Issue、Discussion、SNS等で公開しないようお願いします。影響範囲を確認し、修正・検証・利用者への案内が可能な状態になってから公開します。

## Security design

実装時の具体的なセキュリティ境界は [../docs/SECURITY.md](../docs/SECURITY.md)、品質保証の考え方は [../docs/QUALITY-VERIFICATION.md](../docs/QUALITY-VERIFICATION.md) を参照してください。
