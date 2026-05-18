# Skill: Testing and Validation

## Purpose

Produce evidence that the change works and does not break expected behavior.

## Validation hierarchy

1. Regression test for bug or behavior.
2. Unit tests for new logic.
3. Integration tests for interactions.
4. Contract tests for APIs.
5. End-to-end tests for critical user flows.
6. Lint/typecheck.
7. Build.
8. Manual verification when automation is insufficient.

## Test quality criteria

Tests should:

- Fail before the fix when practical.
- Cover acceptance criteria.
- Include edge cases.
- Avoid brittle implementation details.
- Be deterministic.
- Be readable.
- Match existing test style.

## Handling missing tests

If the repo has no useful tests:

1. Add the smallest meaningful test.
2. Document why broader tests are missing.
3. Recommend follow-up mechanism improvement.

## Handling failing tests

If tests fail:

1. Identify whether failure is related to change.
2. Fix related failures.
3. Document unrelated failures with evidence.
4. Escalate if unrelated failures block validation.
5. Never delete or weaken tests to pass.

## Output

```md
Validation:
- Command:
  Result:
  Evidence:
Tests added:
Tests changed:
Manual verification:
Known gaps:
```


## v3 required testing expansion

For each task, the agent must explicitly decide whether each level applies:

| Level | Applies? | Evidence or gap |
|---|---|---|
| Spec validation | yes | |
| Unit | yes/no | |
| Component | yes/no | |
| Integration | yes/no | |
| Contract | yes/no | |
| E2E | yes/no | |
| Dev test | yes/no | |
| QA test | yes/no | |
| Regression | yes/no | |

A skipped level is acceptable only when the reason is clear and risk is low.

Feature and epic completion require QA handoff, not only code-level tests.
