# Quality Verification

このテンプレートでは、**CIがGreenであることを品質そのものとは扱いません。**

Greenは「現在定義されている評価条件を満たした」というSignalです。変更を信頼できるかは、その前に **何がRiskで、何を正しい状態とし、どのLayerで、どのFailure Signalを使って確認したか** で判断します。

AI / Coding Agentへ実装・テスト・修正を任せる場合も、この原則は変わりません。

## Verification Designの基本

変更を始める前に、最低限次を定義します。

```text
Risk
  ↓
Correct State / Test Oracle
  ↓
Verification Layer
  ↓
Blocking Signal
  ↓
Independent Verification / Human Judgment
```

### 1. Risk

「何が壊れたら困るか」を先に言語化します。

例:

- 他利用者のデータを操作できてしまう
- Migrationで既存データを壊す
- Retryや再実行で二重登録する
- Backupは作れるがRestoreできない
- `0.0.0.0` bindなどで公開範囲が広がる
- Python Versionや依存更新で第三者Cloneが動かなくなる

### 2. Correct State / Test Oracle

Test Oracleは「結果が正しいと判断する基準」です。

HTTP 200やCoverageだけではなく、必要に応じて次も確認対象にします。

- Response body / status
- SQLiteの保存状態
- 所有者条件
- Migration履歴
- ファイル生成状態
- Backup / Restore後の整合性
- セキュリティヘッダー
- bind先 / Tailscale経由のアクセス条件

### 3. Verification Layer

Riskに対して、最も安く・速く・再現性が高いLayerへ検証を置きます。

| Layer | 主な役割 |
| --- | --- |
| Static / Ruff | 構文・Lint・Format・明確な規約違反 |
| Unit | 小さな分岐、境界値、純粋なロジック |
| Integration | Flask Route、SQLite、Migration、認証・認可の組合せ |
| Sampleless smoke | サンプル削除後も共通基盤が成立すること |
| Platform CI | Python 3.11〜3.14、PowerShell 5.1、shell差異 |
| Manual / Acceptance | 実環境、Tailscale、運用手順、UX、復旧判断 |
| Operations | 稼働後のhealth / readiness / Backup / Restore / Rollback |

全部をE2Eや手動確認に寄せず、Failure Modeに合うLayerを選びます。

### 4. Blocking Signal

「何が失敗したらMergeを止めるか」を明確にします。

このテンプレートの標準Blocking Signal:

- doctor FAIL
- `pip check` FAIL
- Ruff lint / format FAIL
- pytest FAIL
- Coverage 80%未満
- sampleless smoke FAIL
- PowerShell / shell構文FAIL
- Python 3.11〜3.14のいずれかでFAIL
- Windows PowerShell 5.1 smoke FAIL

ただし、これらがすべてGreenでも、Issueで定義したRiskを観測していなければ十分な保証にはなりません。

## Risk Level

PRでは変更のRisk Levelを1つ選びます。

### Low

例:

- typo
- 説明だけのdocs更新
- 振る舞いを変えない明確な整理

最低限:

- 差分確認
- 関連するStatic / Unit check
- docs linkや契約テストがある場合はその確認

### Medium

例:

- Route / Serviceの振る舞い変更
- 新しいfeature
- Validation変更
- scripts変更

最低限:

- `scripts/check`
- 正常系
- 境界値または異常系
- 関連するIntegration Test
- 必要ならsampleless / platform差異確認

### High

例:

- 認証・認可
- CSRF / セキュリティヘッダー
- Migration / 既存データ
- Backup / Restore
- bind / Tailscale公開範囲
- dependency major update
- CI / Ruleset / release条件

最低限:

- `scripts/check`
- 正常系 + 境界値 + Failure Mode
- 関連Integration Test
- CI全Required Check
- 実装者の自己確認とは別の差分・受入観点
- 必要なManual / Acceptance確認
- Rollback / Recovery観点

High Risk変更は、AIの「問題ありません」という自己申告だけでMerge判断しません。

## Falsification: 正しさの確認だけでなく、壊しにいく

振る舞いを変更するPRでは、可能な範囲で「この実装が間違っていたら失敗するケース」を最低1つ考えます。

例:

- 空文字・0・負数・上限
- 不正形式
- 他利用者ID
- CSRF token欠落
- Migration再実行
- DBファイル欠落 / 破損
- 既存設定値との不整合
- Python範囲外Version

正常系だけを追加してGreenにするのではなく、変更のBlind Spotを探します。

## AI / Coding Agent利用時のルール

AIに実装とテストを両方任せても構いません。ただし次を守ります。

1. Issue側でRiskとCorrect Stateを先に定義する
2. Agentへ「テストを通す」だけをGoalとして与えない
3. Production CodeとTest Codeを同時に変更した場合、Test Oracleが都合よく変更されていないか差分確認する
4. 既存契約テストを削除・弱体化する場合は理由をPRへ明記する
5. Coverage数値を上げるだけの弱いAssertionを追加しない
6. AIが作ったTestだけを唯一のQuality Gateにしない
7. High Risk変更ではHuman Judgmentまたは実装Loopと異なる受入観点を残す

## Independent Verification

Independent Verificationは「別の人間が全行レビューする」ことだけを意味しません。

このテンプレートでは、実装Loopと異なる評価軸を組み合わせます。

- Ruff / Type-like static checks
- pytestの既存Regression Test
- SQLite / Flask Integration Test
- sampleless template smoke
- Python複数Version
- Windows PowerShell 5.1
- 実環境のTailscale / Operations確認
- High Risk変更に対する人間のJudgment

重要なのはAgentの数ではなく、**評価軸が同じBlind Spotだけを共有しないこと**です。

## PRで記録するVerification Plan

PRテンプレートでは次を記載します。

```text
Risk Level:
Important Risk:
Correct State / Test Oracle:
Verification Layer:
Blocking Signal:
Falsification / Negative Case:
Independent Verification:
Greenが保証する範囲:
Greenだけでは保証しない範囲:
```

すべてを長文にする必要はありません。変更に対して判断可能な粒度で記載します。

## CI成功報告

従来の4点に加えて、品質上重要な変更ではVerification Planの要点も報告します。

1. 修正ソース
2. 修正ドキュメント
3. 修正・追加テスト
4. CI結果
5. 何をRiskとして、どのSignalで確認したか
6. Greenだけでは未保証の範囲が残る場合はその内容

## このテンプレートで採用しないもの

### Coverage 100%の強制

Coverageは観測範囲の指標であり、AssertionやTest Oracleの質を保証しないため、100%を目的化しません。現在の80% Gateを維持し、重要なRiskの検証を優先します。

### 全変更のE2E化

E2Eは高価でFailure原因の切り分けも遅くなります。Failure Modeに合うLayerを選びます。

### Mutation Testingの標準必須化

有用な場面はありますが、この汎用テンプレートでは実行時間・導入コスト・第三者利用時の負担が増えるため標準Gateにはしません。案件側のRiskに応じて追加します。

### AI Reviewerだけを独立検証とみなすこと

AI Reviewは利用できますが、同じContext・同じ評価基準を共有する可能性があります。既存CI、実環境確認、人間のJudgmentと組み合わせます。

## 関連ドキュメント

- [DEVELOPMENT.md](DEVELOPMENT.md)
- [TEMPLATE-SMOKE-TEST.md](TEMPLATE-SMOKE-TEST.md)
- [SECURITY.md](SECURITY.md)
- [OPERATIONS.md](OPERATIONS.md)
- [../CONTRIBUTING.md](../CONTRIBUTING.md)
