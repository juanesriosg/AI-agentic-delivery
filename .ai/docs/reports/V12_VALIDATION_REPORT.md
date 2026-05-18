# v12 Validation Report

Validated on May 15, 2026.

## Checks run

```text
python -m compileall -q .ai/scripts
bash -n for .ai/scripts/*.sh and .codex/*.sh
python -m json.tool .ai/automation/agentic.config.json
PyYAML parsing for .github/workflows/*.yml, .ai/specs/*.yml, and specs/*.yml
.ai/scripts/design_gate.py on the completed layered full-stack example
.ai/scripts/layer_gate.py on synthetic database evidence
.ai/scripts/agentic_sdlc.py --dry-run run-once on a simulated repo with dev/register-form spec branch
```

## Simulation results

- Spec detection found the new branch spec.
- Design gate passed for the completed example spec.
- Planner fallback produced ordered tasks: database, API, frontend.
- Database task was allowed first.
- API task was blocked until database layer pass evidence exists on the source branch.
- Frontend task was blocked until API layer pass evidence exists on the source branch.
- Branch conflict guard received cleaned expected paths, not table prose.

## Package cleanup

```text
No __pycache__ directories
No .pyc files
No .agent runtime artifacts
```

## Environment-dependent items not validated

- Real Codex CLI / Codex Cloud execution.
- Real GitHub PR creation through `gh`.
- Real AWS account / Terraform backend / deployment.
- Project-specific unit, integration, E2E, and browser tests.
