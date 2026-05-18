# Skill: Agent Logging

Use this skill every time an agent starts, completes, fails, blocks, creates feedback, closes feedback, or promotes a story.

## Command

```bash
python .ai/scripts/agent_log.py --agent <agent> --story <story-id> --stage <stage> --action "<action>" --status <status>
```

## Rules

- Append-only.
- No secrets.
- Log failed iterations.
- Include evidence refs when available.
- Generate markdown summary before PR notification.
