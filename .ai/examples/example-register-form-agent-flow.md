# Example Agent Flow — Register Form

```text
Spec Agent
  Reads STORY-register-form and creates acceptance criteria map.

Agile Orchestrator
  Routes to UX Researcher, UI Designer, Frontend Engineer, Backend Engineer, QA Checklist, Visual QA, Accessibility QA, PM Acceptance.

Frontend Engineer
  Implements the form, validation states, submit behavior, component tests, and logs iteration.

Backend Engineer
  Confirms/registers endpoint contract or mocks it if out of scope.

QA Checklist Agent
  Creates functionality/style/accessibility/integration checklist.

Visual QA Agent
  Captures mobile screenshot and finds: placeholder overlaps form container.
  Creates FB-001 for Frontend Engineer with annotation.

Frontend Engineer
  Fixes input padding/floating label behavior and reruns component tests.

QA Regression Agent
  Rechecks visual defect, closes FB-001.

PM Acceptance Agent
  Finds the form is not intuitive because password requirements are hidden.
  Creates FB-002 for UX/UI + Frontend: show password guidance before error.

UX/UI + Frontend
  Adds helper text pattern consistent with existing app.

QA Regression Agent
  Reruns form checklist and passes.

PM Acceptance Agent
  Rechecks PM checklist and passes.

Release Train Engineer
  Prepares qa-user/prod-ready recommendation and PR notification.

Human AI PM
  Reviews the PR with screenshots, code summary, tests, QA/PM checklists, feedback loop, and agents.log.
```
