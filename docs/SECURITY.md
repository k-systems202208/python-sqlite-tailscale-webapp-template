# Security model

## Boundary

The backend listens only on `127.0.0.1`. Remote clients reach it through Tailscale Serve. This is important because Tailscale identity headers must only be trusted behind a trusted local proxy path.

The template intentionally refuses non-loopback binds in `run.py`.

## Tailscale identity

When Tailscale Serve proxies an authenticated tailnet request, it can add identity headers such as:

- `Tailscale-User-Login`
- `Tailscale-User-Name`

The application accepts those headers only if the backend connection itself comes from loopback. A request arriving from another address cannot assert a Tailscale identity by supplying the same header names.

Tailscale's documentation also recommends localhost-only backend listening when identity headers are used.

## Local machine trust

Any process already running with sufficient access on the same host can potentially reach localhost and imitate proxy headers. The host operating system is therefore part of the trust boundary. Keep the host patched and do not run untrusted software under the same user/session.

## Browser protections

The template enables:

- CSRF tokens for state-changing requests
- `SameSite=Strict` and `HttpOnly` session cookies
- Content Security Policy
- frame denial
- MIME sniffing protection
- no-referrer policy
- `no-store` for HTML/JSON responses

## Network exposure rules

Recommended:

- keep the app on `127.0.0.1`
- use Tailscale Serve
- restrict tailnet access with grants/ACLs
- use OS disk permissions and backups for the SQLite database

Avoid:

- `0.0.0.0` binding
- router port forwarding
- DMZ exposure
- Tailscale Funnel for private-only applications
- placing `app.db`, `.env`, or `data/` in Git

## Authorization

Authentication answers "who is this?" Authorization answers "what may they do?" The sample app enforces ownership in SQL queries (`owner_user_id`). Carry this pattern into your own tables.

For roles or feature-level permissions, add application roles in SQLite or use Tailscale grants/app capabilities as an advanced extension. Do not rely only on hiding buttons in the UI.

## Secrets

A random Flask session secret is generated into `data/.secret_key` when `APP_SECRET_KEY` is not supplied. `data/` is gitignored. Production-like installations can instead provide `APP_SECRET_KEY` through the environment.
