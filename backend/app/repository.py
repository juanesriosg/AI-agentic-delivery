from __future__ import annotations

from contextlib import contextmanager
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import sqlite3
from pathlib import Path
from typing import Iterator


@dataclass(frozen=True)
class Note:
    id: int
    title: str
    body: str
    created_at: str
    updated_at: str

    def to_dict(self) -> dict[str, str | int]:
        return asdict(self)


class NoteRepository:
    def __init__(self, database_path: str | Path):
        self._database_path = Path(database_path)

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self._database_path)
        connection.row_factory = sqlite3.Row
        try:
            yield connection
            connection.commit()
        finally:
            connection.close()

    def initialize(self, schema_sql: str) -> None:
        self._database_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.executescript(schema_sql)

    def create(self, title: str, body: str) -> Note:
        if not title or not title.strip():
            raise ValueError("title must not be empty")
        body = body or ""
        note_id: int | None = None
        with self._connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO notes (title, body)
                VALUES (?, ?)
                """,
                (title.strip(), body),
            )
            note_id = int(cursor.lastrowid)
        return self.get(note_id)

    def list(self) -> list[Note]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT id, title, body, created_at, updated_at
                FROM notes
                ORDER BY id ASC
                """
            ).fetchall()
        return [self._row_to_note(row) for row in rows]

    def get(self, note_id: int) -> Note | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT id, title, body, created_at, updated_at
                FROM notes
                WHERE id = ?
                """,
                (note_id,),
            ).fetchone()
        return self._row_to_note(row) if row else None

    def update(self, note_id: int, title: str, body: str) -> Note | None:
        if not title or not title.strip():
            raise ValueError("title must not be empty")
        body = body or ""
        updated = False
        with self._connect() as connection:
            updated = connection.execute(
                """
                UPDATE notes
                SET title = ?, body = ?
                WHERE id = ?
                """,
                (title.strip(), body, note_id),
            ).rowcount
        if not updated:
            return None
        return self.get(note_id)

    def delete(self, note_id: int) -> bool:
        with self._connect() as connection:
            deleted = connection.execute(
                "DELETE FROM notes WHERE id = ?",
                (note_id,),
            ).rowcount
        return deleted > 0

    @staticmethod
    def _row_to_note(row: sqlite3.Row) -> Note:
        return Note(
            id=int(row["id"]),
            title=str(row["title"]),
            body=str(row["body"]),
            created_at=str(row["created_at"]),
            updated_at=str(row["updated_at"]),
        )

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
