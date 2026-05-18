# Optional Codex Cloud Hooks

These files are thin wrappers around the portable `.ai/scripts/` commands.

Use them when a cloud coding platform allows setup and validation commands.

Setup:

```bash
.codex/bootstrap.sh
```

Validation:

```bash
.codex/run-quality-gate.sh
```

The real policy lives in `AGENTS.md`, `.ai/runtime/`, `.ai/specs/`, and `.ai/scripts/`.


## Local-first Codex policy

Default agentic SDLC execution uses Codex CLI local mode with:

```toml
model = "gpt-5.5"
model_reasoning_effort = "xhigh"
```

The manager's target profile is "GPT-5.5 extra high". The current documented Codex config uses `model_reasoning_effort = "xhigh"`, so the package maps the requested profile to the highest documented value and keeps the intent in `.ai/automation/agentic.config.json`.

Cloud execution is blocked unless explicitly requested with `--allow-cloud` or `AGENTIC_EXPLICIT_CLOUD=true`.
