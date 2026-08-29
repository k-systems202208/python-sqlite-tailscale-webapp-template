# Contributing

1. Create a branch from `main`.
2. Keep infrastructure changes separate from sample-domain changes where practical.
3. Add or update tests for authentication, authorization and data ownership behavior.
4. Run `python -m pytest`.
5. Open a pull request describing the security/deployment impact of the change.

Never commit `.env`, `data/`, SQLite database files, generated secrets, or private tailnet information.
