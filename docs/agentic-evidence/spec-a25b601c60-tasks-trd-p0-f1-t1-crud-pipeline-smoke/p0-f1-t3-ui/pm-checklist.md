# PM Checklist

- [x] Change stays inside the smoke-app UI responsibility.
- [x] No auth, billing, cloud, deployment, or production-data behavior was added.
- [x] User-facing copy uses plain CRUD labels: Title, Body, Save, Edit, Delete, New note.
- [x] The app surfaces loading, empty, success, and error states.
- [x] The form now also exposes explicit required/optional guidance for the note fields.
- [x] A concrete environment blocker is recorded instead of a false pass for browser validation.
- [x] The runtime was rechecked and still lacks `node`, so frontend QA remains blocked rather than mislabeled as passed.
- [x] The frontend API adapter now supports `VITE_API_BASE_URL` and safer error parsing without broadening the feature scope.
- [x] Visual QA evidence gap captured explicitly in `visual-evidence.md`.
- [ ] Real frontend test run completed.
- [x] Branch conflict guard passed for the exact frontend files and evidence paths in scope.

## Product Acceptance Decision

Blocked, not accepted yet.

The UI design and copy are product-appropriate for a smoke CRUD page, but the story cannot be product-approved until the frontend can run in a Node-capable environment and produce actual test and browser evidence. The current implementation is acceptable in static review, but the acceptance gate requires runtime validation.

## Notes

The missing Node.js runtime prevents final UI execution, screenshot capture, and visual validation in this environment. Static review suggests the current copy and layout are usable without mouse-only interactions, but the task cannot be promoted to a frontend pass until a Node-capable runtime runs the React tests and browser checks.
