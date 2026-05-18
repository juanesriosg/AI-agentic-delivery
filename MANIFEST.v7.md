# Agentic Delivery OS v7

v7 is an audited/fixed release of the repo-level agentic SDLC ecosystem.

## Main corrections

- Template and example specs are ignored by automation.
- Spec validator blocks templates and incomplete specs.
- Local/offline branch scanning works without `origin`.
- Real Codex failures return non-zero instead of silently succeeding.
- PR creation requires meaningful non-evidence changes.
- PR guardrails inspect committed, staged, unstaged, and untracked files.
- Placeholder QA/PM/test evidence is blocked.
- AWS changes require Terraform-backed evidence and GitHub workflow validation.
- Legacy duplicate workflows are manual-only.
- GitHub secret condition usage was corrected.

See `AUDIT_REPORT_V7.md` for detailed findings and validation.
