# Skill: Business Context Ingestion

## Purpose

Build a reusable project context pack for product and data analysis agents.

## Sources

- `specs/**`
- `docs/specs/**`
- `.ai/inbox/specs/**`
- `.codex/specs/**`
- `docs/business-rules/**`
- `docs/agentic-evidence/**/pr-notification.md`
- `docs/agentic-evidence/**/pm-checklist.md`
- `docs/agentic-evidence/**/qa-checklist.md`
- `.agent/reports/agents.log.md`

## Command

```bash
python .ai/scripts/build_business_context.py \
  --output docs/agentic-business-context/context-pack.md \
  --json-output docs/agentic-business-context/context-pack.json
```

## Expected output

- Project summary.
- Active features/specs.
- Recent PR summary.
- Business rules.
- Known metrics.
- Open business questions.
- Data entities and likely source tables.
