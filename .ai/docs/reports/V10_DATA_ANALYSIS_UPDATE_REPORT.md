# v10 Data Analysis Update Report

## Summary

Added a Business Data Analyst Agent that can answer business questions using project context and read-only SQL.

## Why this matters

The agentic ecosystem now has a way to connect engineering delivery with business outcomes. It can read specs, PR summaries, business rules, QA/PM evidence, and database data to answer questions like:

- Which feature is being adopted?
- Where are users dropping off?
- Did the last PR change the business metric we expected?
- Which records are affected by a bug?
- Which business rule is contradicted by current data?
- What instrumentation is missing?

## Guardrails added

- SQL linter blocks mutating statements.
- Query runner enforces read-only transaction behavior where supported.
- SQLite is opened in `mode=ro` and `PRAGMA query_only = ON`.
- Postgres uses read-only transactions where supported.
- MySQL attempts read-only transactions where supported.
- Default row limit is added to unbounded SELECT queries.
- Sensitive columns are redacted by default.
- Every query run is logged.

## Required setup

Configure a read-only database secret:

```text
AGENTIC_DB_DSN_READONLY
```

For GitHub/Codex data analysis, also configure:

```text
OPENAI_API_KEY
```

## Recommended DB setup

Use a read replica, analytics warehouse, or database role with only SELECT permissions. Do not give the agent production writer credentials.

## Validation performed

- Python compile checks.
- SELECT lint pass.
- DELETE/UPDATE/INSERT/DDL lint block.
- SQLite read-only execution against a temporary database.
- Sensitive column redaction check.
- Context-pack generation check.
- YAML workflow parsing check.
- JSON config parsing check.
