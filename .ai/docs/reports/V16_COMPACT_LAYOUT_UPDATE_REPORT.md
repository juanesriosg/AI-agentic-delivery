# V16 Compact Layout Update Report

## Summary

This version removes root-level documentation noise while preserving all agent control files.

## Root after install

```text
AGENTS.md
.ai/
.codex/
.github/
specs/
```

## Changes

- Moved root framework guides to `.ai/docs/reference/`.
- Moved package manifests to `.ai/docs/manifests/`.
- Moved audit/update/validation reports to `.ai/docs/reports/`.
- Moved package README and START_HERE to `.ai/docs/`.
- Removed root `.gitignore` from the overlay to avoid overwriting application `.gitignore`.
- Added `.ai/docs/install/agentic.gitignore.snippet` for runtime artifact ignores.
- Updated agent prompts, config, workflow paths, and guardrails to use the compact documentation paths.

## Rationale

Application repositories should not receive dozens of top-level Markdown files. The active control plane remains available to Codex and GitHub, while optional/historical documentation is hidden under `.ai/docs`.

- Removed initial root `docs/` directory from the install overlay. Optional docs can be scaffolded with `.ai/scripts/init_agentic_repo_docs.py`.
