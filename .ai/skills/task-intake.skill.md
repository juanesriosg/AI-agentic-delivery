# Skill: Task Intake and Ready Check

## Purpose

Determine whether a task is ready for autonomous agent work.

## Required task fields

```yaml
id:
title:
business_goal:
technical_goal:
repo:
owner:
reviewer:
acceptance_criteria:
scope:
out_of_scope:
risk_level:
autonomy_level:
validation_required:
rollback_expectation:
dependencies:
```

## Ready criteria

A task is ready when:

- The desired outcome is clear.
- Acceptance criteria are testable.
- Repo is identified.
- Ownership is clear.
- Risk level is known.
- Dependencies are not blocking.
- The agent has enough context to begin.
- The work is small enough for one PR.

## Not ready when

- Requirements are ambiguous.
- Acceptance criteria are missing.
- User behavior is unclear.
- The repo owner is unknown.
- The task requires production credentials.
- The task requires cross-repo coordination not described.
- The task implies destructive changes.
- The task is an epic disguised as one task.

## Output

```md
Ready status: Ready / Not ready / Ready with assumptions
Missing information:
Assumptions:
Suggested split:
Recommended agent:
Recommended risk level:
```
