## Spec comprehension

Business goal:
Technical goal:
User / stakeholder:
Source spec:
Acceptance criteria satisfied:
- AC-001:

Assumptions:
- A-001:

Clarifications asked / resolved:
- Q-001:

## Test traceability

| AC | Unit | Component | Integration | Contract | E2E | Dev/QA | Evidence | Status |
|---|---|---|---|---|---|---|---|---|

## QA checklist

QA checklist path or artifact:
QA decision: Pass / Fail / Blocked
Open QA feedback:
-

## PM checklist

PM checklist path or artifact:
PM decision: Pass / Fail / Human AI PM decision needed
Open PM feedback:
-

## Agent iterations / agents.log

agents.log path/artifact:

| Agent | Iteration | Stage | Action | Status | Evidence |
|---|---:|---|---|---|---|

## Agent-to-agent feedback

| Feedback | From | Owner | Severity | Status | Evidence |
|---|---|---|---|---|---|

## Screenshots / visual evidence

Required for UI changes. Use `not UI-related` only when true.

| State | Viewport | Screenshot / annotation | Status |
|---|---|---|---|

## Mandatory Codex AI review

Codex PR Review Gate: Pending / Pass / Fail / Blocked
Required status check: `Agentic Codex PR Review / codex_review_gate`
Codex review artifact/comment:
Open Codex findings:
-

Manager approval must wait until the Codex PR Review Gate passes or the human manager explicitly documents an override.

## Summary

<!-- What changed? -->

## Business goal

<!-- Why does this matter? -->

## Technical notes

<!-- Important implementation details. -->

## Runtime

Runtime detected:
Bootstrap commands:
Bootstrap result:

## Validation

```text
command:
result:
```

## Agent self-review

Quality score: __/100
Findings fixed:
-
Findings accepted as follow-up:
-

## Scale/readiness review

Scale consideration:
- Expected current usage:
- Main growth risk:
- Boundary/limit added:
- Observability added:
- Follow-up needed before larger scale:

## Architecture impact

Pattern/architecture changes:
ADR required: Yes / No
ADR link:
Reversibility: Two-way door / One-way door

## Security impact

Auth/authz changed: Yes / No
Sensitive data touched: Yes / No
Secrets/config touched: Yes / No
Security reviewer required: Yes / No

## Cloud / deployment impact

Cloud/infrastructure changed: Yes / No
Deployment changed: Yes / No
Promotion target: dev / qa-user / staging / prod-ready / none
Production deployment required: No by default

## Deletions and data safety

Files deleted:
Data deletion risk: None / Low / Medium / High
Approval required: Yes / No

## Risk

Risk level: Low / Medium / High
Reason:

## Rollback

<!-- How can this be reverted or disabled safely? -->

## Files worth reviewing carefully

-



## Self-improvement impact

Use this section only when the PR changes `.ai/agents`, `.ai/skills`, `.ai/specs`, `.ai/evals`, Codex prompts, or agent workflow scripts.

Self-improvement proposal path:
Feedback bundle path:
Eval report path:
Skill guardrail report path:
Behavior changed:
Safety boundaries preserved: Yes / No
Human manager approval required: Yes

## Human AI PM requested action

Review / Approve / Request changes / Decide tradeoff

## Agent checklist

- [ ] Acceptance criteria satisfied.
- [ ] QA checklist completed and passed or gaps documented.
- [ ] PM checklist completed and passed or human decision requested.
- [ ] Agent feedback closed or explicitly deferred.
- [ ] agents.log summary included.
- [ ] Screenshots/visual evidence included for UI changes.
- [ ] Accessibility reviewed for user-facing changes.
- [ ] Relevant tests added or updated.
- [ ] Validation commands run.
- [ ] Self-review completed.
- [ ] Scale/readiness review completed.
- [ ] No unrelated broad refactor.
- [ ] No protected file deletion.
- [ ] No secrets committed.
- [ ] Risk documented.
- [ ] Rollback documented.
