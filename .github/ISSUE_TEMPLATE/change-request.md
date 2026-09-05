---
name: 変更・改善
about: 機能追加、修正、リファクタリング、ドキュメント更新など
labels: ''
assignees: ''
---

## 目的
この変更が必要な理由を日本語で記載してください。

## 対応内容
- 変更する内容
- 追加する内容
- 削除する内容

## Verification Plan

実装前に「何が壊れたら困るか」と「何を正しい状態とするか」を決めます。詳細は `docs/QUALITY-VERIFICATION.md` を参照してください。

- Risk Level: Low / Medium / High
- Important Risk:
- Correct State / Test Oracle:
- Verification Layer: Static / Unit / Integration / Sampleless / Platform / Manual / Operations
- Blocking Signal:
- Falsification / Negative Case:
- Independent Verification:

## 影響範囲
- 対象機能：
- Migration / DB変更：あり / なし
- Backup / Restoreへの影響：あり / なし
- `.env.example` 変更：あり / なし
- `requirements` / `constraints` 変更：あり / なし
- 認証・セキュリティへの影響：あり / なし

## 完了条件
- [ ] 実装または修正が完了している
- [ ] Verification Planで定義したRiskを観測できるテスト・確認がある
- [ ] 必要な正常系・境界値・異常系テストが追加・更新されている
- [ ] `scripts/check.ps1` / `scripts/check.sh` または同等の品質確認が成功している
- [ ] README / 関連docsの更新要否を確認している
- [ ] PRを作成し、CI成功後にmainへ取り込める状態になっている
