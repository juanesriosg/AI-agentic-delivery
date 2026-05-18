#!/usr/bin/env python3
"""Safe read-only SQL runner for agentic data analysis.

This script is intentionally conservative. It is not a complete SQL parser, so it
combines static checks with database read-only transaction controls when the
underlying driver supports them.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import sqlite3
import sys
import textwrap
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, List, Sequence, Tuple
from urllib.parse import urlparse, unquote

BLOCKED_PATTERNS = [
    r"\bDELETE\b",
    r"\bUPDATE\b",
    r"\bINSERT\b",
    r"\bUPSERT\b",
    r"\bMERGE\b",
    r"\bTRUNCATE\b",
    r"\bDROP\b",
    r"\bALTER\b",
    r"\bCREATE\b",
    r"\bREPLACE\b",
    r"\bGRANT\b",
    r"\bREVOKE\b",
    r"\bVACUUM\b",
    r"\bANALYZE\b",
    r"\bCALL\b",
    r"\bEXEC\b",
    r"\bEXECUTE\b",
    r"\bCOPY\b",
    r"\bLOAD\b",
    r"\bLOCK\b",
    r"\bBEGIN\b",
    r"\bCOMMIT\b",
    r"\bROLLBACK\b",
    r"\bSAVEPOINT\b",
    r"\bATTACH\b",
    r"\bDETACH\b",
    r"\bPRAGMA\b",
    r"\bSET\s+ROLE\b",
    r"\bSET\s+SESSION\s+AUTHORIZATION\b",
    r"\bINTO\s+OUTFILE\b",
    r"\bINTO\s+DUMPFILE\b",
    r"\bFOR\s+UPDATE\b",
    r"\bPG_SLEEP\s*\(",
    r"\bSLEEP\s*\(",
    r"\bBENCHMARK\s*\(",
]

SENSITIVE_COLUMN_PATTERNS = [
    "password",
    "passwd",
    "secret",
    "token",
    "api_key",
    "access_key",
    "private_key",
    "credit",
    "card",
    "cvv",
    "ssn",
    "national_id",
    "document",
    "phone",
    "email",
    "address",
]

MAX_DEFAULT_LIMIT = 500


@dataclass
class LintResult:
    ok: bool
    reasons: List[str]
    normalized_sql: str
    bounded_sql: str


def strip_sql_comments(sql: str) -> str:
    # Remove /* ... */ block comments and -- line comments. This intentionally
    # does not try to preserve character positions.
    sql = re.sub(r"/\*.*?\*/", " ", sql, flags=re.S)
    sql = re.sub(r"--[^\n\r]*", " ", sql)
    return sql


def mask_string_literals(sql: str) -> str:
    out: List[str] = []
    i = 0
    quote: str | None = None
    while i < len(sql):
        ch = sql[i]
        if quote is None:
            if ch in ("'", '"'):
                quote = ch
                out.append("'x'")
                i += 1
            else:
                out.append(ch)
                i += 1
        else:
            if ch == quote:
                if i + 1 < len(sql) and sql[i + 1] == quote:
                    i += 2
                    continue
                quote = None
            i += 1
    return "".join(out)


def normalize_sql(sql: str) -> str:
    sql = strip_sql_comments(sql).strip()
    # Allow exactly one trailing semicolon, but no internal semicolons.
    if sql.endswith(";"):
        sql = sql[:-1].strip()
    return re.sub(r"\s+", " ", sql)


def has_internal_semicolon(sql: str) -> bool:
    masked = mask_string_literals(strip_sql_comments(sql)).strip()
    if masked.endswith(";"):
        masked = masked[:-1]
    return ";" in masked


def starts_with_read_only(sql: str) -> bool:
    lowered = sql.lstrip().lower()
    return lowered.startswith("select ") or lowered.startswith("with ") or lowered.startswith("explain select ") or lowered == "select"


def contains_limit(sql: str) -> bool:
    return bool(re.search(r"\bLIMIT\s+\d+\b", sql, flags=re.I))


def bound_sql(sql: str, limit: int) -> str:
    if contains_limit(sql):
        return sql
    lowered = sql.lstrip().lower()
    if lowered.startswith("explain "):
        return sql
    return f"{sql} LIMIT {int(limit)}"


def lint_sql(sql: str, limit: int = MAX_DEFAULT_LIMIT) -> LintResult:
    reasons: List[str] = []
    if not sql or not sql.strip():
        reasons.append("SQL is empty.")
        return LintResult(False, reasons, "", "")

    normalized = normalize_sql(sql)
    masked = mask_string_literals(normalized)
    upper_masked = masked.upper()

    if has_internal_semicolon(sql):
        reasons.append("Multiple SQL statements are not allowed.")

    if not starts_with_read_only(normalized):
        reasons.append("Only SELECT, WITH ... SELECT, or EXPLAIN SELECT statements are allowed.")

    for pattern in BLOCKED_PATTERNS:
        if re.search(pattern, upper_masked, flags=re.I):
            reasons.append(f"Blocked SQL pattern detected: {pattern}")

    if re.search(r"\bSELECT\s+\*\b", upper_masked) and not contains_limit(normalized):
        reasons.append("SELECT * requires an explicit LIMIT.")

    bounded = bound_sql(normalized, limit)
    return LintResult(not reasons, reasons, normalized, bounded)


def detect_driver(dsn: str, explicit: str | None = None) -> str:
    if explicit:
        return explicit
    if dsn.startswith("sqlite://") or dsn.endswith(".db") or dsn.endswith(".sqlite") or dsn.endswith(".sqlite3"):
        return "sqlite"
    if dsn.startswith("postgres://") or dsn.startswith("postgresql://"):
        return "postgres"
    if dsn.startswith("mysql://") or dsn.startswith("mariadb://"):
        return "mysql"
    return "sqlite"


def sqlite_path_from_dsn(dsn: str) -> str:
    if dsn.startswith("sqlite:///"):
        return unquote(dsn.replace("sqlite:///", "", 1))
    if dsn.startswith("sqlite://"):
        parsed = urlparse(dsn)
        return unquote(parsed.path)
    return dsn


def redact_rows(columns: Sequence[str], rows: Sequence[Sequence[Any]], extra_patterns: Sequence[str] = ()) -> List[List[Any]]:
    patterns = [p.lower() for p in SENSITIVE_COLUMN_PATTERNS] + [p.lower() for p in extra_patterns]
    redacted: List[List[Any]] = []
    for row in rows:
        new_row: List[Any] = []
        for col, value in zip(columns, row):
            col_lower = str(col).lower()
            if any(p in col_lower for p in patterns):
                new_row.append("[REDACTED]")
            else:
                new_row.append(value)
        redacted.append(new_row)
    return redacted


def execute_sqlite(dsn: str, sql: str, timeout_seconds: int) -> Tuple[List[str], List[Sequence[Any]]]:
    path = sqlite_path_from_dsn(dsn)
    uri = f"file:{Path(path).resolve()}?mode=ro"
    conn = sqlite3.connect(uri, uri=True, timeout=timeout_seconds)
    try:
        conn.execute("PRAGMA query_only = ON")
        cur = conn.execute(sql)
        rows = cur.fetchall()
        columns = [d[0] for d in (cur.description or [])]
        return columns, rows
    finally:
        conn.close()


def execute_postgres(dsn: str, sql: str, timeout_seconds: int) -> Tuple[List[str], List[Sequence[Any]]]:
    try:
        import psycopg  # type: ignore
        with psycopg.connect(dsn, autocommit=False) as conn:
            with conn.cursor() as cur:
                cur.execute("BEGIN READ ONLY")
                cur.execute(f"SET LOCAL statement_timeout = {int(timeout_seconds) * 1000}")
                cur.execute(sql)
                rows = cur.fetchall()
                columns = [d.name for d in (cur.description or [])]
                conn.rollback()
                return columns, rows
    except ImportError:
        try:
            import psycopg2  # type: ignore
            conn = psycopg2.connect(dsn)
            conn.set_session(readonly=True, autocommit=False)
            try:
                cur = conn.cursor()
                cur.execute(f"SET LOCAL statement_timeout = {int(timeout_seconds) * 1000}")
                cur.execute(sql)
                rows = cur.fetchall()
                columns = [d[0] for d in (cur.description or [])]
                conn.rollback()
                return columns, rows
            finally:
                conn.close()
        except ImportError as exc:
            raise RuntimeError("Postgres support requires psycopg or psycopg2.") from exc


def execute_mysql(dsn: str, sql: str, timeout_seconds: int) -> Tuple[List[str], List[Sequence[Any]]]:
    parsed = urlparse(dsn)
    kwargs = {
        "host": parsed.hostname,
        "port": parsed.port or 3306,
        "user": unquote(parsed.username or ""),
        "password": unquote(parsed.password or ""),
        "database": parsed.path.lstrip("/"),
        "connection_timeout": timeout_seconds,
    }
    try:
        import mysql.connector  # type: ignore
        conn = mysql.connector.connect(**kwargs)
        try:
            cur = conn.cursor()
            cur.execute("SET SESSION TRANSACTION READ ONLY")
            cur.execute("START TRANSACTION READ ONLY")
            cur.execute(sql)
            rows = cur.fetchall()
            columns = [d[0] for d in (cur.description or [])]
            conn.rollback()
            return columns, rows
        finally:
            conn.close()
    except ImportError:
        try:
            import pymysql  # type: ignore
            conn = pymysql.connect(**kwargs)
            try:
                cur = conn.cursor()
                cur.execute("SET SESSION TRANSACTION READ ONLY")
                cur.execute("START TRANSACTION READ ONLY")
                cur.execute(sql)
                rows = cur.fetchall()
                columns = [d[0] for d in (cur.description or [])]
                conn.rollback()
                return columns, rows
            finally:
                conn.close()
        except ImportError as exc:
            raise RuntimeError("MySQL support requires mysql-connector-python or pymysql.") from exc


def execute_query(driver: str, dsn: str, sql: str, timeout_seconds: int) -> Tuple[List[str], List[Sequence[Any]]]:
    if driver == "sqlite":
        return execute_sqlite(dsn, sql, timeout_seconds)
    if driver == "postgres":
        return execute_postgres(dsn, sql, timeout_seconds)
    if driver == "mysql":
        return execute_mysql(dsn, sql, timeout_seconds)
    raise RuntimeError(f"Unsupported driver: {driver}")


def markdown_table(columns: Sequence[str], rows: Sequence[Sequence[Any]], max_rows: int) -> str:
    if not columns:
        return "No result columns returned."
    rows = list(rows)[:max_rows]
    header = "| " + " | ".join(str(c) for c in columns) + " |"
    sep = "| " + " | ".join("---" for _ in columns) + " |"
    body = []
    for row in rows:
        body.append("| " + " | ".join(str(v).replace("|", "\\|") for v in row) + " |")
    return "\n".join([header, sep, *body])


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")


def append_query_log(payload: dict[str, Any]) -> None:
    log_path = Path(".agent/data-analysis/query-log.jsonl")
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(payload, default=str) + "\n")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run or lint SELECT-only SQL for agentic data analysis.")
    parser.add_argument("--sql", help="SQL string to lint/execute.")
    parser.add_argument("--sql-file", help="Path to SQL file.")
    parser.add_argument("--dsn", default=os.environ.get("AGENTIC_DB_DSN_READONLY", ""), help="Read-only DSN. Defaults to AGENTIC_DB_DSN_READONLY.")
    parser.add_argument("--driver", choices=["sqlite", "postgres", "mysql"], help="Database driver. Auto-detected from DSN if omitted.")
    parser.add_argument("--lint-only", action="store_true", help="Only lint the SQL; do not execute.")
    parser.add_argument("--limit", type=int, default=MAX_DEFAULT_LIMIT, help="Default row limit when query has no LIMIT.")
    parser.add_argument("--max-output-rows", type=int, default=200, help="Rows to include in markdown output.")
    parser.add_argument("--timeout-seconds", type=int, default=30, help="Statement timeout where supported.")
    parser.add_argument("--question-id", default="manual", help="Question/run id for logging.")
    parser.add_argument("--markdown-output", help="Markdown output path.")
    parser.add_argument("--json-output", help="JSON output path.")
    parser.add_argument("--csv-output", help="CSV output path. Use only for non-sensitive bounded aggregates.")
    parser.add_argument("--redact-column-pattern", action="append", default=[], help="Additional column-name pattern to redact.")
    args = parser.parse_args(argv)

    if args.sql_file:
        sql = Path(args.sql_file).read_text(encoding="utf-8")
    elif args.sql:
        sql = args.sql
    else:
        print("Provide --sql or --sql-file.", file=sys.stderr)
        return 2

    if args.limit <= 0 or args.limit > 5000:
        print("--limit must be between 1 and 5000.", file=sys.stderr)
        return 2

    started = time.time()
    lint = lint_sql(sql, limit=args.limit)
    query_hash = hashlib.sha256(lint.normalized_sql.encode("utf-8")).hexdigest()[:16]

    if not lint.ok:
        payload = {
            "question_id": args.question_id,
            "status": "blocked",
            "query_hash": query_hash,
            "reasons": lint.reasons,
            "timestamp": int(started),
        }
        append_query_log(payload)
        print("SQL blocked by read-only guardrails:", file=sys.stderr)
        for reason in lint.reasons:
            print(f"- {reason}", file=sys.stderr)
        return 1

    if args.lint_only:
        payload = {
            "question_id": args.question_id,
            "status": "lint_passed",
            "query_hash": query_hash,
            "bounded_sql": lint.bounded_sql,
            "timestamp": int(started),
        }
        append_query_log(payload)
        print("SQL lint passed.")
        print(lint.bounded_sql)
        return 0

    if not args.dsn:
        print("No read-only DSN provided. Set AGENTIC_DB_DSN_READONLY or pass --dsn.", file=sys.stderr)
        return 2

    driver = detect_driver(args.dsn, args.driver)
    try:
        columns, rows = execute_query(driver, args.dsn, lint.bounded_sql, args.timeout_seconds)
    except Exception as exc:
        payload = {
            "question_id": args.question_id,
            "status": "execution_failed",
            "query_hash": query_hash,
            "driver": driver,
            "error": str(exc),
            "timestamp": int(started),
        }
        append_query_log(payload)
        print(f"Query execution failed: {exc}", file=sys.stderr)
        return 1

    redacted_rows = redact_rows(columns, rows, args.redact_column_pattern)
    elapsed_ms = int((time.time() - started) * 1000)
    result = {
        "question_id": args.question_id,
        "status": "executed",
        "driver": driver,
        "query_hash": query_hash,
        "sql": lint.bounded_sql,
        "columns": list(columns),
        "row_count": len(rows),
        "elapsed_ms": elapsed_ms,
        "rows": redacted_rows,
    }

    if args.json_output:
        write_json(Path(args.json_output), result)

    if args.csv_output:
        csv_path = Path(args.csv_output)
        csv_path.parent.mkdir(parents=True, exist_ok=True)
        with csv_path.open("w", encoding="utf-8", newline="") as fh:
            writer = csv.writer(fh)
            writer.writerow(columns)
            writer.writerows(redacted_rows)

    md = "\n".join([
        "# Safe SQL Query Result",
        "",
        f"Question ID: `{args.question_id}`",
        "Status: executed",
        f"Driver: `{driver}`",
        f"Query hash: `{query_hash}`",
        f"Rows returned: {len(rows)}",
        f"Elapsed: {elapsed_ms} ms",
        "",
        "## SQL executed",
        "",
        "```sql",
        lint.bounded_sql,
        "```",
        "",
        "## Result",
        "",
        markdown_table(columns, redacted_rows, args.max_output_rows),
        "",
    ])

    if args.markdown_output:
        out = Path(args.markdown_output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(md, encoding="utf-8")
    else:
        print(md)

    log_payload = {
        "question_id": args.question_id,
        "status": "executed",
        "driver": driver,
        "query_hash": query_hash,
        "row_count": len(rows),
        "elapsed_ms": elapsed_ms,
        "timestamp": int(started),
    }
    append_query_log(log_payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
