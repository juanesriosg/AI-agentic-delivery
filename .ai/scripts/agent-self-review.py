#!/usr/bin/env python3
"""Lightweight self-review helper for autonomous agent PRs.

This script is intentionally dependency-free. It does heuristic checks over the git diff
and prints a markdown or JSON report. It is not a replacement for human review.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from dataclasses import dataclass, asdict
from typing import List, Tuple

PROTECTED_DELETE = re.compile(r"^(\.github/|\.ai/|infra/|infrastructure/|terraform/|cloudformation/|cdk/|k8s/|kubernetes/|helm/|migrations/|database/|db/migrations/|secrets/|certs/|config/production/|LICENSE|NOTICE|CODEOWNERS)")
SOURCE_RE = re.compile(r"\.(py|js|jsx|ts|tsx|go|rs|java|kt|cs|rb|php|scala|swift|c|cc|cpp|h|hpp)$")
TEST_RE = re.compile(r"(^|/)(test|tests|spec|__tests__)/|(_test|\.test|\.spec)\.")

@dataclass
class Finding:
    severity: str
    category: str
    message: str
    recommendation: str


def run(cmd: List[str]) -> Tuple[int, str]:
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    return proc.returncode, proc.stdout


def diff_range() -> str:
    candidates = []
    base_env = os.environ.get("BASE_REF")
    if base_env:
        candidates.append(base_env)
    gh_base = os.environ.get("GITHUB_BASE_REF")
    if gh_base:
        candidates.append(f"origin/{gh_base}")
    candidates.extend(["origin/main", "origin/master", "HEAD~1"])
    for base in candidates:
        code, _ = run(["git", "rev-parse", "--verify", base])
        if code == 0:
            return f"{base}...HEAD"
    return "HEAD"


def get_diff() -> Tuple[str, List[str], List[str], int]:
    rng = diff_range()
    _, patch = run(["git", "diff", "--unified=0", rng])
    _, names = run(["git", "diff", "--name-only", rng])
    _, status = run(["git", "diff", "--name-status", rng])
    _, numstat = run(["git", "diff", "--numstat", rng])
    files = [x.strip() for x in names.splitlines() if x.strip()]
    deleted = []
    for line in status.splitlines():
        parts = line.split("\t")
        if parts and parts[0].startswith("D") and len(parts) >= 2:
            deleted.append(parts[1])
    changed_lines = 0
    for line in numstat.splitlines():
        parts = line.split("\t")
        if len(parts) >= 2:
            for val in parts[:2]:
                if val.isdigit():
                    changed_lines += int(val)
    return patch, files, deleted, changed_lines


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--format", choices=["markdown", "json"], default="markdown")
    ap.add_argument("--strict", action="store_true")
    args = ap.parse_args()

    patch, files, deleted, changed_lines = get_diff()
    findings: List[Finding] = []

    source_files = [f for f in files if SOURCE_RE.search(f)]
    test_files = [f for f in files if TEST_RE.search(f)]

    if changed_lines > 400:
        findings.append(Finding("medium", "reviewability", f"Large diff detected: {changed_lines} changed lines.", "Split into smaller PRs or add strong review guidance."))
    if len(files) > 25:
        findings.append(Finding("medium", "scope", f"Many files changed: {len(files)} files.", "Confirm scope is intentional and not a broad refactor."))
    if source_files and not test_files:
        findings.append(Finding("medium", "testing", "Source files changed but no obvious test files changed.", "Add a targeted test or explain why existing/manual tests are sufficient."))

    for f in deleted:
        if PROTECTED_DELETE.search(f):
            findings.append(Finding("high", "deletion", f"Protected file deleted: {f}", "Restore the file or obtain explicit manager/owner approval."))
        else:
            findings.append(Finding("low", "deletion", f"File deleted: {f}", "Explain deletion and rollback in the PR."))

    added_lines = "\n".join(line[1:] for line in patch.splitlines() if line.startswith("+") and not line.startswith("+++"))
    patterns = [
        ("medium", "maintainability", r"\bTODO\b|\bFIXME\b", "New TODO/FIXME found.", "Resolve before PR or convert to tracked follow-up."),
        ("medium", "debuggability", r"console\.log\(|debugger;", "Debug statement found.", "Remove or replace with structured logging if intentional."),
        ("medium", "security", r"eval\(|exec\(|pickle\.loads|yaml\.load\(", "Potential unsafe execution/deserialization found.", "Validate safety or use safer APIs."),
        ("high", "security", r"AKIA[0-9A-Z]{16}|-----BEGIN PRIVATE KEY-----|aws_secret_access_key|ghp_[A-Za-z0-9_]{30,}", "Possible secret found.", "Remove secret and rotate if real."),
        ("medium", "reliability", r"requests\.(get|post|put|delete)\([^\n]*\)(?![^\n]*timeout=)", "Python requests call may lack timeout.", "Add explicit timeout."),
        ("medium", "data", r"SELECT \*", "SELECT * found.", "Select needed columns and confirm query scale."),
        ("medium", "error-handling", r"except Exception:\s*pass|catch \([^)]*\) \{\s*\}", "Swallowed exception found.", "Handle, log, or rethrow with context."),
    ]
    for severity, category, regex, msg, rec in patterns:
        if re.search(regex, added_lines, re.IGNORECASE | re.MULTILINE):
            findings.append(Finding(severity, category, msg, rec))

    score = 100
    for f in findings:
        score -= {"low": 3, "medium": 8, "high": 18}.get(f.severity, 5)
    score = max(score, 0)

    result = {
        "quality_score": score,
        "files_changed": len(files),
        "changed_lines": changed_lines,
        "findings": [asdict(f) for f in findings],
    }

    if args.format == "json":
        print(json.dumps(result, indent=2))
    else:
        print("## Agent self-review")
        print()
        print(f"Quality score: {score}/100")
        print(f"Files changed: {len(files)}")
        print(f"Changed lines: {changed_lines}")
        print()
        if not findings:
            print("No heuristic findings. Still perform human-level reasoning before PR.")
        else:
            print("Findings:")
            for f in findings:
                print(f"- **{f.severity.upper()} / {f.category}**: {f.message} Recommendation: {f.recommendation}")
        print()
        print("Required agent action: fix meaningful findings or document why they are accepted as follow-up.")

    if args.strict and any(f.severity == "high" for f in findings):
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
