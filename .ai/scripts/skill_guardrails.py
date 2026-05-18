#!/usr/bin/env python3
"""Guardrails for PRs that change agent skills, specs, prompts, or evals."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple

SENSITIVE_PATTERNS = [
    r"human_review_required\s*[:=]\s*false",
    r"codex_ai_review_required\s*[:=]\s*false",
    r"runtime_agents_may_modify_skills\s*[:=]\s*true",
    r"self_merge_allowed\s*[:=]\s*true",
    r"human_approval_required\s*[:=]\s*false",
    r"codex_ai_review_required\s*[:=]\s*false",
    r"require_codex_ai_review\s*[:=]\s*false",
    r"allow_mutating_sql\s*[:=]\s*true",
    r"production_requires_human_review\s*[:=]\s*false",
    r"block_on_overlap\s*[:=]\s*false",
    r"qa_deploy_requires_qa_pass\s*[:=]\s*false",
    r"staging_requires_pm_and_qa_pass\s*[:=]\s*false",
    r"all_aws_changes_must_use_terraform\s*[:=]\s*false",
]
REQUIRED_ARTIFACTS = [
    "docs/agentic-self-improvement/feedback-bundle.json",
    "docs/agentic-self-improvement/eval-report.md",
    "docs/agentic-self-improvement/changelog.md",
]
CONTROLLED_PREFIXES = (
    ".ai/agents/",
    ".ai/skills/",
    ".ai/specs/",
    ".ai/evals/",
    ".github/codex/prompts/",
    ".ai/docs/",
)


def git(*args: str, check: bool = True) -> str:
    proc = subprocess.run(["git", *args], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=check)
    return proc.stdout


def diff_files(base: str) -> List[str]:
    try:
        return [x for x in git("diff", "--name-only", f"{base}...HEAD").splitlines() if x]
    except Exception:
        return []


def diff_text(base: str) -> str:
    try:
        return git("diff", f"{base}...HEAD", check=True)
    except Exception:
        return ""


def has_manager_override_label() -> bool:
    # Placeholder for GitHub label checks. The workflow can skip/fail explicitly if needed.
    return False


def main() -> int:
    p = argparse.ArgumentParser(description="Validate self-improvement PR guardrails.")
    p.add_argument("--base", default="main")
    p.add_argument("--markdown-output", default="skill-improvement-guardrails.md")
    p.add_argument("--json-output", default="skill-improvement-guardrails.json")
    args = p.parse_args()

    files = diff_files(args.base)
    controlled = [f for f in files if f.startswith(CONTROLLED_PREFIXES) or f in {"AGENTS.md"}]
    errors: List[str] = []
    warnings: List[str] = []

    if controlled:
        for artifact in REQUIRED_ARTIFACTS:
            if artifact not in files and not Path(artifact).exists():
                errors.append(f"missing required self-improvement artifact: {artifact}")
        proposal_files = [f for f in files if f.startswith("docs/agentic-self-improvement/proposals/") and f.endswith(".md")]
        if not proposal_files:
            errors.append("missing proposal under docs/agentic-self-improvement/proposals/*.md")

    text = diff_text(args.base)
    for pat in SENSITIVE_PATTERNS:
        if re.search(pat, text, flags=re.I):
            errors.append(f"possible safety boundary weakening: {pat}")

    removed_eval_lines = [line for line in text.splitlines() if line.startswith("-") and "EVAL-" in line]
    added_eval_lines = [line for line in text.splitlines() if line.startswith("+") and "EVAL-" in line]
    if removed_eval_lines and len(added_eval_lines) < len(removed_eval_lines):
        errors.append("eval cases appear to be removed without equal or greater replacement")

    skill_additions = [line for line in text.splitlines() if line.startswith("+") and not line.startswith("+++")]
    if len(skill_additions) > 350:
        warnings.append("large skill diff; verify this is not skill bloat")

    status = "PASS" if not errors else "FAIL"
    report = {
        "schema": "agentic.skill_guardrails_report.v1",
        "status": status,
        "controlled_files_changed": controlled,
        "errors": errors,
        "warnings": warnings,
    }
    Path(args.json_output).write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    md = ["# Skill improvement guardrails", "", f"Status: **{status}**", ""]
    if controlled:
        md.extend(["## Controlled files changed", *[f"- {f}" for f in controlled], ""])
    if errors:
        md.extend(["## Errors", *[f"- {e}" for e in errors], ""])
    if warnings:
        md.extend(["## Warnings", *[f"- {w}" for w in warnings], ""])
    Path(args.markdown_output).write_text("\n".join(md), encoding="utf-8")
    print("\n".join(md))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
