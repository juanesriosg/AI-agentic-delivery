# Manifest v10 - Business Data Analysis Agent

v10 adds a safe business/data analysis system.

## Added agents

```text
.ai/agents/business-data-analyst.agent.md
.ai/agents/sql-readonly-analyst.agent.md
.ai/agents/business-context-curator.agent.md
```

## Added skills

```text
.ai/skills/read-only-sql.skill.md
.ai/skills/business-question-analysis.skill.md
.ai/skills/business-context-ingestion.skill.md
.ai/skills/metric-definition.skill.md
```

## Added specs and policies

```text
.ai/specs/data-analysis-policy.yml
.ai/specs/business-context-policy.yml
.ai/specs/read-only-sql-policy.md
.ai/specs/data-question-template.md
.ai/specs/data-answer-template.md
.ai/specs/database-access-config.schema.yml
.ai/data/database-connections.example.yml
```

## Added scripts

```text
.ai/scripts/safe_sql_query.py
.ai/scripts/build_business_context.py
.ai/scripts/data_question.py
```

## Added GitHub/Codex integration

```text
.github/ISSUE_TEMPLATE/data_question.yml
.github/codex/prompts/data-analysis.md
.github/workflows/agentic-data-analysis-request.yml
```

## Added examples and docs

```text
DATA_ANALYSIS_AGENT_V10.md
docs/business-rules/_TEMPLATE.business-rules.md
.ai/examples/example-data-question.md
.ai/examples/example-data-analysis-answer.md
V10_DATA_ANALYSIS_UPDATE_REPORT.md
```

## Safety model

- Only SELECT / WITH SELECT / EXPLAIN SELECT.
- Mandatory guardrail script.
- Read-only DSN required.
- Sensitive columns are redacted by default.
- Query logs are written to `.agent/data-analysis/query-log.jsonl`.
- Prefer aggregate business answers over raw data exports.
