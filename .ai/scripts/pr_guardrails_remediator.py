#!/usr/bin/env python3
"""Create a remediation plan for PR guardrail failures.

The goal is to avoid wasting agent work. This script does not weaken the guardrail;
it translates failures into safe corrective actions that another agent can execute.
It only uses local files and git metadata.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List

RUNTIME_PREFIXES = (
    ".agent/", ".venv/", "venv/", "node_modules/", "vendor/bundle/",
    "__pycache__/", ".pytest_cache/", ".mypy_cache/", "target/", "dist/", "build/",
)
EVIDENCE_PREFIXES = ("docs/agentic-evidence/", ".agent/")
TEST_HINTS = ("test", "spec", "__tests__", "e2e", "integration", "cypress", "playwright", "vitest", "jest", "pytest")


def run(cmd: List[str]) -> str:
    cp = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return cp.stdout if cp.returncode == 0 else ""


def is_runtime(path: str) -> bool:
    p = path.replace("\\", "/")
    return any(p.startswith(prefix) for prefix in RUNTIME_PREFIXES) or "/__pycache__/" in p or p.endswith(".pyc")


def is_evidence(path: str) -> bool:
    p = path.replace("\\", "/")
    return any(p.startswith(prefix) for prefix in EVIDENCE_PREFIXES)


def classify(path: str) -> str:
    p = path.replace("\\", "/").lower()
    if is_runtime(p):
        return "runtime"
    if is_evidence(p):
        return "evidence"
    if any(h in p for h in TEST_HINTS):
        return "tests"
    if p.startswith(("infra/", "terraform/", "cdk/", "cloudformation/", "k8s/", "helm/")) or p.endswith(".tf") or "/terraform/" in p:
        return "cloud"
    if any(token in p for token in ("migration", "database", "prisma", "schema.sql", "/db/", "sql/")):
        return "database"
    if any(token in p for token in ("api/", "routes/", "controllers/", "handlers/", "lambda", "backend", "server")):
        return "backend"
    if p.endswith((".tsx", ".jsx", ".vue", ".svelte", ".css", ".scss", ".html")) or any(token in p for token in ("components/", "pages/", "app/", "frontend/", "ui/", "styles/", "public/")):
        return "frontend"
    if any(token in p for token in ("auth", "permission", "iam", "policy", "secret", "security")):
        return "security"
    return "other"


def load_report(path: Path) -> Dict[str, Any]:
    text = path.read_text(encoding="utf-8", errors="replace")
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Could not parse guardrail report as JSON: {path}\n{exc}")


def split_recommendation(files: Iterable[str]) -> Dict[str, List[str]]:
    buckets: Dict[str, List[str]] = defaultdict(list)
    for f in files:
        buckets[classify(f)].append(f)
    return {k: sorted(v) for k, v in sorted(buckets.items()) if v}


def infer_actions(report: Dict[str, Any]) -> List[Dict[str, Any]]:
    failures = report.get("failures") or []
    files = report.get("files") or []
    implementation_files = report.get("implementation_files") or [f for f in files if not is_runtime(f) and not is_evidence(f)]
    evidence_files = report.get("evidence_files") or [f for f in files if is_evidence(f) and not is_runtime(f)]
    runtime_files = report.get("runtime_files") or [f for f in files if is_runtime(f)]
    actions: List[Dict[str, Any]] = []

    for failure in failures:
        low = failure.lower()
        if "too many" in low and ("line" in low or "file" in low):
            buckets = split_recommendation(implementation_files)
            if not implementation_files and (evidence_files or runtime_files):
                actions.append({
                    "type": "guardrail-noise",
                    "severity": "medium",
                    "summary": "PR size failure appears to be caused by evidence/runtime files rather than implementation files.",
                    "recommended_fix": "Use the updated pr_guardrails.py that counts implementation files separately, then rerun guardrails.",
                    "safe_to_auto_apply": True,
                })
            elif len(buckets) > 1:
                actions.append({
                    "type": "split-pr",
                    "severity": "high",
                    "summary": "Implementation changes span multiple buckets and should be split into smaller PRs.",
                    "recommended_fix": "Create one branch/PR per bucket and keep evidence with the relevant implementation bucket.",
                    "buckets": buckets,
                    "safe_to_auto_apply": False,
                })
            else:
                actions.append({
                    "type": "compress-or-split",
                    "severity": "medium",
                    "summary": "PR is too large inside one responsibility.",
                    "recommended_fix": "Compress verbose generated evidence, remove duplicated logs, or split by subtask while preserving tests and acceptance evidence.",
                    "buckets": buckets,
                    "safe_to_auto_apply": False,
                })
        elif "missing evidence directory" in low:
            actions.append({
                "type": "repair-evidence-path",
                "severity": "medium",
                "summary": failure,
                "recommended_fix": "Search docs/agentic-evidence for a near-matching spec/task directory, then move or copy evidence to the expected task-id path. Do not invent passing evidence.",
                "safe_to_auto_apply": False,
            })
        elif "pending" in low or "placeholder" in low:
            actions.append({
                "type": "complete-evidence",
                "severity": "high",
                "summary": failure,
                "recommended_fix": "Run the relevant tests/checks, replace PENDING_AGENT_VERIFICATION placeholders with real results, and keep failures explicit instead of marking pass.",
                "safe_to_auto_apply": False,
            })
        elif "multiple implementation domains" in low:
            actions.append({
                "type": "split-pr",
                "severity": "high",
                "summary": failure,
                "recommended_fix": "Split into domain-specific PRs: database first, then API/backend, then frontend. Keep support/test/evidence with the matching domain.",
                "buckets": split_recommendation(implementation_files),
                "safe_to_auto_apply": False,
            })
        elif "no test" in low or "test file" in low:
            actions.append({
                "type": "add-tests-or-justify",
                "severity": "high",
                "summary": failure,
                "recommended_fix": "Add the smallest meaningful unit/integration/e2e test. If the change is documentation/config-only, add explicit non-applicable evidence in test-evidence.md.",
                "safe_to_auto_apply": False,
            })
        elif "branch conflict" in low:
            actions.append({
                "type": "avoid-conflict",
                "severity": "high",
                "summary": failure,
                "recommended_fix": "Stop this task, inspect active branches/path leases, then either switch task or extract a new file/component to avoid touching the contested file.",
                "safe_to_auto_apply": False,
            })
        else:
            actions.append({
                "type": "manual-analysis",
                "severity": "medium",
                "summary": failure,
                "recommended_fix": "Ask the PR Guardrails Remediation Agent to inspect the diff, spec, evidence, and guardrail output and propose the smallest safe fix.",
                "safe_to_auto_apply": False,
            })
    return actions


def build_prompt(report_path: Path, report: Dict[str, Any], actions: List[Dict[str, Any]]) -> str:
    return f"""# PR Guardrails Remediation Agent Prompt

You are fixing a PR that failed guardrails. Do not weaken guardrails. Preserve completed work.

## Inputs

- Guardrail report: `{report_path}`
- Failures:
{json.dumps(report.get('failures', []), indent=2)}

## Required behavior

1. Read the guardrail report and current git diff.
2. Classify each failure as auto-fixable, split-needed, evidence-needed, tests-needed, or clarification-needed.
3. Prefer the smallest safe remediation.
4. Do not mark QA/PM/test evidence as passing unless real evidence exists.
5. If PR is too large, split by responsibility/domain instead of deleting work.
6. If missing acceptance/evidence wording exists under another label, search specs/TRD/task docs for synonyms: acceptance criteria, validation checklist, definition of done, QA checklist, PM checklist, evidence, pass criteria.
7. After remediation, rerun `.ai/scripts/pr_guardrails.py` and produce a short remediation report.

## Recommended actions

{json.dumps(actions, indent=2)}
"""


def markdown_report(report_path: Path, report: Dict[str, Any], actions: List[Dict[str, Any]]) -> str:
    lines = [
        "# PR Guardrails Remediation Plan",
        "",
        f"Source report: `{report_path}`",
        "",
        "## Guardrail failures",
        "",
    ]
    for failure in report.get("failures", []):
        lines.append(f"- {failure}")
    lines += ["", "## Suggested remediation", ""]
    for i, action in enumerate(actions, 1):
        lines.append(f"### {i}. {action['type']} ({action['severity']})")
        lines.append("")
        lines.append(action["summary"])
        lines.append("")
        lines.append(f"Recommended fix: {action['recommended_fix']}")
        if action.get("buckets"):
            lines.append("")
            lines.append("Buckets:")
            for bucket, files in action["buckets"].items():
                lines.append(f"- **{bucket}**")
                for f in files[:20]:
                    lines.append(f"  - `{f}`")
                if len(files) > 20:
                    lines.append(f"  - ... {len(files) - 20} more")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a remediation plan for failed PR guardrails")
    parser.add_argument("--report", default="pr_guardrails.out", help="Path to pr_guardrails JSON output")
    parser.add_argument("--out-dir", default=".agent/remediation", help="Where to write remediation artifacts")
    args = parser.parse_args()

    report_path = Path(args.report)
    report = load_report(report_path)
    actions = infer_actions(report)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "pr-guardrails-remediation.json").write_text(json.dumps({"source": str(report_path), "actions": actions, "report": report}, indent=2) + "\n", encoding="utf-8")
    (out_dir / "pr-guardrails-remediation.md").write_text(markdown_report(report_path, report, actions), encoding="utf-8")
    (out_dir / "pr-guardrails-remediation.prompt.md").write_text(build_prompt(report_path, report, actions), encoding="utf-8")
    print(f"Remediation plan written to {out_dir}")
    print(markdown_report(report_path, report, actions))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
