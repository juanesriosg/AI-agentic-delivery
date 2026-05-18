# Agent Feedback Loop

Agents must work like a real agile team. A story can cycle through multiple review/fix iterations before reaching the human AI PM.

## Feedback format

Every feedback item must include:

```yaml
feedback_id: FB-001
story_id: STORY-123
from_agent: qa-agent
recommended_owner_agent: frontend-engineer
severity: medium
stage: qa-review
blocking: true
summary: Placeholder overlaps form container
evidence:
  - .agent/stories/STORY-123/screenshots/register-mobile.png
  - .agent/stories/STORY-123/annotations/VQA-001.json
expected: Placeholder remains inside input field
actual: Placeholder overlaps container border
suggested_fix: Adjust input padding and floating-label state
verification_required: Visual QA at mobile and desktop viewports
```

## Routing

The Agent Feedback Coordinator routes feedback by issue type:

- Requirements ambiguity -> Product Requirements Agent
- UX/intuitiveness -> UX Researcher or PM Acceptance Agent
- Visual/layout/style -> UI Designer, Design System, Frontend Engineer
- Accessibility -> Accessibility QA + Frontend Engineer
- API behavior -> API Contract Engineer + Backend Engineer
- Data persistence -> Database Engineer + Backend Engineer
- Cloud/deploy -> Cloud Platform or DevOps CI/CD Engineer
- Test flakiness -> QA Regression or Test Engineer
- Security -> Security Engineer
- Performance -> Performance Engineer
- Reliability -> SRE Reliability Engineer

## Closure rule

Feedback is closed only when:

- Owner agent acknowledges it in `agents.log`.
- Fix or decision is documented.
- Relevant tests/evidence are updated.
- Reviewing agent verifies the fix.
- PM Agent verifies product-impacting changes when applicable.

## Do not hide feedback

Agents must not rewrite history or remove failed evidence. Failed iterations are valuable because they show review depth and help the human manager trust the process.
