# Visual QA Workflow

Visual QA is required when a change affects UI, layout, user flows, forms, visual states, design-system components, responsive behavior, accessibility, or product intuitiveness.

## What visual QA must capture

For every UI story, capture evidence for relevant states:

- Default empty state
- Valid input state
- Invalid input state
- Loading state
- Error state
- Success state
- Disabled state
- Mobile viewport
- Tablet viewport when applicable
- Desktop viewport
- Dark mode if supported
- High-contrast or accessibility mode if supported

## Screenshot and annotation policy

Screenshots should be stored under:

```text
.agent/stories/<story-id>/screenshots/
```

Annotations should be stored under:

```text
.agent/stories/<story-id>/annotations/
```

A QA agent should annotate issues with:

- bounding box
- severity
- related checklist item
- expected behavior
- actual behavior
- recommended owner agent

Example issue:

```json
{
  "id": "VQA-001",
  "severity": "medium",
  "viewport": "mobile-390x844",
  "selector": "input[name=email]",
  "box": {"x": 22, "y": 124, "width": 320, "height": 42},
  "actual": "Placeholder overlaps the form container border.",
  "expected": "Placeholder stays inside the input and never overlaps the container.",
  "recommended_owner_agent": "frontend-engineer"
}
```

## Automation options

Agents may use any repo-approved visual mechanism:

- Playwright screenshots
- Cypress screenshots
- Storybook visual tests
- Percy, Chromatic, Loki, or similar if already installed
- Framework-native component screenshots
- Manual screenshots in cloud/browser preview when automation is not available

If screenshot automation is not available, the Visual QA Agent must create the test plan and mark the visual evidence gap explicitly.

## Pass criteria

A visual QA pass requires:

- Screenshot evidence exists or gap is justified.
- All checklist items are pass/fail/not-applicable.
- Every failed item has an owner agent and feedback record.
- Fixes are verified with a second review.
- Final evidence is attached to PR notification.
