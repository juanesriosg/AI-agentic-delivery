# Generic Agentic Spec Template Guide

Use this template for any feature, bugfix, infrastructure change, data change, or product experiment that should be implemented by the agentic SDLC.

## Recommended location

For product work, use the PRD/TRD/task-list package:

```text
specs/<story-or-feature>/prd.md
specs/<story-or-feature>/implementation-plan.md
specs/<story-or-feature>/trds/trd-<task-id>-<short-slug>.md
specs/<story-or-feature>/tasks/tasks-trd-<task-id>-<short-slug>.md
```

Place legacy single-file specs in one of these paths so the repo-level automation can detect them:

```text
specs/<story-or-feature>.spec.md
specs/<story-or-feature>.spec.yml
.ai/inbox/specs/<story-or-feature>.spec.md
.codex/specs/<story-or-feature>.spec.md
```

Recommended branch:

```text
dev/<story-or-feature>
```

## Template formats

This package includes:

```text
specs/_TEMPLATE.spec-package.md
specs/_TEMPLATE.prd.md
specs/_TEMPLATE.implementation-plan.md
specs/_TEMPLATE.trd.md
specs/_TEMPLATE.task-list.md
specs/_TEMPLATE.agentic-spec.md
specs/_TEMPLATE.agentic-spec.yml
```

Use the PRD/TRD/task-list templates for substantial product work. Use the older agentic templates only for small one-file changes.
Use YAML when you want automation to parse the spec more strictly.

## Readiness status

Reusable templates are `draft` by default. A real copied spec should be changed to:

```yaml
status: ready_for_agents
```

Only specs with an allowed ready status are automatically implemented. In a PRD/TRD package, set `ready_for_agents` on the most granular document that should run. Prefer a task list over a TRD, a TRD over an implementation plan, and an implementation plan over a PRD.

## Minimum fields before agents should start coding

The agentic workflow can start only when these sections are understandable:

```text
Description
Business need
User need or scenario
Functional requirements
Acceptance criteria
Scope
Files / areas to touch
Files / areas not to touch
Testing expectations
Definition of done
```

If a section is missing, agents should create a clarification request, but they can still make safe progress through discovery, test planning, fixture creation, and existing behavior analysis.

## What makes a good spec

A good spec is not necessarily long. A good spec is precise.

Good:

```text
The registration form must show an inline error below the email input when the email is invalid. The submit button remains disabled until required fields are valid.
```

For package documents, see `.ai/specs/spec-package-convention.md`.

Weak:

```text
Make the form better.
```

## Files to touch

The `Files and areas to touch` section is important because it controls agent behavior.

Use it to say:

```text
Expected files:
- src/features/register/**
- src/components/forms/**
- tests/e2e/register.spec.ts

Do not touch without approval:
- infra/**
- migrations/**
- auth/**
- .github/workflows/**
```

This lets the agents move fast while avoiding accidental broad changes.

## How this supports one-responsibility PRs

The `PR decomposition plan` section tells the Spec Task Splitter Agent how to divide the work. For example:

```text
PR-1: frontend form UI and validation
PR-2: backend registration API integration
PR-3: E2E tests and visual QA evidence
PR-4: Terraform or deployment changes, only if needed
```

The Dev Manager PR Governor checks that each PR stays focused.

## AWS / cloud rule

If the spec requires a new AWS component, the spec must say so. Agents must use Terraform and GitHub workflows for AWS changes. This keeps infrastructure versioned, reviewable, and aligned with operations-as-code and small reversible change practices.
## v12 Design-first / layered testing additions

Every spec that touches data, APIs, or UI must clearly define:

- data model / schema / storage shape, or explicitly state `Not applicable`;
- API contract / endpoint / event interface, or explicitly state `Not applicable`;
- frontend design and states, or explicitly state `Not applicable`;
- cloud/AWS/Terraform components, or explicitly state `Not applicable`;
- layer order: `database → API → frontend`;
- programming paradigm decision: data-driven, object-oriented, event-driven, functional/procedural, or hybrid;
- test plan per layer: database, API, frontend, integration, E2E, QA, PM.

Unit tests alone are not completion. Downstream layers are blocked until upstream layer gates pass.
