# Skill: Mandatory Codex PR Review

## Goal

Every pull request must receive an independent Codex AI review before human approval.

## Required mechanisms

1. GitHub Action gate:
   - `.github/workflows/agentic-codex-pr-review.yml`
   - required check name: `Agentic Codex PR Review / codex_review_gate`
   - uses `openai/codex-action@v1`
   - parses Codex output with `.ai/scripts/codex_pr_review_gate.py`

2. Optional official Codex mention:
   - `.github/workflows/agentic-codex-review-request.yml`
   - posts `@codex review` once per PR head SHA
   - requires Codex GitHub integration to be enabled in Codex settings

## Agent behavior

Before asking the manager to approve a PR, the agent must verify:

```text
QA gate: pass
PM gate: pass or not applicable for technical-only task
Dev-manager gate: pass
Codex PR Review Gate: pass
```

If Codex fails the PR:

1. Read the blocking findings.
2. Route each finding to the correct owner agent.
3. Fix the PR in the same one-responsibility scope when possible.
4. Add or update tests/evidence.
5. Push a new commit.
6. Let the Codex review gate run again.
7. Do not request human approval until the gate passes or the manager explicitly overrides.

## Evidence

The Codex review workflow stores artifacts under:

```text
.agent/codex-review/
```

The PR comment contains the gate result and links to the workflow artifacts.
