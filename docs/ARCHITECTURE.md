# Architecture

## Purpose

This repository is infrastructure for a small, private, self-hosted web application. It deliberately separates reusable platform concerns from replaceable business logic.

## Runtime path

```text
Browser
  |
  | HTTPS inside tailnet
  v
Tailscale Serve
  |
  | localhost reverse proxy + identity headers
  v
127.0.0.1:8000 / Waitress
  |
  v
Flask
  |-- auth.py       identity boundary
  |-- csrf.py       request integrity
  |-- routes.py     HTTP boundary
  |-- services/     business logic
  |-- db.py         SQLite access
  |-- templates/    HTML UI
  +-- static/       CSS / JS
  |
  v
data/app.db
```

## Reusable infrastructure contract

Keep these concepts even when replacing the example feature:

- localhost-only server
- Tailscale Serve as the remote entry point
- identity resolved at the HTTP boundary
- current user available through `g.current_user`
- ownership enforced in database queries, not only in the UI
- SQLite connection lifecycle per request
- CSRF for state-changing browser requests
- security headers
- tests for cross-user isolation

## Replaceable application layer

The sample `items` table/service/routes/template are intentionally disposable. A real application can replace them with inventory, bookings, checklists, household data, media metadata, operations records, or any other small-domain model.

## Data ownership

The host machine is the source of truth for application data. Tailscale transports requests; it is not the application database.

## Scale boundary

This template targets single-host / small-team / household applications. SQLite is a strong fit when one application process owns the database file and write concurrency is moderate. If you later need multiple independent server nodes or high write concurrency, move the persistence layer to a client/server database rather than sharing the SQLite file over a network filesystem.
