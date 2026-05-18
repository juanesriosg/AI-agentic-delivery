#!/usr/bin/env python3
"""Create a spec branch and scaffold a validator-friendly spec file for GPT Pro / AI PM usage."""
from __future__ import annotations

import argparse
import datetime as dt
import re
import subprocess
from pathlib import Path
from typing import Sequence


def run(cmd: Sequence[str], check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(list(cmd), text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=check)


def git(*args: str, check: bool = True) -> str:
    cp = run(["git", *args], check=check)
    return (cp.stdout or "").strip()


def slug(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "-", value).strip("-")
    return value or "poc-spec"


def replace_front_matter_value(text: str, key: str, value: str) -> str:
    pattern = rf"(?m)^{re.escape(key)}:\s*.*$"
    line = f'{key}: "{value}"' if any(ch in value for ch in [' ', '/', '@', '-']) else f"{key}: {value}"
    if re.search(pattern, text):
        return re.sub(pattern, line, text, count=1)
    if text.startswith("---\n"):
        end = text.find("\n---\n", 4)
        if end != -1:
            return text[:end] + "\n" + line + text[end:]
    return f"---\n{line}\n---\n\n" + text


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Create a dev/spec branch with an agentic spec scaffold")
    parser.add_argument("--title", required=True)
    parser.add_argument("--repo", default="owner/repo", help="GitHub repo name, e.g. owner/repo")
    parser.add_argument("--manager", default="@juanesriosg")
    parser.add_argument("--branch-prefix", default="dev")
    parser.add_argument("--base", default="main")
    parser.add_argument("--spec-dir", default="specs")
    parser.add_argument("--push", action="store_true")
    parser.add_argument("--ready", action="store_true", help="Mark status ready_for_agents. Otherwise draft.")
    args = parser.parse_args(argv)

    feature = slug(args.title)
    today = dt.date.today().strftime("%Y%m%d")
    today_iso = dt.date.today().isoformat()
    branch = f"{args.branch_prefix.rstrip('/')}/{feature}"
    spec_path = Path(args.spec_dir) / f"{feature}.spec.md"

    git("fetch", "origin", args.base, check=False)
    base_ref = f"origin/{args.base}" if git("rev-parse", "--verify", "--quiet", f"origin/{args.base}", check=False) else "HEAD"
    git("switch", "-C", branch, base_ref)

    template = Path("specs/_TEMPLATE.agentic-spec.md")
    if template.exists():
        text = template.read_text(encoding="utf-8")
    else:
        text = """---
spec_id: SPEC-YYYYMMDD-short-slug
spec_version: "1.0"
story_id: STORY-short-slug
title: "Feature title"
status: draft
priority: medium
risk_level: medium
owner: "@juanesriosg"
manager: "@juanesriosg"
repo: "owner/repo"
source_branch: "dev/feature"
target_branch: "main"
final_pr_base: "main"
expected_pr_strategy: source-spec-branch-final-pr
pr_strategy: source-spec-branch-final-pr
autonomy_level: L3
created_at: "YYYY-MM-DD"
updated_at: "YYYY-MM-DD"
---

# Agentic Spec: Feature title

## Description

## Business need

## User needs and scenarios

| Scenario ID | Scenario | Expected outcome |
|---|---|---|
| US-001 | TBD | TBD |

## Requirements

| ID | Requirement | Priority | Acceptance signal | Owner agent |
|---|---|---|---|---|
| FR-001 | TBD | must | TBD | TBD |

## Scope

## Files and areas to touch

## Files not to touch without approval

## Testing strategy

## Agent routing

## PR / task decomposition plan

| PR | Responsibility | Expected files | Depends on | Target branch |
|---|---|---|---|---|
| PR-1 | TBD | TBD | none | dev/feature |

## Acceptance criteria

| ID | Acceptance criterion | Type | Validated by | Evidence |
|---|---|---|---|---|
| AC-001 | TBD | functional | QA Agent | TBD |

## Risks and guardrails

## Clarifications

## Definition of done
"""
    replacements = {
        "spec_id": f"SPEC-{today}-{feature}",
        "spec_version": "1.0",
        "story_id": f"STORY-{feature}",
        "title": args.title,
        "status": "ready_for_agents" if args.ready else "draft",
        "priority": "medium",
        "risk_level": "medium",
        "owner": args.manager,
        "manager": args.manager,
        "repo": args.repo,
        "source_branch": branch,
        "target_branch": args.base,
        "final_pr_base": args.base,
        "expected_pr_strategy": "source-spec-branch-final-pr",
        "pr_strategy": "source-spec-branch-final-pr",
        "autonomy_level": "L3",
        "created_at": today_iso,
        "updated_at": today_iso,
    }
    for key, value in replacements.items():
        text = replace_front_matter_value(text, key, value)

    text = text.replace("SPEC-YYYYMMDD-short-slug", f"SPEC-{today}-{feature}")
    text = text.replace("STORY-short-slug", f"STORY-{feature}")
    text = text.replace("Short, human-readable feature title", args.title)
    text = text.replace("<Feature / User Story Title>", args.title)
    text = text.replace("<feature-or-story>", feature)
    text = text.replace("<github-user>", args.manager.lstrip("@"))
    text = text.replace("<owner/repo>", args.repo)
    text = text.replace("dev/<feature-or-story>", branch)
    text = text.replace("dev/feature", branch)
    text = text.replace("Feature title", args.title)

    spec_path.parent.mkdir(parents=True, exist_ok=True)
    spec_path.write_text(text, encoding="utf-8")
    git("add", str(spec_path))
    git("commit", "-m", f"spec: {args.title}", check=False)
    if args.push:
        git("push", "-u", "origin", branch)
    print(f"branch={branch}")
    print(f"spec={spec_path}")
    print("Keep status: draft until the spec is complete and validate it before changing to ready_for_agents.")
    print(f"validate=python .ai/scripts/validate_agentic_spec.py {spec_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
