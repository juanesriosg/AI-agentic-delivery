# v15 self-improvement validation report

Validated package: `agentic-delivery-os-v15-self-improving-agents`

## Checks run

```text
python -m py_compile .ai/scripts/*.py
bash -n .ai/scripts/*.sh .codex/*.sh
python -m json.tool .ai/automation/agentic.config.json
python -m json.tool .ai/evals/skill-improvement/eval-cases.json
PyYAML parse for .github/workflows/*.yml, .ai/specs/*.yml, .github/ISSUE_TEMPLATE/*.yml
python .ai/scripts/skill_eval_runner.py --all
python .ai/scripts/harvest_github_feedback.py --limit 1
feedback capture simulation
self-improvement dry-run simulation
skill guardrail safe PR simulation
skill guardrail unsafe policy weakening simulation
package cleanup check for .agent, .git, __pycache__, and .pyc artifacts
```

## Results

```text
Python compile: PASS
Bash syntax: PASS
JSON parse: PASS
YAML parse: PASS
Skill eval runner: PASS
GitHub feedback harvester without gh auth: PASS as non-strict graceful skip
Feedback capture simulation: PASS
Self-improvement dry run: PASS
Safe skill guardrail simulation: PASS
Unsafe skill guardrail simulation: FAIL as expected
Package cleanup: PASS
```

## Important limitation

The package was not connected to a real GitHub repository, real Codex CLI execution, or real project PR history in this validation. The GitHub feedback harvester is best-effort and requires authenticated `gh` in a real repo.
