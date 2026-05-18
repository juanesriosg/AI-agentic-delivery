# POC Repository Onboarding v13

This is the minimal operating path for a new POC.

## 1. Create the repository

```bash
gh repo create <owner>/<repo> --private --clone
cd <repo>
```

Copy this package into the repository root:

```text
AGENTS.md
.ai/
.codex/
.github/
specs/
docs/
```

Commit the package:

```bash
git add AGENTS.md .ai .codex .github specs docs
 git commit -m "chore: install agentic SDLC"
git push -u origin main
```

## 2. Index / load repo context into GPT Pro

Give GPT Pro the repo context, the POC, and the prompt:

```text
.ai/prompts/gpt-pro-poc-to-spec.prompt.md
```

Ask GPT Pro to create a complete spec, not code.

## 3. Push a ready spec branch

```bash
git switch -c dev/<feature-slug>
mkdir -p specs
$EDITOR specs/<feature-slug>.spec.md
python .ai/scripts/validate_agentic_spec.py specs/<feature-slug>.spec.md
git add specs/<feature-slug>.spec.md
git commit -m "spec: <feature>"
git push -u origin dev/<feature-slug>
```

## 4. Let Codex run

The workflow starts automatically:

```text
.github/workflows/agentic-poc-spec-to-pr.yml
```

It runs the POC-to-PR command:

```bash
python .ai/scripts/poc_to_pr.py --allow-cloud --branch dev/<feature-slug> --mode cloud
```

## 5. Review the final PR

The final PR is opened from:

```text
dev/<feature-slug> → main
```

The PR tags:

```text
@juanesriosg
```

Do not approve until these pass:

```text
- design gate
- DB/API/frontend layer gates as applicable
- QA agent
- PM agent
- Dev Manager agent
- branch conflict guard
- PR guardrails
- Codex AI review
```

## 6. AWS rule

Any new AWS component must be versioned as code, preferably Terraform, and deployed by GitHub workflow. Do not allow manual console setup as the final source of truth.
