from __future__ import annotations

import argparse
import os
import sqlite3
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")


def default_database_path() -> Path:
    data_dir = Path(os.getenv("APP_DATA_DIR", "data"))
    if not data_dir.is_absolute():
        data_dir = ROOT / data_dir
    return data_dir / "app.db"


def quick_check(database: Path) -> str:
    database = Path(database)
    if not database.exists():
        raise FileNotFoundError(f"Database not found: {database}")

    with sqlite3.connect(database) as connection:
        row = connection.execute("PRAGMA quick_check").fetchone()

    result = row[0] if row else ""
    if result != "ok":
        raise RuntimeError(f"SQLite quick_check failed for {database}: {result}")
    return result


def backup_database(
    database: Path,
    backup_dir: Path,
    *,
    prefix: str | None = None,
) -> Path:
    database = Path(database)
    backup_dir = Path(backup_dir)
    if not database.exists():
        raise FileNotFoundError(f"Database not found: {database}")

    backup_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().astimezone().strftime("%Y%m%d-%H%M%S-%f")
    name = prefix or database.stem
    destination = backup_dir / f"{name}-{timestamp}.db"

    with sqlite3.connect(database) as source, sqlite3.connect(destination) as target:
        source.backup(target)

    quick_check(destination)
    return destination


def _remove_sqlite_sidecars(database: Path) -> None:
    for suffix in ("-wal", "-shm"):
        sidecar = Path(f"{database}{suffix}")
        if sidecar.exists():
            sidecar.unlink()


def restore_database(
    backup: Path,
    database: Path,
    *,
    safety_backup_dir: Path | None = None,
) -> Path | None:
    backup = Path(backup)
    database = Path(database)
    quick_check(backup)

    database.parent.mkdir(parents=True, exist_ok=True)
    safety_backup = None
    if database.exists():
        safety_dir = Path(safety_backup_dir or (ROOT / "backups"))
        safety_backup = backup_database(database, safety_dir, prefix="pre-restore")

    temporary = database.with_name(f".{database.name}.restore-{uuid4().hex}.tmp")
    try:
        with sqlite3.connect(backup) as source, sqlite3.connect(temporary) as target:
            source.backup(target)
        quick_check(temporary)
        _remove_sqlite_sidecars(database)
        os.replace(temporary, database)
    finally:
        if temporary.exists():
            temporary.unlink()

    quick_check(database)
    return safety_backup


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="SQLite backup, restore and integrity tools")
    subparsers = parser.add_subparsers(dest="command", required=True)

    backup_parser = subparsers.add_parser("backup", help="Create a consistent SQLite backup")
    backup_parser.add_argument("--database", type=Path, default=default_database_path())
    backup_parser.add_argument("--backup-dir", type=Path, default=ROOT / "backups")

    check_parser = subparsers.add_parser("check", help="Run PRAGMA quick_check")
    check_parser.add_argument("--database", type=Path, default=default_database_path())

    restore_parser = subparsers.add_parser("restore", help="Restore a SQLite backup")
    restore_parser.add_argument("backup", type=Path)
    restore_parser.add_argument("--database", type=Path, default=default_database_path())
    restore_parser.add_argument("--safety-backup-dir", type=Path, default=ROOT / "backups")
    restore_parser.add_argument(
        "--yes",
        action="store_true",
        help="Required confirmation for destructive restore",
    )

    return parser


def main() -> int:
    args = _parser().parse_args()

    if args.command == "backup":
        path = backup_database(args.database, args.backup_dir)
        print(f"Backup created: {path}")
        return 0

    if args.command == "check":
        quick_check(args.database)
        print(f"SQLite quick_check: ok ({args.database})")
        return 0

    if args.command == "restore":
        if not args.yes:
            raise SystemExit("Restore requires --yes. Stop the app and create a backup first.")
        safety = restore_database(
            args.backup,
            args.database,
            safety_backup_dir=args.safety_backup_dir,
        )
        if safety:
            print(f"Pre-restore safety backup: {safety}")
        print(f"Restore complete: {args.database}")
        return 0

    raise AssertionError(f"Unexpected command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
