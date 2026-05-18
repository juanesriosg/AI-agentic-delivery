# MANIFEST v6 — Generic Agentic Spec Templates

v6 adds reusable templates for specs created with ChatGPT Pro and pushed to watched branches.

## New files

```text
specs/_TEMPLATE.agentic-spec.md
specs/_TEMPLATE.agentic-spec.yml
.ai/specs/generic-agentic-spec-template.md
.ai/specs/spec-template.schema.yml
.ai/examples/example-completed-generic-spec.md
.ai/scripts/validate_agentic_spec.py
.github/workflows/agentic-spec-template-validation.yml
SPEC_TEMPLATE_GUIDE.md
```

## Purpose

The template is designed so agents can read specs deeply, split work into one-responsibility PRs, route work to specialist agents, test thoroughly, and prepare concise PRs with evidence.

## Required concepts

Every implementation spec should clearly define:

```text
Description
Business need
User needs
Functional requirements
Non-functional requirements
Scope / out of scope
Files to touch
Files not to touch without approval
Architecture expectations
AWS/Terraform expectations when cloud is involved
Testing expectations
Acceptance criteria
Agent routing hints
PR decomposition plan
Risks, assumptions, clarifications
Definition of done
Notification requirements
```

## Automation fit

The spec template is compatible with:

```text
.ai/scripts/agentic_sdlc.py
.github/workflows/agentic-spec-autostart.yml
.github/workflows/agentic-spec-template-validation.yml
Codex Cloud handoff prompts
local daytime loop
night cloud loop
```
