# Skill: Spec Reading

## Purpose

Convert specs into executable engineering understanding.

## Procedure

1. Identify the source documents and their priority order.
   - For spec packages, use `PRD -> Implementation Plan -> TRD -> Task List`.
   - Prefer the most granular ready execution document, but read upstream documents for authority and conflict checks.
2. Extract:
   - Business goal.
   - User/stakeholder affected.
   - Current behavior.
   - Desired behavior.
   - Acceptance criteria.
   - Non-goals.
   - Constraints.
   - Data/contracts involved.
   - Risks.
   - Dependencies.
3. Rewrite each acceptance criterion into a measurable statement.
4. Assign IDs: `AC-001`, `AC-002`, etc.
5. Detect ambiguity using the ambiguity taxonomy.
6. Record assumptions separately from facts.
7. Map every acceptance criterion to a validation method.
8. Record package document paths when present:
   - PRD:
   - Implementation plan:
   - TRD:
   - Task list:

## Evidence format

```md
## Spec comprehension
Document type:
Source documents:
Business goal:
Technical goal:
Users/stakeholders:
Current behavior:
Desired behavior:
Non-goals:
Constraints:

## Acceptance criteria
- AC-001:
- AC-002:

## Assumptions
- A-001:

## Ambiguities
- Q-001:
  Type:
  Blocking: yes/no
  Safe assumption:
  Safe progress:

## Test mapping
| AC | Test level | Test name/command | Status |
```

## Quality bar

The implementing agent should be able to code from the output without rereading the original task, while still having links back to source specs.
