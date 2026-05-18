# Skill: feedback-capture

## Purpose
Capture reviewable feedback signals from agent work without creating extra manual process.

## Operating context
Feedback appears in PR comments, issues, QA/PM checklists, Codex review output, CI logs, agents.log, and manager notes. Capture only signals that can teach future behavior.

## Principles
- Feedback must include correction plus rationale when possible.
- Preserve contradictions instead of hiding them.
- Do not create a durable rule from one noisy data point.
- Do not store secrets, raw PII, or sensitive customer data.

## Good feedback structure
- What happened?
- Why was it wrong, noisy, risky, or useful?
- What should future agents do differently?
- Which skill, agent, or gate should learn from it?
- Is this accepted, rejected, or unresolved?

## Procedure
1. Read review comments, QA findings, PM findings, Codex review, failed gates, and agents.log.
2. Ignore vague feedback without rationale unless it is repeated.
3. Normalize the feedback into one event.
4. Use `.ai/scripts/capture_agent_feedback.py`.
5. Link evidence paths or PR URLs when possible.

## Classification
Use one of:

- `accepted_correction`
- `rejected_agent_output`
- `ci_failure`
- `qa_failure`
- `pm_failure`
- `codex_review_failure`
- `manager_comment`
- `security_finding`
- `architecture_finding`
- `spec_gap`
- `test_gap`
- `process_gap`

## Quality bar
Do not create low-signal noise. A useful event teaches future behavior.

## Uncertainty behavior
If the target skill or agent is unclear, record `unknown`, keep the evidence, and let the Skill Improver Agent cluster it later. If feedback conflicts, record both sides and flag the conflict.

## Feedback hooks
Write events to `.agent/feedback/feedback.jsonl` and promote durable records to `docs/agentic-feedback/**` when they should be reviewed.
