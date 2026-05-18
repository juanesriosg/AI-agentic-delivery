# v14 Local-first Codex runtime policy

This package is configured so Codex runs the agentic SDLC in **local mode by default**.

## Default runtime

```bash
python .ai/scripts/agentic_sdlc.py watch --mode local --poll-seconds 180
python .ai/scripts/agentic_sdlc.py run-once --mode local --max-specs 1
python .ai/scripts/poc_to_pr.py --mode local
```

Local mode means the agents operate against the checked-out repository/worktree and should assume they can run local bootstraps, tests, QA checks, screenshots, and app-specific validation when the environment supports it.

## Default Codex model

The agentic SDLC now passes these options to `codex exec`:

```bash
--model gpt-5.5 \
-c model_reasoning_effort=xhigh \
-c model_reasoning_summary=concise \
-c model_verbosity=high
```

The repository config also contains:

```json
"codex": {
  "model": "gpt-5.5",
  "reasoning_effort": "xhigh",
  "model_reasoning_effort": "xhigh",
  "reasoning_summary": "concise",
  "verbosity": "high"
}
```

## Cloud mode is blocked unless explicit

Cloud mode is no longer a default for push events, scheduled jobs, or POC-to-PR automation.

Cloud mode requires one of these explicit actions:

```bash
AGENTIC_EXPLICIT_CLOUD=true python .ai/scripts/agentic_sdlc.py --allow-cloud run-once --mode cloud --max-specs 1
```

or:

```bash
python .ai/scripts/agentic_sdlc.py --allow-cloud run-once --mode cloud --max-specs 1
```

or manual GitHub Actions dispatch with:

```text
mode = cloud
allow_cloud = true
```

For the explicit cloud continuation workflow, the operator must type:

```text
I_APPROVE_CLOUD_RUN
```

## GitHub workflows

### POC spec to PR

`.github/workflows/agentic-poc-spec-to-pr.yml` still reacts to spec-branch pushes, but its mode default is now:

```yaml
mode: local
```

It will fail if someone chooses `mode=cloud` without the explicit cloud opt-in.

### Night cloud continuation

`.github/workflows/agentic-night-cloud.yml` is manual-only. The schedule was removed.

The goal is to prevent accidental cloud execution when you expected local behavior.

## PR review

The Codex PR review gate now also uses:

```yaml
model: gpt-5.5
effort: xhigh
```

## Local-first rule for agents

Agents must not say something was tested locally unless they actually ran the local test in the current worktree/environment. If a local-only test cannot run, the agent must mark it as a local-test gap and continue only with safe, truthful validation.
