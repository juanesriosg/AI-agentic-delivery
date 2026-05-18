#!/usr/bin/env python3
"""
POC-to-PR workflow runner v14 local-first.

Detects spec files pushed to a spec/dev branch, invokes the Agentic SDLC
orchestrator for each changed spec, and relies on source-spec-branch mode to
push validated implementation commits to the same branch and create a final PR.

Standard-library only. Intended for GitHub Actions and local dry-runs.
"""
from __future__ import annotations

import argparse
import fnmatch
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Iterable, List, Sequence

SPEC_PATTERNS = [
    "specs/**/*.md", "specs/**/*.yml", "specs/**/*.yaml",
    ".ai/inbox/specs/**/*.md", ".ai/inbox/specs/**/*.yml", ".ai/inbox/specs/**/*.yaml",
    ".codex/specs/**/*.md", "docs/specs/**/*.md", "requirements/specs/**/*.md",
]
IGNORE_PATTERNS = [
    "**/_TEMPLATE*", "**/*.template.*", "**/*.example.*", "**/example-*",
    ".ai/examples/**", "**/drafts/**", "**/.archived/**", "**/README.md",
]
READY_STATUSES = {"ready_for_agents", "ready", "approved", "implementation_ready"}
BLOCKED_STATUSES = {"template", "draft", "blocked", "on_hold", "hold", "paused", "clarification_needed", "needs_clarification", "cancelled", "canceled", "archived"}


def extract_status(path: str) -> str:
    try:
        text = Path(path).read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""
    # Markdown front matter / YAML-ish line / body fallback. Keep this small;
    # agentic_sdlc.py performs the full structural validation later.
    for line in text.splitlines()[:80]:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.lower().startswith(("status:", "spec_status:", "agent_status:", "implementation_status:")):
            value = stripped.split(":", 1)[1].strip().strip("'\"").split()[0]
            return value.lower().replace("-", "_")
    return ""


def is_ready_spec(path: str) -> bool:
    status = extract_status(path)
    if not status or status in BLOCKED_STATUSES:
        return False
    return status in READY_STATUSES


def run(cmd: Sequence[str], check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(list(cmd), text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=check)


def git(*args: str, check: bool = True) -> str:
    cp = run(["git", *args], check=check)
    return (cp.stdout or "").strip()


def matches(path: str, patterns: Iterable[str]) -> bool:
    normalized = path.replace("\\", "/")
    for pattern in patterns:
        candidates = [pattern, pattern.replace("**/", "")]
        if any(fnmatch.fnmatch(normalized, c) for c in candidates):
            return True
    return False


def changed_files(before: str, after: str) -> List[str]:
    if before and after and before != "0" * 40:
        out = git("diff", "--name-only", before, after, check=False)
        if out:
            return [x.strip() for x in out.splitlines() if x.strip()]
    # Fallback for manual dispatch or first push.
    out = git("ls-tree", "-r", "--name-only", "HEAD", check=False)
    return [x.strip() for x in out.splitlines() if x.strip()]


def detect_specs(before: str, after: str) -> List[str]:
    files = changed_files(before, after)
    specs = []
    for path in files:
        if matches(path, SPEC_PATTERNS) and not matches(path, IGNORE_PATTERNS) and is_ready_spec(path):
            specs.append(path)
    return sorted(set(specs))


def all_ready_specs_in_head() -> List[str]:
    """Return all ready specs in the checked-out branch.

    This is essential for source-spec-branch integration mode: agent pushes may
    update code/evidence/layer-gate files without touching the spec file, but the
    branch still needs another run to continue DB → API → frontend work.
    """
    out = git("ls-tree", "-r", "--name-only", "HEAD", check=False)
    specs = []
    for path in [x.strip() for x in out.splitlines() if x.strip()]:
        if matches(path, SPEC_PATTERNS) and not matches(path, IGNORE_PATTERNS) and is_ready_spec(path):
            specs.append(path)
    return sorted(set(specs))


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run POC-to-PR agentic flow for changed specs")
    parser.add_argument("--branch", default=os.environ.get("GITHUB_REF_NAME", ""), help="Spec branch name")
    parser.add_argument("--before", default=os.environ.get("GITHUB_EVENT_BEFORE", ""), help="Before SHA")
    parser.add_argument("--after", default=os.environ.get("GITHUB_SHA", "HEAD"), help="After SHA")
    parser.add_argument("--mode", choices=["local", "cloud"], default=os.environ.get("AGENTIC_MODE", "local"))
    parser.add_argument("--spec", action="append", default=[], help="Specific spec path. Can be repeated.")
    parser.add_argument("--max-specs", type=int, default=int(os.environ.get("AGENTIC_MAX_SPECS", "3")))
    parser.add_argument("--no-branch-scan-fallback", action="store_true", help="Do not scan all ready specs when changed files contain no spec changes.")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--allow-cloud", action="store_true", help="Explicitly permit cloud mode for this run. Default is local-only.")
    args = parser.parse_args(argv)

    if args.mode == "cloud" and not (args.allow_cloud or os.environ.get("AGENTIC_EXPLICIT_CLOUD", "").strip().lower() == "true"):
        print("ERROR: cloud mode is blocked by local-first policy. Use --allow-cloud or set AGENTIC_EXPLICIT_CLOUD=true only when cloud execution is explicitly intended.", file=sys.stderr)
        return 2

    branch = args.branch or git("rev-parse", "--abbrev-ref", "HEAD", check=False)
    if not branch or branch == "HEAD":
        print("ERROR: branch is required. In GitHub Actions use github.ref_name.", file=sys.stderr)
        return 2

    specs = []
    if args.spec:
        for spec in args.spec:
            clean = spec.strip().strip("'\"")
            if matches(clean, IGNORE_PATTERNS):
                print(f"Ignoring template/example spec path: {clean}")
                continue
            specs.append(clean)
    else:
        specs = detect_specs(args.before, args.after)
        if not specs and not args.no_branch_scan_fallback:
            specs = all_ready_specs_in_head()
            if specs:
                print("No changed spec file detected; continuing ready spec(s) already present on this branch.")
    if not specs:
        print("No ready specs detected. Nothing to run.")
        return 0

    report = {"branch": branch, "mode": args.mode, "specs": specs[: args.max_specs], "results": []}
    failures = 0
    for spec in specs[: args.max_specs]:
        cmd = [sys.executable, ".ai/scripts/agentic_sdlc.py"]
        if args.dry_run:
            cmd.append("--dry-run")
        if args.mode == "cloud" and (args.allow_cloud or os.environ.get("AGENTIC_EXPLICIT_CLOUD", "").strip().lower() == "true"):
            cmd.append("--allow-cloud")
        cmd.extend(["run-spec", "--mode", args.mode, "--branch", branch, "--spec", spec])
        print("Running:", " ".join(cmd), flush=True)
        cp = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(cp.stdout, end="")
        if cp.stderr:
            print(cp.stderr, file=sys.stderr, end="")
        report["results"].append({"spec": spec, "exit_code": cp.returncode})
        if cp.returncode != 0:
            failures += 1

    out = Path(".agent/state/poc-to-pr-run.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"POC-to-PR report written to {out}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
