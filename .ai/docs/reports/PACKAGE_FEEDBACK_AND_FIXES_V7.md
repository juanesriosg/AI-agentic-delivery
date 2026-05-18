# Package feedback and fixes — v7

## Executive summary

I audited the package as if it were being installed in a production repository. The overall architecture is strong: it defines specialized agents, branch-spec detection, Codex/local/cloud execution paths, one-responsibility PRs, QA/PM/dev-manager gates, Terraform-first AWS deployment, evidence collection, and manager notification.

The biggest problems were not conceptual; they were automation safety issues. The package needed stronger protection against templates or incomplete specs starting code work, stronger validation before implementation, cleaner dry-run behavior, and better package hygiene.

## Bugs and risks found

### 1. Reusable templates could look implementation-ready

The Markdown and YAML spec templates had `status: ready_for_agents`. Even though template paths were ignored, a copied template renamed to a real spec path could accidentally trigger implementation before it was completed.

**Fix:** reusable templates now use `status: draft`. A copied spec must be completed and changed to `status: ready_for_agents` before automation starts.

### 2. Spec detection checked path/status, but not spec quality

The orchestrator could start work if the branch/path/status matched, even if the spec still contained placeholders or weak acceptance criteria.

**Fix:** `agentic_sdlc.py` now runs `.ai/scripts/validate_agentic_spec.py` before autonomous implementation. If validation fails, coding is skipped and a validation report is written under `.agent/state/spec-validation/`.

### 3. Specs without status could start automatically

The previous default allowed specs without a readiness status to be processed. That is convenient, but risky for this workflow because a partially drafted file under `specs/` could trigger work.

**Fix:** default config now requires an explicit ready status. `process_specs_without_status` is set to `false`.

### 4. Copied placeholders were not blocked by orchestration

The validator could catch placeholders when run manually, but the orchestrator was not enforcing it.

**Fix:** validation is now part of the orchestration gate, not just a standalone helper.

### 5. Dry-run and generated evidence needed tighter hygiene

The package already had good dry-run behavior, but the audit confirmed it should never mark specs as processed or dirty the repo.

**Fix validated:** dry-run produces preview/evidence under ignored `.agent/` state and does not mark specs as processed.

### 6. Runtime artifacts could leak into the package

Running compile checks created `__pycache__` files.

**Fix:** runtime artifacts were removed and `.gitignore` includes `.agent/`, virtual envs, caches, pycache, node modules, build outputs, and coverage artifacts.

### 7. Documentation needed a v7 entrypoint

The package had accumulated v4/v5/v6 docs, but the first README/START_HERE sections did not clearly identify the corrected v7 flow.

**Fix:** README and START_HERE now begin with the v7 corrected workflow and readiness rule.

## Validation performed

- Python scripts compile successfully.
- JSON files parse successfully.
- YAML workflow/spec files parse successfully.
- Shell scripts pass `bash -n`.
- Runtime artifacts are excluded from the final tree.
- Draft copied template is detected but not processed.
- Ready completed spec is detected and dry-run implementation starts.
- Ready spec with unresolved placeholders is blocked by the validation gate.
- Dry-run does not dirty the simulated repository.

## Remaining limits

- I did not run a real Codex Cloud workspace.
- I did not run a real AWS account, Terraform plan, or Terraform apply.
- I did not execute project-specific unit/integration/E2E tests because this is a reusable template package, not installed in a specific application repo.

## Recommended next step per repo

Install the package in one pilot repo first, then run:

```bash
python .ai/scripts/agentic_sdlc.py doctor
python .ai/scripts/agentic_sdlc.py --dry-run scan
python .ai/scripts/validate_agentic_spec.py .ai/examples/example-completed-generic-spec.md
```

After that, create one real `dev/<feature>` branch with a completed `specs/<feature>.agentic-spec.md` and run the local loop in dry-run mode before enabling full Codex execution.
