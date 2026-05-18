# Skill: Branch Spec Ingestion

## Purpose

Enable autonomous agents to start work when a manager pushes a ChatGPT-generated spec to a development branch.

## When to use

Use this skill whenever a new or modified spec file is detected in a watched branch/path.

## Procedure

1. Identify the source branch and commit SHA.
2. Identify the changed spec file.
3. Read the whole spec, not only headings.
4. Extract:
   - business goal,
   - user/stakeholder problem,
   - technical goal,
   - acceptance criteria,
   - non-goals,
   - constraints,
   - risks,
   - dependencies,
   - owners,
   - test expectations,
   - release/deployment expectations.
5. Create a spec comprehension summary.
6. Run:

```bash
.ai/scripts/spec-quality-check.py --spec <spec-file> --format markdown
.ai/scripts/generate-test-matrix.py --spec <spec-file>
```

7. Classify missing information:
   - blocking: cannot implement safely,
   - non-blocking: safe progress is possible,
   - manager decision: business/product tradeoff,
   - repo owner decision: ownership/risk boundary.
8. Ask focused clarification questions only for decisions that affect behavior, risk, architecture, data, public contracts, ownership, or validation.
9. Continue safe progress while waiting.
10. Dispatch or execute implementation using the branch model:

```text
checkout source spec branch
create implementation branch from source spec branch
open PR back to source spec branch
```

## Safe progress while waiting

Allowed:

- repo discovery,
- dependency discovery,
- test discovery,
- existing behavior characterization,
- fixtures,
- test harness setup,
- component mapping,
- low-risk tests for unambiguous behavior,
- non-invasive bug reproduction,
- draft implementation plan,
- mock or local-only experiments not committed.

Not allowed:

- public API guesses,
- auth/security/billing changes,
- migrations,
- infrastructure changes,
- production config changes,
- destructive operations,
- broad refactors,
- deployment,
- marking QA-ready.

## Completion

The branch spec ingestion work is complete when at least one of these is true:

- an implementation task was created and dispatched,
- a clarification request was created and safe-progress work was dispatched,
- the spec was rejected as not implementable with clear reasons,
- a repo owner/manager approval gate was raised for high-risk work.
