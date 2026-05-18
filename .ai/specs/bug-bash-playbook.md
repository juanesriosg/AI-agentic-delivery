# Agent Bug Bash Playbook

Use this when a feature, epic, or risky PR is close to completion.

## 1. Define the charter

```md
Feature:
Critical flows:
Highest risks:
Browsers/devices/environments if relevant:
Data states:
Timebox:
```

## 2. Test core flow

Run the expected happy path once to confirm the environment works.

## 3. Attack edge cases

- Empty values.
- Invalid values.
- Very large values.
- Duplicate actions.
- Refresh/retry/back button.
- Expired or missing auth.
- Wrong role or tenant.
- Slow or failed dependencies.
- Concurrent submissions.
- Missing optional fields.
- Old data shape.

## 4. Capture bugs

For each bug, record expected/actual, reproduction, evidence, severity, and blocking status.

## 5. Convert bugs into tests

Add regression tests for in-scope confirmed bugs when practical.

## 6. Report readiness

Produce a QA handoff with bugs, gaps, and recommended manager action.
