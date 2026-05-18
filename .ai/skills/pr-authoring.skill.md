# Skill: PR Authoring and Notification

## Purpose

Create PRs that managers and repo owners can review quickly.

## PR title

```text
[AI][<type>] <short result-oriented title>
```

Examples:

```text
[AI][Bugfix] Prevent duplicate invoice creation on retry
[AI][Feature] Add CSV export for customer report
[AI][Test] Add regression coverage for account lockout
```

## PR body sections

```md
## Summary
What changed in plain language.

## Business goal
Why this matters.

## Technical notes
Important implementation details.

## Validation
Commands run and results.

## Risk
Low / Medium / High, with explanation.

## Rollback
How to revert safely.

## Files worth reviewing carefully
Focused list for the manager/reviewer.

## Assumptions
Anything assumed.

## Follow-up
Non-blocking improvements.

## Task / Epic
Links.
```

## Manager notification

After PR creation:

```md
Status: PR ready
Task:
Repo:
Branch:
PR:
Validation:
Risk:
Files worth reviewing:
Manager action needed:
Next agent action:
```

## Rules

- Do not mark PR ready with failing related tests.
- Do not hide skipped tests.
- Do not omit risk.
- Do not omit rollback.
- Keep the PR focused.
