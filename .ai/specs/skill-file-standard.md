# Skill File Standard

A skill file should read like guidance for a strong teammate, not a brittle decision tree.

## Required sections

```md
# Skill: <name>

## Purpose
...

## Operating context
...

## Principles
...

## Procedure
...

## Quality bar
...

## Uncertainty behavior
...

## Feedback hooks
...
```

## Writing rules

- Prefer durable judgment over one-off patches.
- Keep the core skill concise.
- Use examples only when they generalize.
- Do not add contradictory instructions.
- Do not weaken safety boundaries.
- Do not repeat global AGENTS.md rules unless the skill needs a local interpretation.
- Move long examples into `.ai/examples/` or `.ai/evals/`.

## Review checklist

- What behavior will change?
- What evidence justifies the change?
- What eval proves the change helps?
- What risk does the change introduce?
- How can it be rolled back?
