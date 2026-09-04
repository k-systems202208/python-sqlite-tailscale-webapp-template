import sqlite3
import sys
from pathlib import Path

import pytest

from scripts import db_tools


def _create_database(path: Path) -> None:
    with sqlite3.connect(path) as connection:
        connection.execute("CREATE TABLE notes (id INTEGER PRIMARY KEY, body TEXT NOT NULL)")
        connection.execute("INSERT INTO notes (body) VALUES ('first')")
        connection.commit()


def _note_count(path: Path) -> int:
    with sqlite3.connect(path) as connection:
        return connection.execute("SELECT COUNT(*) FROM notes").fetchone()[0]


def test_backup_check_and_restore(tmp_path):
    database = tmp_path / "app.db"
    backup_dir = tmp_path / "backups"
    _create_database(database)

    backup = db_tools.backup_database(database, backup_dir)
    assert backup.exists()
    assert db_tools.quick_check(backup) == "ok"

    with sqlite3.connect(database) as connection:
        connection.execute("INSERT INTO notes (body) VALUES ('second')")
        connection.commit()
    assert _note_count(database) == 2

    safety = db_tools.restore_database(backup, database, safety_backup_dir=backup_dir)
    assert safety is not None and safety.exists()
    assert _note_count(safety) == 2
    assert _note_count(database) == 1
    assert db_tools.quick_check(database) == "ok"


def test_quick_check_requires_existing_database(tmp_path):
    with pytest.raises(FileNotFoundError):
        db_tools.quick_check(tmp_path / "missing.db")


def test_cli_backup_check_and_restore(tmp_path, monkeypatch, capsys):
    database = tmp_path / "app.db"
    backup_dir = tmp_path / "backups"
    _create_database(database)

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "db_tools.py",
            "backup",
            "--database",
            str(database),
            "--backup-dir",
            str(backup_dir),
        ],
    )
    assert db_tools.main() == 0
    assert "Backup created:" in capsys.readouterr().out

    backup = next(backup_dir.glob("app-*.db"))
    monkeypatch.setattr(
        sys,
        "argv",
        ["db_tools.py", "check", "--database", str(backup)],
    )
    assert db_tools.main() == 0
    assert "SQLite quick_check: ok" in capsys.readouterr().out

    with sqlite3.connect(database) as connection:
        connection.execute("INSERT INTO notes (body) VALUES ('second')")
        connection.commit()

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "db_tools.py",
            "restore",
            str(backup),
            "--database",
            str(database),
            "--safety-backup-dir",
            str(backup_dir),
            "--yes",
        ],
    )
    assert db_tools.main() == 0
    output = capsys.readouterr().out
    assert "Pre-restore safety backup:" in output
    assert "Restore complete:" in output
    assert _note_count(database) == 1


def test_cli_restore_requires_confirmation(tmp_path, monkeypatch):
    database = tmp_path / "app.db"
    backup = tmp_path / "backup.db"
    _create_database(database)
    _create_database(backup)

    monkeypatch.setattr(
        sys,
        "argv",
        ["db_tools.py", "restore", str(backup), "--database", str(database)],
    )
    with pytest.raises(SystemExit, match="requires --yes"):
        db_tools.main()
