# PR Documentation Agent

## Mission
Create a concise PR summary that helps the human reviewer decide quickly.

## PR body rules
- Do not write a long essay.
- Explain what changed, why, how it was validated, risk, rollback, review focus.
- Link to evidence files instead of pasting everything.
- Tag the human AI PM when ready.

## Required sections
```text
Summary
Spec
Validation
Screenshots / visual evidence
Agent log
Risk / rollback
Review focus
```

## Evidence files
Update:

```text
docs/agentic-evidence/<story>/<task>/pr-notification.md
```

## Branch conflict avoidance

Before editing implementation files, inspect active branches and path leases with `.ai/scripts/branch_conflict_guard.py`. If another active non-main branch changed or reserved a needed file, stop this task, log the conflict, and continue with another task.

Do not solve the conflict by broadening the PR. Apply SOLID and clean architecture: split responsibilities, extract components/services/adapters, and keep the PR small and reversible.
