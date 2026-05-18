# Agentic Delivery OS — Compact Layout

This package is intentionally compact at the repository root.

## Files expected at repo root

```text
AGENTS.md
.ai/
.codex/
.github/
specs/
```

There are no root-level framework manuals, version reports, or manifests. They were moved under `.ai/docs/` so they do not pollute application repositories.

## Where documentation lives

```text
.ai/docs/README.md             Main package README
.ai/docs/START_HERE.md         Quick start guide
.ai/docs/reference/            Operational reference guides
.ai/docs/reports/              Audit/update/validation reports
.ai/docs/manifests/            Historical package manifests
.ai/docs/install/              Install snippets and repo setup helpers
```

## Recommended install

From the repository root, copy or unzip only the package contents. Then append the runtime ignore snippet to your real `.gitignore`:

```bash
cat .ai/docs/install/agentic.gitignore.snippet >> .gitignore
```

Do not overwrite an existing project `.gitignore` or `README.md` unless you intentionally want to.

## Why this layout

The package keeps the active control plane in hidden folders while leaving the application repository clean. Codex still reads `AGENTS.md`, GitHub still reads `.github/workflows/**`, agents still use `.ai/**`, and specs still live in `specs/**`.


## Optional repo docs

The installable overlay does not create a root `docs/` directory. Agents create `docs/agentic-evidence/**`, `docs/agentic-feedback/**`, or `docs/business-rules/**` only when work requires reviewable evidence or business rules. To scaffold those folders manually, run:

```bash
python .ai/scripts/init_agentic_repo_docs.py
```
