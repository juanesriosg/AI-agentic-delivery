# v10 Data Analysis Agent

This package adds a business/data analysis capability to the agentic delivery system.

The goal is to let an AI data analyst answer business questions using the project context and database data while enforcing a strict **read-only SQL** policy.

## What the agent can do

- Read project business context from specs, PR summaries, business rules, release evidence, and agent logs.
- Ask clarifying questions when a business question is ambiguous.
- Continue safe exploratory analysis while waiting for clarification.
- Inspect schema metadata when allowed.
- Propose SQL queries.
- Execute only `SELECT`, `WITH ... SELECT`, or safe `EXPLAIN SELECT` statements through `.ai/scripts/safe_sql_query.py`.
- Summarize results in business language.
- State assumptions and data-quality limitations.
- Recommend product, engineering, QA, or data follow-ups.

## What the agent must never do

- Never run `DELETE`, `UPDATE`, `INSERT`, `UPSERT`, `MERGE`, `TRUNCATE`, `DROP`, `ALTER`, `CREATE`, `REPLACE`, `GRANT`, `REVOKE`, `VACUUM`, `ANALYZE`, `CALL`, `EXEC`, `COPY`, `LOAD`, `LOCK`, `COMMIT`, `ROLLBACK`, or `BEGIN`.
- Never use write-capable database credentials.
- Never bypass `.ai/scripts/safe_sql_query.py` for database queries.
- Never expose secrets, credentials, raw tokens, passwords, or private keys.
- Never export large datasets unless the manager explicitly approves and the database policy allows it.
- Never make business claims without linking them to query evidence or project context.

## Default data flow

```text
Business question / issue / manager prompt
  ↓
Build business context pack
  ↓
Read specs, PR summaries, business rules, release notes
  ↓
Inspect allowed schema metadata
  ↓
Create analysis plan
  ↓
Run safe SELECT queries only
  ↓
Validate numbers and edge cases
  ↓
Answer with assumptions, evidence, and next actions
```

## Required runtime setup

Use a read-only database user. The credentials should be scoped to the minimum database/schema needed.

Recommended environment variable:

```bash
export AGENTIC_DB_DSN_READONLY='postgresql://readonly_user:***@host:5432/dbname'
```

Supported drivers:

```text
sqlite    built into Python
postgres  requires psycopg or psycopg2
mysql     requires mysql-connector-python or pymysql
```

The agent may also use a local configuration file, but secrets must not be committed:

```text
.ai/data/database-connections.local.yml   # ignored by git
```

The committed example file is:

```text
.ai/data/database-connections.example.yml
```

## Build the business context pack

```bash
python .ai/scripts/build_business_context.py \
  --output docs/agentic-business-context/context-pack.md \
  --json-output docs/agentic-business-context/context-pack.json
```

Optional GitHub PR summary ingestion:

```bash
python .ai/scripts/build_business_context.py --include-github-prs --github-limit 30
```

This requires the GitHub CLI (`gh`) to be authenticated.

## Run a safe query

Lint only:

```bash
python .ai/scripts/safe_sql_query.py --lint-only --sql "SELECT COUNT(*) FROM users"
```

Execute:

```bash
python .ai/scripts/safe_sql_query.py \
  --dsn "$AGENTIC_DB_DSN_READONLY" \
  --sql "SELECT status, COUNT(*) AS total FROM orders GROUP BY status" \
  --markdown-output .agent/data-analysis/orders-by-status.md \
  --json-output .agent/data-analysis/orders-by-status.json
```

## Ask a business question

Use the issue template:

```text
.github/ISSUE_TEMPLATE/data_question.yml
```

Or manually create a prompt for Codex:

```bash
python .ai/scripts/build_business_context.py
codex exec --ask-for-approval never --sandbox workspace-write "$(cat .github/codex/prompts/data-analysis.md)"
```

## Review evidence

Data analysis evidence is written under:

```text
.agent/data-analysis/
docs/agentic-business-context/
docs/agentic-evidence/<story-id>/<task-id>/data-analysis.md
```

The answer should include:

```text
Question
Context used
Queries run
Result summary
Business interpretation
Assumptions
Data-quality warnings
Recommended actions
Follow-up questions
```

## Production safety recommendation

Do not give the agent write-capable production credentials. Use a read replica, analytics replica, warehouse, or restricted read-only role whenever possible. If production querying is needed, use a dedicated read-only role with statement timeout, row limits, schema restrictions, and auditing.
