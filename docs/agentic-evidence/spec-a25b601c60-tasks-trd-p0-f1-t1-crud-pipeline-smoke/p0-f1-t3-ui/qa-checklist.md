# QA Checklist

- [x] Spec and TRD reviewed for the UI layer task.
- [x] Frontend scope kept to one responsibility: React CRUD page plus API adapter and component tests.
- [x] Accessibility basics included: visible labels for Title and Body, keyboard-reachable buttons, form semantics, status/error regions, and explicit required/optional guidance.
- [x] Exact blocker recorded for visual/E2E/browser validation: Node.js is unavailable in this runtime.
- [x] Current validation pass confirmed the blocker still applies after rechecking `node --version`.
- [x] The API adapter now tolerates non-JSON error responses and accepts `VITE_API_BASE_URL` for local environment flexibility.
- [ ] Frontend unit/component tests executed locally.
- [ ] Frontend build executed locally.
- [x] Browser screenshot evidence gap captured as an explicit blocker in `visual-evidence.md`.
- [x] Branch conflict guard passed for the exact frontend paths owned by this task.

## Validation snapshot

- `node --version` -> `command not found`
- `npm --version` -> `11.6.0`
- `python3 .ai/scripts/branch_conflict_guard.py guard --mode preflight --base dev/crud-pipeline-smoke --path frontend/src/App.jsx --path frontend/src/api.js --path frontend/src/App.test.jsx --path frontend/e2e/notes-crud.spec.js --path frontend/package.json --path docs/agentic-evidence/spec-a25b601c60-tasks-trd-p0-f1-t1-crud-pipeline-smoke/p0-f1-t3-ui --path .agent/stories/spec-a25b601c60-tasks-trd-p0-f1-t1-crud-pipeline-smoke/p0-f1-t3-ui --task-id p0-f1-t3-ui --story-id STORY-crud-pipeline-smoke` -> PASS

## Notes

The unchecked items are blocked by the missing `node` runtime, not by the application code itself. No screenshots or annotations can be produced until Node.js is available. Static inspection shows the UI remains keyboard usable and includes the required/optional guidance requested by the accessibility review.
