# Branch Spec Workflow — ChatGPT Specs to Autonomous Agent Implementation

This workflow supports the manager pattern where high-quality specs are written with ChatGPT/pro models, pushed to a development branch, and then autonomous agents begin implementation, testing, QA handoff, and release readiness work.

## Default flow

1. The manager creates a spec with ChatGPT/pro models.
2. The manager pushes the spec to a watched branch, usually `dev/<feature>`, `develop`, `spec/<feature>`, `chatgpt/<feature>`, or `ai-spec/<feature>`.
3. The spec is committed under a watched path such as `specs/`, `.ai/inbox/specs/`, `docs/specs/`, `requirements/specs/`, or `.codex/specs/`.
4. GitHub Actions runs `.github/workflows/agent-spec-ingestion.yml`.
5. The workflow detects new or modified spec files.
6. The workflow validates spec quality and generates a spec-to-test traceability matrix.
7. The workflow creates an `ai:ready` GitHub issue and/or calls an agent dispatch webhook.
8. Codex Cloud or another coding agent checks out the spec branch, reads the spec, creates an implementation branch, and opens a PR back to the source spec branch.
9. The agent runs unit, component, integration, contract, E2E, dev, QA, and regression checks as appropriate for the change.
10. The manager reviews the PR or feature completion report at daily review time.

## Branch and PR model

Default policy:

```text
Spec branch:             dev/<feature>
Spec path:               specs/<feature>.spec.md
Agent implementation:    ai/<spec-id>-<slug>
Agent PR target:         dev/<feature>
Manager/repo owner PR:   dev/<feature> -> main/release branch
```

This keeps agent implementation isolated while letting the spec branch remain the source of truth for the feature.

## Automation modes

The included workflow supports three levels of automation.

### Mode 1 — GitHub issue dispatch

The workflow creates a GitHub issue containing the full agent task. A Codex Cloud runner, human, or issue-driven agent can pick it up.

### Mode 2 — Repository dispatch

The workflow can emit `repository_dispatch` events for downstream automation if your organization uses another workflow or GitHub App as the agent runner.

### Mode 3 — Webhook dispatch

If `AGENT_DISPATCH_WEBHOOK_URL` is configured, the workflow posts a JSON task payload to that URL. Use this to connect a Codex Cloud adapter, internal worker, or agent orchestration service.

The kit does not assume a vendor-specific Codex Cloud API. Instead, it provides a stable, repo-native task payload that your Codex Cloud integration can consume.

## Deployment policy

Agents may prepare deployment evidence and execute non-production deployment only when explicitly configured.

Default:

```text
Dev/test deployment: allowed only if repo has a safe deploy script and ALLOW_AGENT_DEV_DEPLOY=true
QA deployment: requires manager/repo owner approval unless explicitly delegated
Production deployment: never automatic by default
```

Deployment must never bypass tests, ownership boundaries, environment approvals, or rollback requirements.

## Manager expectation

The manager should not need to monitor the agent all day. The agent must notify when:

- a spec is not implementation-ready,
- a clarification is needed,
- a PR is ready,
- a feature is agent-complete,
- QA handoff is ready,
- deployment readiness is reached,
- a bug is discovered,
- an epic is complete or blocked.
