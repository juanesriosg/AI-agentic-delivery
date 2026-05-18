# Manifest v4 — Agile Agent Ecosystem

## New top-level docs

- `.ai/docs/reference/AGENTIC_SDLC_V4.md`
- `.ai/docs/reference/AGILE_AGENT_ECOSYSTEM.md`
- `.ai/docs/reference/VISUAL_QA_WORKFLOW.md`
- `.ai/docs/reference/AGENT_FEEDBACK_LOOP.md`

## New agent types

- Agile Delivery Orchestrator
- Product Requirements Agent
- Product Manager Acceptance Agent
- UX Researcher Agent
- UI Designer Agent
- Design System Agent
- Frontend Engineer Agent
- Backend Engineer Agent
- API Contract Engineer Agent
- Database Engineer Agent
- Cloud Platform Engineer Agent
- DevOps CI/CD Engineer Agent
- QA Checklist Engineer Agent
- Visual QA Engineer Agent
- Accessibility QA Engineer Agent
- E2E QA Engineer Agent
- QA Regression Engineer Agent
- Integration Engineer Agent
- SRE Reliability Engineer Agent
- Release Train Engineer Agent
- Agent Scribe Logger Agent
- Agent Feedback Coordinator Agent
- Mobile QA Engineer Agent

## New automation

- `agent-agile-story-orchestration.yml`
- `agent-stage-gates.yml`
- `agent-visual-qa.yml`
- `agent-feedback-log.yml`
- `agent-promotion-gates.yml`

## New scripts

- `agent_log.py`
- `agent_feedback.py`
- `story_state.py`
- `create_qa_checklist.py`
- `create_pm_checklist.py`
- `validate_stage_gate.py`
- `annotate_screenshot.py`
- `visual_qa_report.py`
- `generate_pr_notification.py`
- `run_visual_qa.sh`

## New gates

- QA approval required for every task.
- QA + PM Agent approval required for every user story.
- Visual QA required for UI changes.
- Accessibility review required for user-facing UI.
- Cloud work uses Well-Architected review.
- Production merge/deploy is not automatic by default.
