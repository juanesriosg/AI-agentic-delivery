# Example Clarification with Continuous Progress

Clarification needed:

- ID: Q-001
- Related AC: AC-003
- Question: Should archived users be excluded from the export, or should the CSV include both active and archived users with a status column?
- Why it matters: It changes the query filter and QA expected results.
- Options:
  1. Exclude archived users.
  2. Include archived users.
- Recommended option: Exclude archived users because the feature says active users.
- Blocking: Partially. It blocks final query behavior only.
- Safe assumption if unanswered: Exclude archived users.
- Safe progress I will continue:
  - Create CSV formatter unit tests.
  - Add endpoint permission tests.
  - Build export service with filter parameter but keep default active-only.
  - Prepare QA handoff note documenting the assumption.
