# Required status checks for agentic repositories

Require these checks in branch protection for branches that receive agent PRs.

Minimum required checks:

```text
Agentic Codex PR Review / codex_review_gate
agentic-pr-guardrails
agent-guardrails
agent-pr-checks
```

For AWS/Terraform repositories also require:

```text
agentic-terraform-plan
```

For UI repositories also require visual QA and E2E checks when available.

## Human approval rule

Human approval should happen after checks pass, not before.

Manager approval is allowed only after:

```text
QA gate passed
PM gate passed when product/user story work
Dev-manager gate passed
Codex PR Review Gate passed
```

## v11 required branch conflict check

Add this required check to protected branches:

```text
Agentic branch conflict guard / branch_conflict_guard
```

This check prevents two active non-main branches from touching the same implementation file.

## v12 required design/layer gate check

Add this required check to protected branches:

```text
Agentic design and layer gates / design_layer_gates
```

This check keeps design/spec updates explicit and ensures layer gate evidence remains parseable. The repo-level orchestrator also runs `.ai/scripts/design_gate.py` before coding and `.ai/scripts/layer_gate.py` before PR guardrails.

## v15 required self-improvement check

For PRs that change agent instructions, skills, evals, prompts, or agent workflow scripts, require:

```text
Agentic skill improvement gate / skill_improvement_gate
```

Self-improvement PRs still also require:

```text
Agentic Codex PR Review / codex_review_gate
```

No self-improvement PR should be merged by agents. Human AI PM approval is required.
