from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any, Callable
from wsgiref.simple_server import make_server

from backend.app.repository import NoteRepository


DEFAULT_DATABASE_PATH = Path(__file__).resolve().parents[2] / "database" / "notes.sqlite3"
SCHEMA_PATH = Path(__file__).resolve().parents[2] / "database" / "schema.sql"


def _json_response(status: str, payload: Any) -> tuple[str, list[tuple[str, str]], bytes]:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    headers = [
        ("Content-Type", "application/json; charset=utf-8"),
        ("Content-Length", str(len(body))),
    ]
    return status, headers, body


def _read_json(environ: dict[str, Any]) -> dict[str, Any]:
    try:
        length = int(environ.get("CONTENT_LENGTH") or 0)
    except ValueError:
        length = 0
    raw = environ["wsgi.input"].read(length) if length else b""
    if not raw:
        return {}
    return json.loads(raw.decode("utf-8"))


def _parse_note_id(path: str) -> int | None:
    prefix = "/api/notes/"
    if not path.startswith(prefix):
        return None
    note_id = path[len(prefix):]
    if not note_id.isdigit():
        return None
    return int(note_id)


def create_app(repository: NoteRepository | None = None) -> Callable[[dict[str, Any], Callable[..., Any]], list[bytes]]:
    repo = repository or NoteRepository(DEFAULT_DATABASE_PATH)
    if repository is None and not DEFAULT_DATABASE_PATH.exists():
        repo.initialize(SCHEMA_PATH.read_text())

    def app(environ: dict[str, Any], start_response: Callable[..., Any]) -> list[bytes]:
        method = environ["REQUEST_METHOD"].upper()
        path = environ.get("PATH_INFO", "")

        try:
            if path == "/healthz":
                status, headers, body = _json_response("200 OK", {"status": "ok"})
            elif path == "/api/notes" and method == "GET":
                notes = [asdict(note) for note in repo.list()]
                status, headers, body = _json_response("200 OK", {"notes": notes})
            elif path == "/api/notes" and method == "POST":
                payload = _read_json(environ)
                note = repo.create(str(payload.get("title", "")), str(payload.get("body") or ""))
                status, headers, body = _json_response("201 Created", asdict(note))
            else:
                note_id = _parse_note_id(path)
                if note_id is None:
                    status, headers, body = _json_response("404 Not Found", {"error": "not found"})
                elif method == "GET":
                    note = repo.get(note_id)
                    if note is None:
                        status, headers, body = _json_response("404 Not Found", {"error": "note not found"})
                    else:
                        status, headers, body = _json_response("200 OK", asdict(note))
                elif method == "PUT":
                    payload = _read_json(environ)
                    updated = repo.update(note_id, str(payload.get("title", "")), str(payload.get("body") or ""))
                    if updated is None:
                        status, headers, body = _json_response("404 Not Found", {"error": "note not found"})
                    else:
                        status, headers, body = _json_response("200 OK", asdict(updated))
                elif method == "DELETE":
                    deleted = repo.delete(note_id)
                    if not deleted:
                        status, headers, body = _json_response("404 Not Found", {"error": "note not found"})
                    else:
                        status = "204 No Content"
                        body = b""
                        headers = [("Content-Length", "0")]
                else:
                    status, headers, body = _json_response("405 Method Not Allowed", {"error": "method not allowed"})
        except ValueError as exc:
            status, headers, body = _json_response("400 Bad Request", {"error": str(exc)})
        except json.JSONDecodeError:
            status, headers, body = _json_response("400 Bad Request", {"error": "invalid json"})

        start_response(status, headers)
        return [body]

    return app


def run_server(host: str = "127.0.0.1", port: int = 8000) -> None:
    with make_server(host, port, create_app()) as server:
        server.serve_forever()


if __name__ == "__main__":
    run_server()
