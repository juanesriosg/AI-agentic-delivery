# One-Responsibility PR Standard

Every agent-created PR must be easy for a senior developer / product manager to understand, debug, reject, approve, or return to later.

## Required

- One business goal.
- One technical responsibility.
- One clear rollback path.
- Concise PR body.
- Evidence links or files.
- `agents.log` for the iterations.
- Tests appropriate to the change.
- Screenshots for UI changes.
- Terraform plan for AWS infrastructure changes.

## Not allowed

- Mixing frontend, backend, database, and cloud changes in one PR unless the story is tiny and the dev-manager agent explicitly approves.
- Large opportunistic refactors.
- Deleting tests to make CI pass.
- Changing production config without release gate approval.
- Creating AWS resources manually outside Terraform/GitHub workflows.

## PR title format

```text
<type>(<scope>): <short responsibility>
```

Examples:

```text
feat(register): add frontend form validation
feat(register-api): add registration endpoint contract
infra(register): add Lambda Terraform module
fix(register-ui): prevent placeholder overlap on mobile
```

## PR body length

Keep it concise. The PR body should summarize; evidence files can hold details.

Recommended sections:

```text
Summary
Why
Validation
Screenshots / evidence
Risks
Rollback
Review focus
AI agent log
```

## Branch conflict rule

One responsibility per PR also means one clear file ownership boundary per active branch. If another active non-main branch already changed or reserved a file, a new agent task must not edit that file.

The correct response is to split the task, create a smaller component/service/adapter, or move to another task. Do not create a PR that makes the manager solve an avoidable merge conflict.

## v12 layer responsibility

A PR must not mix database, API, and frontend work when the layers can be separated. Prefer:

```text
PR 1: data model / database
PR 2: API/backend contract using the validated data layer
PR 3: frontend using the validated API
```

A combined PR is allowed only when the change is tiny, cannot be safely split, and the dev-manager agent documents why splitting would increase risk.
