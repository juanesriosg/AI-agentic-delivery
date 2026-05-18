# Example Codex Cloud Task Prompt

Read `AGENTS.md` first.

Use these policies:

- `.ai/runtime/runtime-contract.md`
- `.ai/runtime/codex-cloud.runtime.md`
- `.ai/specs/clean-code-standard.yml`
- `.ai/specs/scalable-engineering-standard.yml`
- `.ai/specs/deletion-protection-policy.yml`

Task:

```md
Repo:
Issue/task:
Business goal:
Technical goal:
Acceptance criteria:
Scope:
Out of scope:
Risk level:
Autonomy level: L3
```

Before coding:

```bash
.codex/bootstrap.sh
```

Before PR:

```bash
.codex/run-quality-gate.sh
```

When done:

- Open a PR.
- Fill every PR template section.
- Comment with status.
- Move task to `manager:review`.
- Continue to the next `ai:ready` task if the cloud session and WIP limits allow.
