# Read-Only SQL Policy

The data analysis agents may query data only through approved read-only paths.

## Allowed

```sql
SELECT ...
WITH cte AS (...) SELECT ...
EXPLAIN SELECT ...
```

## Forbidden

```sql
DELETE
UPDATE
INSERT
UPSERT
MERGE
TRUNCATE
DROP
ALTER
CREATE
REPLACE
GRANT
REVOKE
VACUUM
ANALYZE
CALL
EXEC
COPY
LOAD
LOCK
BEGIN
COMMIT
ROLLBACK
SAVEPOINT
```

## Required controls

1. Use read-only database credentials.
2. Use `.ai/scripts/safe_sql_query.py`.
3. Use explicit limits for exploratory queries.
4. Use statement timeouts where supported.
5. Prefer aggregates over raw rows.
6. Redact sensitive columns.
7. Log every analysis run.
8. State assumptions and data-quality limitations.

## Escalate to manager

Escalate when:

- The agent needs raw PII.
- The query would scan a very large table.
- The metric definition is ambiguous.
- The database owner is unknown.
- A blocked query seems required.
- Production data access is required.
- Results conflict with business rules or PR/spec history.
