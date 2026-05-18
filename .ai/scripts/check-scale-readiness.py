#!/usr/bin/env python3
"""Heuristic scale-readiness review for agent PRs.

Dependency-free and intentionally conservative. It highlights issues for agent
self-review; it does not prove scalability.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from dataclasses import dataclass, asdict
from typing import List, Tuple

@dataclass
class Finding:
    severity: str
    pillar: str
    message: str
    recommendation: str


def run(cmd: List[str]) -> Tuple[int, str]:
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    return proc.returncode, proc.stdout


def diff_range() -> str:
    candidates = []
    if os.environ.get("BASE_REF"):
        candidates.append(os.environ["BASE_REF"])
    if os.environ.get("GITHUB_BASE_REF"):
        candidates.append(f"origin/{os.environ['GITHUB_BASE_REF']}")
    candidates.extend(["origin/main", "origin/master", "HEAD~1"])
    for base in candidates:
        code, _ = run(["git", "rev-parse", "--verify", base])
        if code == 0:
            return f"{base}...HEAD"
    return "HEAD"


def get_added_diff() -> Tuple[str, List[str]]:
    rng = diff_range()
    _, patch = run(["git", "diff", "--unified=0", rng])
    _, names = run(["git", "diff", "--name-only", rng])
    added = "\n".join(line[1:] for line in patch.splitlines() if line.startswith("+") and not line.startswith("+++"))
    files = [x.strip() for x in names.splitlines() if x.strip()]
    return added, files


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--format", choices=["markdown", "json"], default="markdown")
    ap.add_argument("--strict", action="store_true")
    args = ap.parse_args()

    added, files = get_added_diff()
    findings: List[Finding] = []

    checks = [
        ("medium", "reliability", r"requests\.(get|post|put|delete)\([^\n]*\)(?![^\n]*timeout=)", "Network call may not have a timeout.", "Add explicit timeout and error handling."),
        ("medium", "reliability", r"fetch\([^\n]*\)(?![\s\S]{0,200}AbortController|[\s\S]{0,200}signal)", "Fetch call may not have cancellation/timeout.", "Use AbortController or platform timeout."),
        ("medium", "scale", r"\.all\(\)|findAll\(\)|SELECT \*|scan\(", "Potential unbounded data access.", "Add pagination, limit, filtering, or streaming."),
        ("medium", "scale", r"for .* in .*:\n\s+.*(requests\.|fetch\(|axios\.|http\.)", "Possible synchronous fan-out in loop.", "Batch, bound concurrency, add timeouts, and handle partial failure."),
        ("medium", "performance", r"for \([^\n]*\) \{[\s\S]{0,200}(await |fetch\(|axios\.)", "Possible awaited I/O inside loop.", "Bound concurrency or batch requests; preserve ordering only if needed."),
        ("high", "security", r"password\s*=\s*['\"]|secret\s*=\s*['\"]|token\s*=\s*['\"]", "Possible hardcoded credential-like value.", "Remove and use secret management."),
        ("medium", "concurrency", r"global |static .* mutable|var .* = \[\]|let .* = \[\]", "Potential shared mutable state.", "Confirm it is not on a concurrent path or protect it."),
        ("medium", "operability", r"throw new Error\(['\"][^'\"]{0,20}['\"]\)|raise Exception\(['\"][^'\"]{0,20}['\"]\)", "Low-context error message.", "Add actionable context while avoiding sensitive data."),
    ]

    for severity, pillar, regex, msg, rec in checks:
        if re.search(regex, added, re.IGNORECASE | re.MULTILINE):
            findings.append(Finding(severity, pillar, msg, rec))

    relevant_paths = [f for f in files if re.search(r"(api|controller|route|handler|service|job|worker|queue|repository|dao|model|migration|infra|terraform|k8s|auth|security)", f, re.I)]
    if relevant_paths and not re.search(r"(metric|log|trace|span|logger|counter|histogram|observability)", added, re.I):
        findings.append(Finding("low", "operability", "Scale-relevant paths changed without obvious observability additions.", "Confirm existing telemetry is sufficient or add metrics/logs/traces."))

    verdict = "ready_with_notes"
    if any(f.severity == "high" for f in findings):
        verdict = "not_ready_until_high_findings_resolved_or_approved"

    result = {
        "verdict": verdict,
        "files_changed": files,
        "findings": [asdict(f) for f in findings],
    }

    if args.format == "json":
        print(json.dumps(result, indent=2))
    else:
        print("## Scale/readiness review")
        print()
        print(f"Verdict: {verdict}")
        print()
        if not findings:
            print("No heuristic scale findings. Still reason about scale, reliability, security, and operability.")
        else:
            print("Findings:")
            for f in findings:
                print(f"- **{f.severity.upper()} / {f.pillar}**: {f.message} Recommendation: {f.recommendation}")
        print()
        print("Required agent action: fix meaningful findings or document accepted residual risk and follow-up.")

    if args.strict and any(f.severity == "high" for f in findings):
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
