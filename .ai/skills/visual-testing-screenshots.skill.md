# Skill: Visual Testing with Screenshots

Use this skill for UI stories.

## Steps

1. Identify relevant screens, states, and viewports.
2. Prefer existing tools: Playwright, Cypress, Storybook, Chromatic, Percy, Loki, or framework-specific screenshot tooling.
3. Capture screenshots under `.agent/stories/<story-id>/screenshots/`.
4. Create a visual evidence report.
5. Annotate failures with `.ai/scripts/annotate_screenshot.py` when possible.
6. Route visual feedback to Frontend, UI Designer, Design System, or Accessibility agents.
7. Capture after-fix evidence before visual QA pass.

## Minimum for forms

- Empty
- Focused
- Invalid
- Valid
- Loading/submitting
- Success
- Error
- Mobile and desktop
