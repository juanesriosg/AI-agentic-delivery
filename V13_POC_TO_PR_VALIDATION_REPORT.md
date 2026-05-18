# V13 POC-to-PR Validation Report

## Fixes applied after review

- Fixed GitHub Actions argument passing for optional `--spec` and `--dry-run` values by replacing shell string concatenation with a Bash array.
- Updated the completed example spec so it passes the design-first gate.
- Made `design_gate.py` more robust by recognizing `data requirements`, `database contract`, `layer sequencing`, `programming paradigm`, and `design pattern decision` headings.
- Confirmed the POC-to-PR dry-run can detect a ready spec, validate it, run the design gate, create task prompts, and simulate source-branch integration.

## Validated commands

```bash
python -m py_compile .ai/scripts/*.py
bash -n .ai/scripts/*.sh
bash -n .codex/*.sh
python .ai/scripts/validate_agentic_spec.py specs/register-form.spec.md
python .ai/scripts/design_gate.py --spec specs/register-form.spec.md --allow-not-applicable
python .ai/scripts/poc_to_pr.py --allow-cloud --branch dev/register-form --mode cloud --spec specs/register-form.spec.md --dry-run
```

## Expected final workflow

```text
POC from boss
  -> repo created and indexed
  -> GPT Pro writes spec
  -> GPT Pro pushes ready spec to dev/<feature>
  -> GitHub workflow detects spec
  -> Codex agents implement and test
  -> agents push implementation commits to the same spec branch
  -> final PR opens from dev/<feature> to main and tags the manager
```

## v13.2 prompt/scaffold validation

Additional fixes validated after aligning the workflow with the expected GPT Pro spec-push flow:

```text
- GPT Pro prompt now includes required spec front matter and required section IDs.
- GPT Pro branch contract now treats `source_branch` as the implementation branch and `target_branch` / `final_pr_base` as the final PR base.
- `create_spec_branch.py` compiles and now fills validator-friendly fields: spec_id, story_id, source_branch, target_branch, priority, risk_level, manager, and PR strategy.
```

Re-ran:

```bash
python -m py_compile .ai/scripts/*.py
bash -n .ai/scripts/*.sh .codex/*.sh
python .ai/scripts/poc_to_pr.py --allow-cloud --branch dev/register-form --mode cloud --spec specs/register-form.spec.md --dry-run
```
