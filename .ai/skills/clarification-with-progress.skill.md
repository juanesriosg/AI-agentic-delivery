# Skill: Clarification with Continuous Progress

## Purpose

Ask necessary questions without stopping all useful engineering work.

## Rule

A clarification should block only the specific decision it affects.

## Process

1. Identify the uncertainty.
2. Classify it:
   - Blocking implementation.
   - Blocking only QA acceptance.
   - Non-blocking assumption.
   - Architecture/owner decision.
3. Ask the smallest possible question.
4. State the safe default assumption.
5. State what progress can continue.
6. Continue with safe progress.

## Safe progress examples

- Repository discovery.
- Test command discovery.
- Existing behavior characterization.
- Failing regression test for known bug.
- Component test harness.
- Non-controversial validation setup.
- Documentation of assumptions.
- Bug reproduction.
- Contract/schema inspection.

## Unsafe progress examples

- Changing public behavior based on a guess.
- Modifying auth, billing, security, infrastructure, migrations, or production config based on an assumption.
- Deleting data or files while waiting for clarification.
- Merging, deploying, or marking QA-ready.

## Clarification format

```md
Clarification needed:
- ID: Q-001
- Related AC: AC-003
- Question:
- Why it matters:
- Blocking: yes/no
- Safe assumption if unanswered:
- Safe progress I will continue:
```
