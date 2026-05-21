from __future__ import annotations

import sqlite3
import tempfile
from pathlib import Path
import time
import unittest

from backend.app.repository import NoteRepository


REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_SQL = (REPO_ROOT / "database" / "schema.sql").read_text()


class TestDatabaseNotes(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.tempdir.name) / "notes.sqlite3"
        self.repository = NoteRepository(self.db_path)
        self.repository.initialize(SCHEMA_SQL)

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def test_schema_defines_expected_columns(self) -> None:
        with sqlite3.connect(self.db_path) as connection:
            columns = connection.execute("PRAGMA table_info(notes)").fetchall()

        column_names = [column[1] for column in columns]
        self.assertEqual(
            column_names,
            ["id", "title", "body", "created_at", "updated_at"],
        )

    def test_schema_enforces_update_timestamp_trigger_and_body_default(self) -> None:
        with sqlite3.connect(self.db_path) as connection:
            trigger = connection.execute(
                """
                SELECT sql
                FROM sqlite_master
                WHERE type = 'trigger' AND name = 'notes_set_updated_at'
                """
            ).fetchone()
            inserted = connection.execute(
                """
                INSERT INTO notes (title)
                VALUES (?)
                """,
                ("Trigger note",),
            )
            note_id = inserted.lastrowid
            row = connection.execute(
                """
                SELECT body, created_at, updated_at
                FROM notes
                WHERE id = ?
                """,
                (note_id,),
            ).fetchone()

        self.assertIsNotNone(trigger)
        self.assertEqual(row[0], "")
        self.assertTrue(str(row[1]).endswith("Z"))
        self.assertTrue(str(row[2]).endswith("Z"))

    def test_create_list_get_update_delete_round_trip(self) -> None:
        created = self.repository.create("First note", "Hello")
        self.assertEqual(created.title, "First note")
        self.assertEqual(created.body, "Hello")
        self.assertTrue(created.created_at.endswith("Z"))
        self.assertTrue(created.updated_at.endswith("Z"))

        listed = self.repository.list()
        self.assertEqual([note.id for note in listed], [created.id])

        fetched = self.repository.get(created.id)
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched.title, "First note")

        time.sleep(1.1)
        updated = self.repository.update(created.id, "Updated note", "World")
        self.assertIsNotNone(updated)
        self.assertEqual(updated.title, "Updated note")
        self.assertEqual(updated.body, "World")
        self.assertNotEqual(updated.updated_at, created.updated_at)

        deleted = self.repository.delete(created.id)
        self.assertTrue(deleted)
        self.assertIsNone(self.repository.get(created.id))

    def test_rejects_empty_titles(self) -> None:
        with self.assertRaisesRegex(ValueError, "title must not be empty"):
            self.repository.create("   ", "Body")
        with self.assertRaisesRegex(ValueError, "title must not be empty"):
            self.repository.update(1, "", "Body")

    def test_missing_note_returns_none(self) -> None:
        self.assertIsNone(self.repository.get(999))
        self.assertFalse(self.repository.update(999, "Nope", "Body"))
        self.assertFalse(self.repository.delete(999))


if __name__ == "__main__":
    unittest.main()
