# Layered Test Matrix

## Frontend test strategy

1. React component tests validate the CRUD form, list rendering, edit flow, delete flow, and status messaging.
2. Accessibility review checks visible labels, required/optional guidance, keyboard-reachable controls, and live regions.
3. Browser/E2E validation against the real API is required for the frontend layer gate when Node.js is available.
4. Visual evidence is required once a browser can launch; until then, the environment blocker must be recorded instead of pretending the check passed.

| Acceptance / requirement | Validation | Status | Evidence |
|---|---|---|---|
| FR-003 / AC-003 | React CRUD page uses the API adapter and renders create/edit/delete states. | implemented | `frontend/src/App.jsx`, `frontend/src/api.js` |
| FR-003 / AC-003 | Required/optional guidance is visible and programmatically associated with the form fields. | implemented | `frontend/src/App.jsx`, `frontend/src/styles.css` |
| FR-004 / AC-004 | Component tests cover create, edit, and delete flows. | blocked | Node.js unavailable in this runtime, so the React test runner cannot start |
| FR-004 / AC-004 | Visual/browser validation and screenshots. | blocked | Node.js unavailable in this runtime, so no browser or screenshot tooling can start |
| FR-003 / AC-003 | API adapter accepts `VITE_API_BASE_URL` and preserves non-JSON error text for local environment flexibility. | implemented | `frontend/src/api.js` |
| Accessibility / usability | Static review confirmed native labels, keyboard-reachable controls, logical sectioning, and live feedback regions. | satisfied | Code review of `frontend/src/App.jsx` and `frontend/src/styles.css` |
| QA/PM readiness | QA and PM can only advance after the Node-backed frontend test and browser steps run in a Node-capable environment. | blocked | `test-evidence.md`, `qa-checklist.md`, `pm-checklist.md` |
| NFR-REL-001 | Record exact blockers instead of a false pass. | satisfied | `test-evidence.md`, `qa-checklist.md`, `pm-checklist.md` |
