# Architecture

## 目的

このテンプレートは、Python / Flask + SQLite + Tailscale の共通基盤を再利用しながら、業務機能を `feature` 単位で追加・削除できる構成にします。

最重要ルールは、**共通基盤からサンプル業務ロジックを分離すること**です。

## 全体像

```mermaid
flowchart LR
    U["Browser"] --> T["Tailscale Serve"]
    T --> W["Waitress 127.0.0.1"]
    W --> F["Flask"]
    F --> C["Common Core"]
    F --> X["Feature Registry"]
    X --> I["Optional items sample"]
    C --> DB[("SQLite")]
    I --> DB
```

## Common Core

```text
app/core/                 共通Route・アクセス制御
app/auth.py               利用者識別
app/config.py             設定
app/csrf.py               CSRF
app/db.py                 SQLite / Migration runner
app/security.py           セキュリティヘッダー
app/features/__init__.py  feature自動検出・登録
app/templates/            共通Template
app/static/               共通static
scripts/                  運用・品質ツール
```

共通coreは、特定の業務featureが存在しなくても動きます。

共通URL:

- `/`
- `/healthz`
- `/readyz`
- `/api/me`

## Optional items sample

```text
app/features/items/
├─ __init__.py
├─ routes.py
├─ service.py
├─ templates/items/index.html
└─ migrations/002_sample_items.sql
```

```mermaid
flowchart TD
    T["Template"] --> C["Core"]
    T --> S["Sample"]
    C --> C1["Auth / Security"]
    C --> C2["SQLite / Tailscale"]
    C --> C3["Backup / CI"]
    S --> S1["app/features/items/"]
```

itemsを使わない新規アプリでは、このfolderを削除できます。

## Feature自動登録

`app/features/__init__.py` は `app/features/` 直下のPython packageを検出します。packageに `register(app)` があればFlask appへ登録します。

```mermaid
sequenceDiagram
    participant A as create_app
    participant F as app.features
    participant X as feature package
    A->>F: register_features(app)
    F->>F: feature packageを検出
    F->>X: register(app)
    X-->>A: Blueprint登録
```

`app/__init__.py` に `items` というfeature名をハードコードしないため、feature folderを削除してもfactoryを編集する必要がありません。

## Routeの分離

共通Routeは `app/core/routes.py` に置きます。

items sample Routeは `app/features/items/routes.py` に置きます。

```mermaid
flowchart LR
    F["Flask"] --> C["core Blueprint"]
    F --> I["items Blueprint"]
    C --> R1["/ /healthz /readyz /api/me"]
    I --> R2["/items /api/items"]
```

## Service層

業務featureのSQL / 業務処理はfeature内のServiceへ寄せます。

```mermaid
flowchart LR
    R["feature routes"] --> S["feature service"]
    S --> D["app.db / SQLite"]
```

共通DB接続やMigration処理は `app/db.py` に残します。

## Migration

Migration sourceは2系統あります。

```text
app/migrations/*.sql                    core Migration
app/features/*/migrations/*.sql         feature Migration
```

初期状態:

```text
001_initial.sql                         users
002_sample_items.sql                    optional items sample
```

全Migrationは共通の `schema_migrations` で管理し、version番号はリポジトリ全体で一意にします。

## Identity / Authorization

```mermaid
flowchart TD
    R["Request"] --> I["resolve_identity"]
    I --> U["users"]
    U --> G["g.current_user"]
    G --> C["core / feature route"]
    C --> S["Service"]
    S --> Q["SQL owner condition"]
```

Tailscale到達制御とアプリ内認可は別の層です。利用者別データはSQLでも所有者条件を付けます。

## Tailscale境界

```mermaid
flowchart LR
    B["Browser on tailnet"] --> TS["Tailscale Serve"]
    TS --> L["127.0.0.1:8000"]
    L --> F["Flask / Waitress"]
```

Flask / Waitressは `0.0.0.0` へ公開しません。Identity Headerはloopback経由のときだけ信用します。

## Templateから独自アプリへ

```mermaid
flowchart LR
    A["Use this template"] --> B["不要ならitems削除"]
    B --> C["独自feature追加"]
    C --> D["Migration / Service / Route / UI"]
    D --> E["Tests / check / CI"]
```

このfeature境界を維持することで、テンプレート本体へ案件固有コードが混ざりにくくなります。
