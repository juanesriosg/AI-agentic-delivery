# SQLite Notes Model

This repository task uses a local SQLite database as the persistence boundary for the CRUD smoke app.

## Schema

The schema lives in [`schema.sql`](./schema.sql) and defines a single `notes` table:

- `id`: integer primary key.
- `title`: required text, rejected when empty or whitespace-only.
- `body`: note body text, defaulting to an empty string.
- `created_at`: ISO timestamp stored as `TEXT`.
- `updated_at`: ISO timestamp stored as `TEXT`.

## Repository behavior

The database layer is expected to support:

- create
- list
- read
- update
- delete

The repository code should keep SQLite access local and temporary-file friendly for tests.

## Test data strategy

- Tests use a temporary SQLite file per test case.
- Schema is loaded from `schema.sql` before exercising repository behavior.
- No persistent fixture database is committed to the repo.

## Rollback guidance

This task has no production migration path.

Rollback means:

1. Remove the local notes schema and repository files introduced by this task.
2. Delete any temporary SQLite databases created during testing.
3. Re-run the database tests to confirm the repository no longer exposes the smoke model.

## Validation notes

Database layer validation should prove that:

- empty titles are rejected,
- CRUD operations round-trip through SQLite,
- missing notes return `None` rather than silently fabricating rows,
- timestamps are populated by SQLite and refreshed on update.
