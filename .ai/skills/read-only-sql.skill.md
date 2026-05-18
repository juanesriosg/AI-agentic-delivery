# Skill: Read-Only SQL Analysis

## Purpose

Safely query relational data while preventing data mutation.

## Procedure

1. Restate the business question.
2. Identify the metric, population, and time range.
3. Read `docs/agentic-business-context/context-pack.md`.
4. Check `.ai/specs/data-analysis-policy.yml`.
5. Write the smallest safe query that answers the question.
6. Run lint:

```bash
python .ai/scripts/safe_sql_query.py --lint-only --sql-file query.sql
```

7. If lint passes, execute:

```bash
python .ai/scripts/safe_sql_query.py \
  --sql-file query.sql \
  --markdown-output .agent/data-analysis/<question-id>.md \
  --json-output .agent/data-analysis/<question-id>.json
```

8. Validate the result with a second query or explain why validation is not possible.
9. Summarize in business terms.

## Rules

- Use only `SELECT`, `WITH ... SELECT`, or safe `EXPLAIN SELECT`.
- Prefer aggregates over raw rows.
- Use limits for exploratory queries.
- Use explicit time windows.
- Never bypass the guardrail script.
- Never use write-capable credentials.
