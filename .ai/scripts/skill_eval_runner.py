#!/usr/bin/env python3
"""Deterministic eval runner for agent skill improvements.

This does not replace human review or model-based judging. It enforces basic
invariants that are cheap, repeatable, and hard to game.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

REQUIRED_SKILL_SECTIONS = [
    "purpose",
    "operating context",
    "principles",
    "procedure",
    "quality bar",
    "uncertainty behavior",
]
FORBIDDEN_WEAKENING_PATTERNS = [
    r"skip\s+codex\s+review",
    r"skip\s+qa",
    r"skip\s+pm",
    r"allow\s+delete",
    r"allow\s+production\s+deploy",
    r"allow\s+update\s+sql",
    r"allow\s+delete\s+sql",
    r"allow\s+insert\s+sql",
    r"force\s+push\s+allowed",
]
DEFAULT_EVALS = Path(".ai/evals/skill-improvement/eval-cases.json")


def words(text: str) -> int:
    return len(re.findall(r"\b\w+\b", text))


def headings(text: str) -> List[str]:
    return [m.group(1).strip().lower() for m in re.finditer(r"^##\s+(.+)$", text, flags=re.M)]


def check_skill_file(path: Path, max_words: int = 900) -> Tuple[bool, List[str]]:
    errors: List[str] = []
    text = path.read_text(encoding="utf-8")
    h = headings(text)
    lower_text = text.lower()
    for section in REQUIRED_SKILL_SECTIONS:
        if not any(section in item for item in h):
            errors.append(f"missing required section: {section}")
    if words(text) > max_words:
        errors.append(f"skill too long: {words(text)} words > {max_words}")
    for pat in FORBIDDEN_WEAKENING_PATTERNS:
        if re.search(pat, lower_text):
            errors.append(f"possible safety weakening phrase: {pat}")
    return not errors, errors


def check_eval_cases(path: Path) -> Tuple[bool, List[str]]:
    errors: List[str] = []
    if not path.exists():
        return False, [f"missing eval suite: {path}"]
    data = json.loads(path.read_text(encoding="utf-8"))
    cases = data.get("cases", [])
    if len(cases) < 5:
        errors.append("need at least 5 eval cases")
    levels = {c.get("level") for c in cases}
    if not {"easy", "realistic", "adversarial"}.issubset(levels):
        errors.append("eval suite must include easy, realistic, and adversarial cases")
    seen = set()
    required = {"id", "skill", "level", "type", "scenario", "expected_behavior", "failure_conditions", "requires_human_calibration"}
    for case in cases:
        cid = case.get("id")
        if not cid:
            errors.append("eval case missing id")
        elif cid in seen:
            errors.append(f"duplicate eval id: {cid}")
        seen.add(cid)
        missing = required - set(case)
        if missing:
            errors.append(f"{cid or '<unknown>'} missing fields: {sorted(missing)}")
        if not case.get("failure_conditions"):
            errors.append(f"{cid or '<unknown>'} has no failure conditions")
    return not errors, errors


def changed_files(base: str) -> List[Path]:
    import subprocess
    try:
        proc = subprocess.run(["git", "diff", "--name-only", f"{base}...HEAD"], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return [Path(line.strip()) for line in proc.stdout.splitlines() if line.strip()]
    except Exception:
        return []


def markdown_report(results: Dict[str, Any]) -> str:
    lines = ["# Skill eval report", "", f"Status: **{results['status']}**", ""]
    for item in results["checks"]:
        lines.append(f"## {item['name']}")
        lines.append(f"Status: **{item['status']}**")
        if item.get("errors"):
            lines.append("")
            lines.extend(f"- {err}" for err in item["errors"])
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser(description="Run deterministic skill evals.")
    p.add_argument("--all", action="store_true", help="Evaluate self-improvement core files, changed skills, and eval suites.")
    p.add_argument("--strict-all-skills", action="store_true", help="Audit every .ai/skills/*.skill.md file against the v15 skill-file standard.")
    p.add_argument("--base", default="main", help="Git base for changed-file mode.")
    p.add_argument("--skill", action="append", default=[])
    p.add_argument("--evals", default=str(DEFAULT_EVALS))
    p.add_argument("--max-skill-words", type=int, default=900)
    p.add_argument("--markdown-output", default="docs/agentic-self-improvement/eval-report.md")
    p.add_argument("--json-output", default=".agent/self-improvement/eval-report.json")
    args = p.parse_args()

    skill_paths: List[Path] = []
    if args.all:
        # Historical packages may contain older skill files that predate the
        # v15 skill-file standard. --all validates the self-improvement core
        # and any changed skill files; use --strict-all-skills to audit every
        # legacy skill in a later migration PR.
        skill_paths.extend([
            Path(".ai/skills/self-improvement-loop.skill.md"),
            Path(".ai/skills/feedback-capture.skill.md"),
            Path(".ai/skills/evaluation-design.skill.md"),
        ])
        skill_paths.extend(p for p in changed_files(args.base) if str(p).startswith(".ai/skills/") and p.suffix == ".md")
    if args.strict_all_skills:
        skill_paths.extend(sorted(Path(".ai/skills").glob("*.skill.md")))
    if args.skill:
        skill_paths.extend(Path(s) for s in args.skill)
    if not args.all and not args.skill and not args.strict_all_skills:
        skill_paths.extend(p for p in changed_files(args.base) if str(p).startswith(".ai/skills/") and p.suffix == ".md")

    checks: List[Dict[str, Any]] = []
    for path in sorted(set(skill_paths)):
        if not path.exists():
            checks.append({"name": str(path), "status": "FAIL", "errors": ["file missing"]})
            continue
        ok, errors = check_skill_file(path, args.max_skill_words)
        checks.append({"name": str(path), "status": "PASS" if ok else "FAIL", "errors": errors})

    ok, errors = check_eval_cases(Path(args.evals))
    checks.append({"name": args.evals, "status": "PASS" if ok else "FAIL", "errors": errors})

    status = "PASS" if all(c["status"] == "PASS" for c in checks) else "FAIL"
    result = {"schema": "agentic.skill_eval_report.v1", "status": status, "checks": checks}
    out_json = Path(args.json_output)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    out_md = Path(args.markdown_output)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text(markdown_report(result), encoding="utf-8")
    print(markdown_report(result))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
