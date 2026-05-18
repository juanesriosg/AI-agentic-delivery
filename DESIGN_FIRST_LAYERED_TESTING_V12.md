# Design-First Layered Testing Workflow v12

This version makes architecture/design the entry point of the agentic SDLC and makes DB → API → frontend sequencing a hard quality gate.

## Core rule

Agents must not treat unit tests as completion. Unit tests are only the first checkpoint. A task is complete only when the correct layer gate passes:

```text
design gate
  ↓
database/data model gate
  ↓
API/backend contract + DB integration gate
  ↓
frontend component + visual + accessibility + real API/E2E gate
  ↓
QA gate
  ↓
PM acceptance gate
  ↓
Codex PR review gate
  ↓
human AI PM review
```

## Why this exists

A frontend can pass component tests while the API does not exist. An API can pass unit tests while the database schema is wrong. A database migration can pass locally but break integration behavior. v12 blocks that false confidence.

## Agent behavior

Before coding, agents must understand and document:

- data model and business entities
- database/storage access patterns
- API contracts and error semantics
- frontend states and user flows
- AWS/cloud components and Terraform changes
- security, observability, reliability, cost, and scale implications
- programming paradigm decision: data-driven, object-oriented, event-driven, or hybrid
- testing strategy per layer

## Task sequencing

### Database/data model tasks

Database tasks go first when the story touches data. They must produce:

- data model or schema evidence
- migration and rollback evidence when applicable
- repository/query tests
- DB integration tests
- data factory / fixture strategy
- layer gate pass file

### API/backend tasks

API tasks run only after database layer gate evidence exists on the source branch when the story depends on data.

They must produce:

- contract/API spec evidence
- unit tests for business logic
- contract tests
- DB-backed integration tests
- auth/validation/error handling evidence
- observability notes
- layer gate pass file

### Frontend tasks

Frontend tasks run only after API layer gate evidence exists on the source branch when the UI depends on the API.

They must produce:

- component tests
- visual screenshots and annotations
- accessibility evidence
- real API integration/E2E evidence
- no final pass based only on mocks
- layer gate pass file

## Parallel work policy

Parallelism is allowed only when dependencies and files do not overlap.

Allowed examples:

```text
- Design-system token cleanup while DB layer runs
- Cloud/Terraform foundation while database task runs, if paths do not overlap
- Security review in read-only mode
- Data analysis in SELECT-only mode
```

Blocked examples:

```text
- Frontend integration before API gate passed
- API integration before DB gate passed
- Two branches editing the same component/service/schema file
- UI marked done with mocks only
```

## Evidence locations

```text
docs/agentic-evidence/<spec-id>/<task-id>/test-evidence.md
docs/agentic-evidence/<spec-id>/<task-id>/qa-checklist.md
docs/agentic-evidence/<spec-id>/<task-id>/pm-checklist.md
docs/agentic-evidence/<spec-id>/<task-id>/layered-test-matrix.md
docs/agentic-evidence/<spec-id>/layer-gates/database.passed.md
docs/agentic-evidence/<spec-id>/layer-gates/api.passed.md
docs/agentic-evidence/<spec-id>/layer-gates/frontend.passed.md
```

## Required commands

Design gate:

```bash
python .ai/scripts/design_gate.py --spec specs/<feature>.spec.md --allow-not-applicable --markdown-output .agent/design-gate.md
```

Layer gate:

```bash
python .ai/scripts/layer_gate.py \
  --layer api \
  --spec-id <spec-id> \
  --task-id <task-id> \
  --evidence-dir docs/agentic-evidence/<spec-id>/<task-id> \
  --pass-dir docs/agentic-evidence/<spec-id>/layer-gates \
  --write-pass-file
```

Generate a test matrix:

```bash
python .ai/scripts/generate_layered_test_matrix.py \
  --spec specs/<feature>.spec.md \
  --output docs/agentic-evidence/<spec-id>/<task-id>/layered-test-matrix.md
```
