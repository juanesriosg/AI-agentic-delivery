from __future__ import annotations

import io
import json
import tempfile
import unittest
from pathlib import Path

from backend.app.main import create_app
from backend.app.repository import NoteRepository


REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_SQL = (REPO_ROOT / "database" / "schema.sql").read_text()


def run_app(app, method: str, path: str, body: dict | None = None):
    payload = json.dumps(body).encode("utf-8") if body is not None else b""
    environ = {
        "REQUEST_METHOD": method,
        "PATH_INFO": path,
        "CONTENT_LENGTH": str(len(payload)),
        "wsgi.input": io.BytesIO(payload),
    }
    captured = {}

    def start_response(status, headers):
        captured["status"] = status
        captured["headers"] = dict(headers)

    result = b"".join(app(environ, start_response))
    captured["body"] = result.decode("utf-8") if result else ""
    return captured


class TestNotesApi(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.tempdir.name) / "notes.sqlite3"
        self.repository = NoteRepository(self.db_path)
        self.repository.initialize(SCHEMA_SQL)
        self.app = create_app(self.repository)

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def test_post_list_get_update_delete_round_trip(self) -> None:
        created = run_app(self.app, "POST", "/api/notes", {"title": "API note", "body": "Hello"})
        self.assertEqual(created["status"], "201 Created")
        created_body = json.loads(created["body"])
        self.assertEqual(created_body["title"], "API note")

        listed = run_app(self.app, "GET", "/api/notes")
        self.assertEqual(listed["status"], "200 OK")
        listed_body = json.loads(listed["body"])
        self.assertEqual(len(listed_body["notes"]), 1)

        note_id = created_body["id"]
        fetched = run_app(self.app, "GET", f"/api/notes/{note_id}")
        self.assertEqual(fetched["status"], "200 OK")
        self.assertEqual(json.loads(fetched["body"])["title"], "API note")

        updated = run_app(self.app, "PUT", f"/api/notes/{note_id}", {"title": "Updated", "body": "World"})
        self.assertEqual(updated["status"], "200 OK")
        self.assertEqual(json.loads(updated["body"])["title"], "Updated")

        deleted = run_app(self.app, "DELETE", f"/api/notes/{note_id}")
        self.assertEqual(deleted["status"], "204 No Content")
        missing = run_app(self.app, "GET", f"/api/notes/{note_id}")
        self.assertEqual(missing["status"], "404 Not Found")

    def test_validation_and_not_found_contract(self) -> None:
        invalid = run_app(self.app, "POST", "/api/notes", {"title": " ", "body": "Body"})
        self.assertEqual(invalid["status"], "400 Bad Request")
        self.assertIn("title must not be empty", invalid["body"])

        missing = run_app(self.app, "GET", "/api/notes/999")
        self.assertEqual(missing["status"], "404 Not Found")
        self.assertEqual(json.loads(missing["body"])["error"], "note not found")

    def test_cors_preflight_allows_frontend_browser_flow(self) -> None:
        response = run_app(self.app, "OPTIONS", "/api/notes")
        self.assertEqual(response["status"], "204 No Content")
        self.assertEqual(response["body"], "")
        self.assertEqual(response["headers"].get("Access-Control-Allow-Origin"), "*")
        self.assertIn("GET, POST, PUT, DELETE, OPTIONS", response["headers"].get("Access-Control-Allow-Methods", ""))


if __name__ == "__main__":
    unittest.main()
