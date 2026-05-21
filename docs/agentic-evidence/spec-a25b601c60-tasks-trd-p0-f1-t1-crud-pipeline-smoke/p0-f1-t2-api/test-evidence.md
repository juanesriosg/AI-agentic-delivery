# Test Evidence

## Validation commands

- `python3 .ai/scripts/spec-quality-check.py --spec specs/crud-pipeline-smoke/tasks/tasks-trd-p0-f1-t1-crud-pipeline-smoke.md --format markdown`
- `python3 .ai/scripts/generate-test-matrix.py --spec specs/crud-pipeline-smoke/tasks/tasks-trd-p0-f1-t1-crud-pipeline-smoke.md`
- `python3 -m unittest discover -s backend/tests -v`
- `python3 -m unittest discover -s tests -v`
- `python3 .ai/scripts/agent-self-review.py --format markdown`
- `python3 .ai/scripts/check-scale-readiness.py --format markdown`
- `python3 .ai/scripts/agent-bug-scan.py --format markdown`
- `python3 .ai/scripts/branch_conflict_guard.py guard --mode preflight --base dev/crud-pipeline-smoke --spec-file specs/crud-pipeline-smoke/tasks/tasks-trd-p0-f1-t1-crud-pipeline-smoke.md --task-id p0-f1-t2-api --story-id SPEC-20260520-crud-pipeline-smoke --path backend/app/main.py --path backend/app/repository.py --path backend/tests/test_notes_api.py --path backend/requirements.txt --path docs/agentic-evidence/SPEC-20260520-crud-pipeline-smoke/p0-f1-t2-api`

## Results

- Spec quality check completed with a score of `75/100` and confirmed the task contains business goal, technical goal, acceptance criteria, tests, assumptions, clarifications, and risks.
- Test matrix generation completed and records the API task as the validation owner for `AC-002`.
- Database layer evidence was already green before API validation, satisfying the required DB -> API ordering.
- Backend validation passed:
  - `python3 -m unittest discover -s backend/tests -v` ran 2 tests and passed.
  - `python3 -m unittest discover -s tests -v` ran 5 tests and passed.
- Self-review and scale readiness passed:
  - `python3 .ai/scripts/agent-self-review.py --format markdown` returned `Quality score: 100/100`.
  - `python3 .ai/scripts/check-scale-readiness.py --format markdown` returned `Verdict: ready_with_notes`.
- The bug scan returned heuristic findings only in unrelated `.ai/scripts/agentic_sdlc.py` and `.ai/scripts/pr_guardrails.py` files, which are outside this API task scope.
- The branch conflict guard blocked implementation edits because another active branch already changes the API task's implementation paths. That means the task is evidence-complete but code-edit blocked in this workspace.

## Coverage summary

- API create/list/read/update/delete round-trip is covered.
- Empty title validation is covered.
- Missing note lookup is covered.
- The task remains local-only and does not introduce cloud validation requirements.

## Residual gaps

- Frontend integration, visual QA, and browser-based E2E evidence are out of scope for this API task and remain blocked on the UI task.
- No API contract defects were found during validation; remaining work is the later UI and QA layers.
