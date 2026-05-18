#!/usr/bin/env python3
"""Enforce the mandatory Codex PR review gate.

The Codex reviewer prompt must end with markers like:

    <!-- codex-pr-review-status: PASS -->
    <!-- codex-pr-review-risk: Low -->

This script parses the final Codex output, writes a concise report/artifact,
and exits non-zero unless the review explicitly passes.
"""
from __future__ import annotations

import argparse
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

STATUS_RE = re.compile(r"codex-pr-review-status\s*:\s*(PASS|FAIL|BLOCKED)", re.I)
RISK_RE = re.compile(r"codex-pr-review-risk\s*:\s*(Low|Medium|High)", re.I)
FALLBACK_STATUS_RE = re.compile(r"^\s*Status\s*:\s*(PASS|FAIL|BLOCKED)\s*$", re.I | re.M)
FALLBACK_RISK_RE = re.compile(r"^\s*Risk\s*:\s*(Low|Medium|High)\s*$", re.I | re.M)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except FileNotFoundError:
        return ""


def normalize(value: str | None, default: str = "UNKNOWN") -> str:
    if not value:
        return default
    return value.strip().upper()


def extract_decision(text: str) -> tuple[str, str, list[str]]:
    warnings: list[str] = []
    status_match = STATUS_RE.search(text)
    risk_match = RISK_RE.search(text)

    if not status_match:
        status_match = FALLBACK_STATUS_RE.search(text)
        if status_match:
            warnings.append("Used fallback Status line because final status marker was missing.")
    if not risk_match:
        risk_match = FALLBACK_RISK_RE.search(text)
        if risk_match:
            warnings.append("Used fallback Risk line because final risk marker was missing.")

    status = normalize(status_match.group(1) if status_match else None)
    risk_raw = risk_match.group(1) if risk_match else "UNKNOWN"
    risk = risk_raw.strip().capitalize() if risk_match and risk_raw else "UNKNOWN"

    if status == "UNKNOWN":
        warnings.append("Codex review output did not contain a parseable PASS/FAIL/BLOCKED decision.")
    if risk == "UNKNOWN":
        warnings.append("Codex review output did not contain a parseable Low/Medium/High risk marker.")

    return status, risk, warnings


def collect_failure_reasons(status: str, text: str, action_outcome: str | None, warnings: list[str]) -> list[str]:
    reasons: list[str] = []
    action_outcome_norm = (action_outcome or "").strip().lower()
    if action_outcome_norm and action_outcome_norm not in {"success", "skipped"}:
        reasons.append(f"Codex Action outcome was {action_outcome_norm}.")
    if not text.strip():
        reasons.append("Codex output file is missing or empty.")
    if status != "PASS":
        reasons.append(f"Codex review status is {status}; required status is PASS.")
    if any("final status marker was missing" in w.lower() for w in warnings):
        reasons.append("Final status marker is missing; require explicit marker for deterministic CI gating.")
    if any("final risk marker was missing" in w.lower() for w in warnings) or "parseable Low/Medium/High risk" in " ".join(warnings):
        reasons.append("Final risk marker is missing; require explicit Low/Medium/High risk marker for deterministic CI gating.")
    # Defensive fallback: obvious blocking terms should not pass without explicit PASS marker.
    lower = text.lower()
    if status == "PASS" and any(token in lower for token in ["[p0]", "[p1]", "status: fail", "status: blocked"]):
        reasons.append("Output contains blocking/severe finding language despite PASS status; review needs clarification.")
    return reasons


def write_report(report_path: Path, output_path: Path, result: dict[str, Any], codex_text: str) -> None:
    report_path.parent.mkdir(parents=True, exist_ok=True)
    status = result["status"]
    risk = result["risk"]
    passed = result["passed"]
    lines = [
        "# Codex PR Review Gate",
        "",
        f"Status: {'PASS' if passed else 'FAIL'}",
        f"Codex decision: {status}",
        f"Risk: {risk}",
        f"Generated at: {result['generated_at']}",
        f"PR: {result.get('pr_number') or 'unknown'}",
        f"Head SHA: {result.get('head_sha') or 'unknown'}",
        f"Source output: `{output_path}`",
        "",
    ]
    if result["failure_reasons"]:
        lines.append("## Failure reasons")
        for reason in result["failure_reasons"]:
            lines.append(f"- {reason}")
        lines.append("")
    if result["warnings"]:
        lines.append("## Warnings")
        for warning in result["warnings"]:
            lines.append(f"- {warning}")
        lines.append("")
    lines.extend([
        "## Codex output",
        "",
        codex_text.strip() or "_No Codex output was produced._",
        "",
    ])
    report_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, help="Path to Codex output markdown")
    parser.add_argument("--report", required=True, help="Path to write markdown gate report")
    parser.add_argument("--json", required=True, help="Path to write JSON gate report")
    parser.add_argument("--action-outcome", default=os.environ.get("CODEX_ACTION_OUTCOME", ""))
    parser.add_argument("--require-final-marker", action="store_true", default=True)
    args = parser.parse_args()

    output_path = Path(args.output)
    report_path = Path(args.report)
    json_path = Path(args.json)
    text = read_text(output_path)

    status, risk, warnings = extract_decision(text)
    failure_reasons = collect_failure_reasons(status, text, args.action_outcome, warnings)
    passed = not failure_reasons

    result: dict[str, Any] = {
        "passed": passed,
        "status": status,
        "risk": risk,
        "warnings": warnings,
        "failure_reasons": failure_reasons,
        "output_path": str(output_path),
        "report_path": str(report_path),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "pr_number": os.environ.get("PR_NUMBER") or os.environ.get("GITHUB_PR_NUMBER"),
        "base_ref": os.environ.get("PR_BASE"),
        "head_ref": os.environ.get("PR_HEAD"),
        "head_sha": os.environ.get("PR_HEAD_SHA"),
        "action_outcome": args.action_outcome,
    }

    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    write_report(report_path, output_path, result, text)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
