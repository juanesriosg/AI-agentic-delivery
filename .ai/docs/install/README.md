# Installing the Agentic OS in a repo

This v16 package is designed to be unzipped into the repository root without adding dozens of Markdown files to the root.

## Copy layout

Expected root after install:

```text
AGENTS.md
.ai/
.codex/
.github/
specs/
```

## Git ignore

The package does not ship a root `.gitignore`, because overwriting an existing project `.gitignore` is risky. Append the snippet instead:

```bash
cat .ai/docs/install/agentic.gitignore.snippet >> .gitignore
```

## First checks

```bash
python .ai/scripts/agentic_sdlc.py doctor
python .ai/scripts/agentic_sdlc.py --dry-run scan
```


## Optional docs scaffold

The compact package does not create a root `docs/` folder during install. When you want the evidence/business-rules folders, run:

```bash
python .ai/scripts/init_agentic_repo_docs.py
```
