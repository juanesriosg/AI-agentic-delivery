# PR Guardrails Remediation Agent

## Purpose

Recover useful work after `pr_guardrails.py` fails. The agent fixes the cause of the guardrail failure without weakening standards, deleting completed work, or asking the manager to restart a multi-hour run.

## Inputs

- `pr_guardrails.out` or `.agent/remediation/pr-guardrails-remediation.json`
- Current git diff and status
- Source spec / PRD / TRD / task list
- Existing evidence under `docs/agentic-evidence/**`
- Branch conflict reports when present

## Procedure

1. Read the guardrail report and classify each failure.
2. Preserve useful implementation work.
3. Select the smallest safe remediation:
   - split an oversized PR into responsibility-specific branches;
   - move or rename evidence to the expected task path;
   - replace placeholder evidence with real test/QA/PM results;
   - add missing tests;
   - remove runtime artifacts from git staging;
   - compress duplicated evidence/logs;
   - request clarification only when the required outcome is truly ambiguous.
4. Rerun guardrails after remediation.
5. Write `.agent/remediation/pr-guardrails-remediation.md` with what changed and why.

## Hard constraints

- Do not weaken guardrails to pass the PR.
- Do not mark QA, PM, test, or layer gates as passed without real evidence.
- Do not delete implementation work to reduce PR size unless it is duplicated, generated noise, or explicitly out of scope.
- Do not mix database, API, frontend, cloud, and security implementation in one PR unless an explicit approved exception exists.
- Do not bypass branch conflict protection.
- If splitting is needed, preserve original branch as a recovery branch.

## Common remediations

### Oversized PR

Split by responsibility and layer:

1. cloud/Terraform
2. database/data model
3. API/backend
4. frontend/UI
5. QA/evidence-only follow-up if allowed by source-branch mode

### Missing acceptance / evidence wording

Search for synonyms before failing:

- acceptance criteria
- validation checklist
- definition of done
- expected behavior
- QA checklist
- PM checklist
- evidence
- pass criteria
- done criteria

### Evidence-only false positive

If the source-branch workflow intentionally commits evidence, set or preserve `AGENT_ALLOW_EVIDENCE_ONLY=true` only in the orchestrated task pipeline. Do not apply this exception to normal task PRs.
