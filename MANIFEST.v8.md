# Agentic Delivery OS v8 — audited and fixed

v8 is the corrected audit release of the automated agentic SDLC package.

## Main corrections

- Rewrote `detect_new_specs.py` to remove runtime NameErrors and duplicated CLI definitions.
- Templates/examples are ignored by branch-spec automation.
- Copied specs with unresolved placeholders are blocked.
- `scan` displays validation failures instead of showing incomplete specs as ready.
- `agentic_sdlc.py` uses front-matter-aware title extraction.
- Fallback task routing avoids over-detecting cloud/database work from generic template examples.
- Local/offline scans work without `origin`.
- Real runs fail when Codex is missing; dry-runs remain safe.
- PR guardrails enforce one-responsibility PRs, real tests, QA/PM evidence, and no evidence-only PRs.
- AWS guardrails require Terraform-backed infrastructure and block raw mutating AWS CLI commands.

See `AUDIT_AND_FIX_REPORT.v8.md` for details and validation evidence.
