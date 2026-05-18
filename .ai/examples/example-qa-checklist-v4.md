# QA Checklist — STORY-register-form

| ID | Category | Check | Expected | Status | Evidence | Owner if failed |
|---|---|---|---|---|---|---|
| QA-FUNC-001 | functionality | Submit valid form | Account request is sent and success state appears | pass | test output | |
| QA-FUNC-002 | validation | Invalid email | Helpful error appears | pass | component test | |
| QA-VIS-001 | style_visual | Placeholder layout | Placeholder does not overlap container | fail | mobile-annotated.png | frontend-engineer |
| QA-A11Y-001 | accessibility | Labels | Inputs have visible labels/access names | pass | accessibility review | |
| QA-RESP-001 | responsive | Mobile layout | Form usable at 390x844 | fail | mobile-annotated.png | frontend-engineer |

QA decision: Fail until FB-001 is fixed and verified.
