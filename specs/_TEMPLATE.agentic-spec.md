---
spec_id: SPEC-YYYYMMDD-short-slug
story_id: STORY-short-slug
title: "Short, human-readable feature title"
status: draft
priority: medium
risk_level: medium
owner: "@github-user-or-team"
source_branch: "dev/<feature-or-story>"
target_branch: "dev/<feature-or-story>"
expected_pr_strategy: one-responsibility-per-pr
created_at: "YYYY-MM-DD"
updated_at: "YYYY-MM-DD"
---

# Agentic Spec: <Feature / User Story Title>

## 0. Spec control

**Spec ID:** SPEC-YYYYMMDD-short-slug  
**Story ID:** STORY-short-slug  
**Author:** <person or ChatGPT session>  
**Product owner / AI PM:** @<github-user>  
**Repo:** <owner/repo>  
**Source branch:** `dev/<feature-or-story>`  
**Target branch for agent PRs:** `dev/<feature-or-story>`  
**Expected PR strategy:** one responsibility per PR  
**Status:** draft — change to `ready_for_agents` only when the copied spec is complete.  
**Autonomy level:** L3 by default: agents may branch, code, test, open PR, and notify; agents may not merge or deploy production without approval.

## 1. Description

Describe the feature, bug, improvement, or research task in plain language.

Include:
- What should exist after this work is complete.
- Who needs it.
- Why it matters now.
- What problem it solves.

**Example:**  
Users need a registration form that lets them create an account with name, email, password, and password confirmation. The form must validate input, be accessible, display errors clearly, and integrate with the existing authentication API.

## 2. Business need

Explain the business or user outcome.

| Question | Answer |
|---|---|
| Who is the user or stakeholder? | <user/customer/team> |
| What outcome do they need? | <outcome> |
| What pain exists today? | <pain> |
| What metric, signal, or behavior should improve? | <metric/signal> |
| What is the cost of not doing this? | <risk/opportunity cost> |

## 3. User needs and scenarios

Write the user-facing needs. These become PM and QA acceptance checks.

### Primary user story

As a `<type of user>`, I want `<capability>`, so that `<benefit>`.

### User scenarios

| Scenario ID | Scenario | Expected outcome |
|---|---|---|
| US-001 | <user action or situation> | <expected result> |
| US-002 | <edge case> | <expected result> |
| US-003 | <error case> | <expected result> |

## 4. Requirements

### 4.1 Functional requirements

Each requirement must be testable.

| ID | Requirement | Priority | Acceptance signal | Owner agent |
|---|---|---|---|---|
| FR-001 | <what the system must do> | must | <how QA knows it works> | frontend/backend/etc. |
| FR-002 | <what the system must do> | should | <how QA knows it works> | frontend/backend/etc. |

### 4.2 Non-functional requirements

| ID | Requirement | Target / constraint | Validation method |
|---|---|---|---|
| NFR-SEC-001 | Security | <auth, permission, data handling> | security review / tests |
| NFR-REL-001 | Reliability | <timeouts, retries, idempotency, recovery> | integration tests / chaos or failure tests if relevant |
| NFR-PERF-001 | Performance | <latency, throughput, bundle size, query limit> | benchmark / profiler / load test |
| NFR-UX-001 | Usability | <intuitive path, accessible labels, feedback> | PM checklist / UX review |
| NFR-A11Y-001 | Accessibility | <WCAG target, keyboard nav, screen reader> | accessibility QA |
| NFR-OBS-001 | Observability | <logs, metrics, traces, audit events> | telemetry evidence |
| NFR-COST-001 | Cost | <avoid waste, managed services, bounded usage> | cost review |

### 4.3 Data requirements

| Field / entity | Source | Validation | Sensitivity | Retention / lifecycle |
|---|---|---|---|---|
| <field> | <user/API/db> | <rules> | public/internal/confidential/PII | <policy> |

### 4.4 API / contract requirements

| API / event / contract | Change type | Request | Response | Compatibility expectation |
|---|---|---|---|---|
| <endpoint/event> | add/change/remove | <shape> | <shape> | backward compatible / breaking / unknown |

## 5. Scope

### In scope

- <specific item>
- <specific item>

### Out of scope

- <specific item that agents must not implement>
- <future work that should become another spec>

### Explicit non-goals

- <things that are intentionally not part of this story>

## 6. Files and areas to touch

Use this section to guide agents and prevent broad, risky changes.

### Expected files / directories to touch

| Path / pattern | Expected change | Owner agent | Required? |
|---|---|---|---|
| `src/...` | <change> | frontend/backend/etc. | yes/no |
| `tests/...` | <tests to add/update> | qa/dev | yes/no |
| `infra/terraform/...` | <infrastructure as code only> | cloud/terraform | only if AWS changes are needed |

### Files / directories that must not be touched without approval

| Path / pattern | Reason | Approval required from |
|---|---|---|
| `migrations/**` | data risk | manager / db owner |
| `infra/**` | cloud risk | cloud owner / manager |
| `.github/workflows/**` | deployment risk | manager / DevOps owner |
| `auth/**` | security risk | security owner / manager |

### Unknown files to discover

List areas the agents should investigate before coding.

- <module to inspect>
- <existing component to reuse>
- <test pattern to follow>

## 7. Design / UX expectations

Required for UI or user-facing work.

| Area | Expectation |
|---|---|
| Layout | <desktop/mobile behavior> |
| States | empty, loading, valid, invalid, error, success, disabled |
| Feedback | <how errors/success are shown> |
| Accessibility | labels, focus order, keyboard navigation, screen reader text |
| Screenshots required | yes/no; list viewports/states |
| Design system | <components/tokens/patterns to reuse> |

## 8. Architecture expectations

Explain how the solution should fit the system.

| Area | Expectation |
|---|---|
| Pattern to prefer | <simple module, service, adapter, repository, CQRS, event-driven, etc.> |
| Pattern to avoid | <anti-patterns or banned approaches> |
| Boundaries | <what layer owns what responsibility> |
| Dependencies | <allowed or disallowed dependencies> |
| Concurrency | <idempotency, race conditions, locks, queues, async behavior> |
| Scale | <pagination, batching, caching, rate limits, timeouts> |
| Observability | <logs/metrics/traces/events> |


## 8.1 Layer order / dependency order

Use this section for any story that touches more than one layer. Agents must follow this order unless the spec explicitly says a layer is not applicable.

```text
database / data model → API / backend → frontend / UI
```

| Layer | Required? | What must be true before next layer starts | Evidence expected |
|---|---|---|---|
| Database / data model | yes/no | data model, schema/repository behavior, test data, and DB integration pass | `docs/agentic-evidence/<spec-id>/layer-gates/database.passed.md` |
| API / backend | yes/no | API contract, validation, DB-backed integration, errors/auth pass | `docs/agentic-evidence/<spec-id>/layer-gates/api.passed.md` |
| Frontend / UI | yes/no | component tests, visual/accessibility, real API/E2E pass | `docs/agentic-evidence/<spec-id>/layer-gates/frontend.passed.md` |

### Important

Frontend mocks are allowed only for early component tests. They are not final integration evidence. API unit tests are not enough when the API depends on a database.

## 8.2 Programming paradigm and design pattern decision

Choose the simplest paradigm that fits the problem.

| Option | Use here? | Why / why not |
|---|---|---|
| Data-driven programming | yes/no | <business rules, transformations, analytics, config-driven behavior> |
| Object-oriented programming | yes/no | <domain entities, invariants, strategies, adapters, repositories> |
| Event-driven programming | yes/no | <async work, queues/events, retries, idempotency, decoupling> |
| Functional/procedural style | yes/no | <simple pure transformations or small isolated logic> |

Selected approach: <data-driven / object-oriented / event-driven / hybrid / functional-procedural>  
Design patterns to use: <repository, adapter, strategy, factory, observer, CQRS, etc., or none>  
Patterns to avoid: <god service, hidden global state, unnecessary abstraction, etc.>

### 8.1 Data model / database contract

Describe the entities, tables, fields, validation rules, indexes, retention, sensitivity, and migration/rollback strategy. If this story does not require data model changes, write **Not applicable** and explain the existing data source.

### 8.2 Programming paradigm and design pattern decision

State whether the implementation should use data-driven programming, object-oriented/domain boundaries, event-driven programming, functional/procedural logic, or a hybrid. Explain why the selected paradigm fits this task and what pattern must be avoided.

## 9. AWS / cloud / infrastructure expectations

Use when the work touches AWS, cloud, deployment, environments, or infrastructure.

| Question | Answer |
|---|---|
| Does this require new AWS components? | no/yes/unknown |
| Must infrastructure be changed? | no/yes/unknown |
| Terraform required? | no by default; yes for all new/changed AWS components |
| Environment targets | local/dev/qa/staging/prod |
| Secrets or credentials needed? | yes/no; never include secret values |
| Deployment path | GitHub workflow + Terraform + approved environment |
| Rollback expectation | <rollback approach> |

Required cloud rule:

> New AWS components must be implemented through Terraform and GitHub workflows. Agents must not create AWS resources manually with console or ad-hoc CLI commands unless an explicit emergency exception is approved.

## 10. Testing expectations

Agents must map every acceptance criterion to tests or a documented reason why it cannot be tested yet.

| Test type | Required? | What to test | Evidence expected |
|---|---|---|---|
| Unit tests | yes/no | <logic/components> | test output |
| Component tests | yes/no | <UI/component/service module> | test output |
| Integration tests | yes/no | <API/db/external dependency> | test output |
| Contract tests | yes/no | <API/event contract> | test output |
| E2E tests | yes/no | <user flow> | test output + screenshots if UI |
| Visual QA | yes/no | <states/viewports> | screenshots/annotations |
| Accessibility QA | yes/no | <keyboard/screen reader/labels> | checklist/tool output |
| Security tests | yes/no | <auth/input validation/secrets> | scan/review evidence |
| Performance tests | yes/no | <latency/load/query count> | benchmark/load evidence |
| Local manual/dev test | yes/no | <local app behavior> | notes/screenshots |

## 10.1 Layer order / dependency order

Define the exact implementation and testing order. For full-stack work, the required default is:

1. Design gate.
2. Database/data model gate.
3. API/backend contract + DB integration gate.
4. Frontend/UI + real API/E2E gate.
5. QA, PM, Dev Manager, Codex review, and human review.

If a layer is not needed, explicitly mark it **Not applicable** and explain why. Unit tests alone are never enough when a downstream layer depends on an upstream layer.

## 11. Acceptance criteria

These are the conditions for QA Agent and PM Agent approval.

| ID | Acceptance criterion | Type | Validated by | Evidence |
|---|---|---|---|---|
| AC-001 | <observable result> | functional | QA Agent | <test/checklist/screenshot> |
| AC-002 | <observable result> | product/usability | PM Agent | <PM checklist> |
| AC-003 | <observable result> | technical | Dev Manager Agent | <review/gate> |

## 12. Agent routing hints

List which agents should participate.

| Agent | Needed? | Reason |
|---|---|---|
| Product Requirements Agent | yes/no | <reason> |
| UX / UI Designer Agent | yes/no | <reason> |
| Frontend Engineer Agent | yes/no | <reason> |
| Backend Engineer Agent | yes/no | <reason> |
| API Contract Engineer Agent | yes/no | <reason> |
| Database Engineer Agent | yes/no | <reason> |
| Cloud / Terraform Agent | yes/no | <reason> |
| Security Agent | yes/no | <reason> |
| QA Checklist Agent | yes | every story/task needs QA |
| Visual QA Agent | yes/no | UI changes |
| Accessibility QA Agent | yes/no | user-facing UI |
| PM Acceptance Agent | yes | every story needs PM acceptance |
| Dev Manager PR Governor | yes | every PR needs scope/quality gate |

## 13. PR decomposition plan

Agents must keep one responsibility per PR.

| PR | Responsibility | Expected files | Depends on | Target branch |
|---|---|---|---|---|
| PR-1 | <single responsibility> | <paths> | none | `dev/<feature>` |
| PR-2 | <single responsibility> | <paths> | PR-1 | `dev/<feature>` |

If the agent discovers this spec is too large, it must split it into smaller tasks before coding.

## 14. Risks, assumptions, and clarifications

### Known assumptions

| ID | Assumption | Impact if wrong | How to validate |
|---|---|---|---|
| A-001 | <assumption> | <impact> | <validation> |

### Clarifications needed

| ID | Question | Blocking? | Safe progress allowed while waiting |
|---|---|---|---|
| Q-001 | <question> | yes/no | <what agents can still do> |

### Risks

| ID | Risk | Severity | Mitigation | Owner agent |
|---|---|---|---|---|
| R-001 | <risk> | low/medium/high | <mitigation> | <agent> |

## 15. Definition of done

A task is done only when:

- [ ] Implementation is complete for the task scope.
- [ ] QA Agent checklist passes.
- [ ] PM Agent checklist passes for story-level user value.
- [ ] Dev Manager Agent confirms one responsibility per PR.
- [ ] Tests are added or updated according to this spec.
- [ ] Screenshots or visual evidence are attached for UI changes.
- [ ] Accessibility evidence exists for user-facing UI changes.
- [ ] Terraform is used for new AWS components.
- [ ] No protected files were deleted or modified without approval.
- [ ] `agents.log` records each agent iteration.
- [ ] PR summary is concise and includes evidence links.
- [ ] Rollback or revert path is documented.

## 16. Done notification requirements

When the PR is ready, agents must notify the manager with:

- PR link.
- One-sentence summary.
- Responsibility of the PR.
- Validation status.
- Screenshots/evidence links.
- Risk level.
- Files worth reviewing carefully.
- Open questions, if any.
- Tag: @<manager-github-user>

## 17. Appendix: references, examples, data, screenshots

Attach or link supporting material:

- Existing screenshots.
- Data samples.
- API examples.
- Logs.
- Stakeholder notes.
- Related PRs/issues.
- Existing components to reuse.
