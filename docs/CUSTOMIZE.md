# Customizing the template

## 1. Rename the application

Copy `.env.example` to `.env` and change:

```text
APP_NAME=My Private App
```

## 2. Replace the sample domain

The sample domain is `items`.

Replace or extend:

- `app/schema.sql`
- `app/services/items.py`
- item routes in `app/routes.py`
- `app/templates/index.html`
- CRUD tests

Keep authentication, CSRF, loopback binding and user isolation unless you have a specific reason to redesign those boundaries.

## 3. Evolve the database safely

`schema.sql` is suitable for bootstrapping a new database. Once real users have data, stop rewriting existing tables casually. Add an explicit migration mechanism and backup before schema upgrades.

A lightweight approach is a `schema_migrations` table plus numbered SQL files. A larger project can adopt Alembic/SQLAlchemy if that complexity is justified.

## 4. Decide your user model

The starter maps a Tailscale login to one row in `users` and a direct localhost owner to one configured identity.

Common extensions:

- `roles` column/table
- owner/admin flag
- shared team records
- per-user preferences
- audit log
- Tailscale app capability mapping

## 5. Add APIs carefully

For same-origin browser JavaScript, mutating requests must include the CSRF token from:

```html
<meta name="csrf-token" content="...">
```

as:

```text
X-CSRF-Token: ...
```

Do not enable broad CORS by default.

## 6. Backups

For SQLite, a practical first step is periodic copies made through SQLite's backup API, not raw file copies during active writes. Put backups outside the source tree and define a retention policy appropriate to the application.

## 7. Tailnet policy

Treat Tailscale network access as part of deployment, not application code. Define who may reach the host/service using grants or ACLs in your tailnet policy. Keep application authorization as a second layer when users have different permissions inside the app.
