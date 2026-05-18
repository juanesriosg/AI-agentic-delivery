# Repo Installation v2

Copy these files to each repo:

```text
AGENTS.md
.ai/
.github/
.codex/        # optional but recommended for Codex Cloud setup/validation hooks
```

Then customize:

```text
.ai/runtime/task-environments.yml
.ai/specs/ownership-boundaries.yml
.ai/specs/autonomy-levels.yml
.ai/specs/restricted-operations.yml
.github/CODEOWNERS
```

## Required repo-specific decisions

- Default branch.
- Repo owner.
- Allowed autonomy level.
- Protected paths.
- Required validation commands.
- Which tests can run in Codex Cloud.
- Which tests need local/staging resources.
- Whether agents can open PRs automatically.
- Whether agents can continue to the next task automatically.

## First PR in every repo

Run:

```md
Use Repo Scout Agent and Cloud Runtime Engineer Agent.
Create a repo context pack and verify local/cloud bootstrap.
Do not change production code.
```
