# Self-Improvement Proposal: PRD/TRD/Task Spec Package Structure

## Summary

Port the spec authoring workflow used in `cobalto-agile` and `real-estate-v2` into this agentic repo so specs are no longer vague single documents.

## Feedback source

Manager request on 2026-05-19: specs in this repo are too vague and should use the same structure as the reference repos, including PRDs, TRDs, task lists, and implementation plans.

## Proposed change

- Add PRD, implementation-plan, TRD, task-list, and package templates under `specs/`.
- Add repo skills for creating PRDs, implementation plans, TRDs, and task lists.
- Teach spec readers, validators, dispatchers, and prompts to classify PRD/TRD/task-list package documents.
- Keep legacy single-file agentic specs supported for small changes.

## Risk

Risk is medium because this changes agent workflow behavior and validation heuristics. It does not weaken review, QA, PM, Codex review, SQL, Terraform, branch conflict, or deployment controls.

## Rollback

Revert the new templates/skills and restore `spec_templates.markdown_template` to `specs/_TEMPLATE.agentic-spec.md`. Legacy single-file spec support remains unchanged, so rollback is a clean revert.
