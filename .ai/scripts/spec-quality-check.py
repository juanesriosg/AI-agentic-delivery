#!/usr/bin/env python3
"""Lightweight spec quality checker for autonomous agents.

Usage:
  python .ai/scripts/spec-quality-check.py --spec path/to/task.md --format markdown

The script does not understand every project format. It provides a conservative
heuristic report that helps agents notice missing goals, acceptance criteria,
constraints, tests, assumptions, and clarifications before coding.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Dict, List

KEYWORDS = {
    "business_goal": ["business goal", "user goal", "why", "outcome", "stakeholder", "problem", "product vision", "purpose"],
    "technical_goal": ["technical goal", "implementation", "implementation plan", "change", "solution", "task", "deliverable", "trd"],
    "acceptance_criteria": ["acceptance criteria", "acceptance", "definition of done", "done when", "must", "acceptance criteria coverage"],
    "constraints": ["constraint", "out of scope", "non-goal", "non-goals", "do not", "must not", "restriction", "product rules"],
    "tests": ["test", "testing", "validation", "qa", "verify", "e2e", "integration", "unit", "evidence"],
    "assumptions": ["assumption", "assumptions", "assume"],
    "clarifications": ["clarification", "question", "questions for clarification", "open questions", "unknown", "tbd", "todo"],
    "risks": ["risk", "risks", "security", "auth", "migration", "billing", "rollback", "production"],
}

AMBIGUOUS_PHRASES = [
    "works well", "make it better", "improve", "optimize", "fast", "scalable",
    "user friendly", "clean", "as needed", "tbd", "todo", "maybe", "probably",
    "should be fine", "handle all", "support everything",
]

HIGH_RISK_TERMS = [
    "auth", "authorization", "authentication", "permission", "billing", "payment",
    "migration", "database", "delete", "production", "infrastructure", "terraform",
    "kubernetes", "secret", "token", "public api", "contract", "schema",
]

DOC_TYPE_SIGNALS = {
    "prd": ["prd master", "product requirements", "product vision", "personas", "use cases", "product rules"],
    "implementation_plan": ["implementation plan by phases", "short prd understanding", "task id", "deliverable"],
    "trd": ["task requirements document", "functional requirements (task-level)", "context & links"],
    "task_list": ["task list", "relevant files", "acceptance criteria coverage", "- [ ]"],
}


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(errors="replace")


def has_any(text_l: str, words: List[str]) -> bool:
    return any(w in text_l for w in words)


def infer_doc_type(path: Path, text_l: str) -> str:
    name = path.name.lower()
    if "doc_type:" in text_l:
        for doc_type in DOC_TYPE_SIGNALS:
            if re.search(rf"doc_type:\s*{doc_type}\b", text_l):
                return doc_type
    if name.startswith("tasks-") or "task list" in name:
        return "task_list"
    scores = {
        doc_type: sum(1 for signal in signals if signal in text_l)
        for doc_type, signals in DOC_TYPE_SIGNALS.items()
    }
    doc_type, score = max(scores.items(), key=lambda item: item[1])
    return doc_type if score >= 2 else "generic"


def extract_acceptance_candidates(text: str) -> List[str]:
    lines = text.splitlines()
    candidates: List[str] = []
    in_ac = False
    for line in lines:
        stripped = line.strip()
        low = stripped.lower()
        if re.match(r"^#+\s+.*(acceptance criteria|acceptance|done when)", low):
            in_ac = True
            continue
        if in_ac and stripped.startswith("#"):
            in_ac = False
        if in_ac and stripped.startswith("|") and "|" in stripped[1:]:
            cells = [c.strip() for c in stripped.strip("|").split("|")]
            if cells and re.match(r"AC[- ]?\d+", cells[0], re.I):
                criterion = cells[1] if len(cells) > 1 else ""
                candidates.append(f"{cells[0]}: {criterion}".strip())
                continue
        if in_ac and (stripped.startswith("-") or re.match(r"^(AC-?\d+|\d+[.)])", stripped, re.I)):
            candidates.append(stripped)
        elif re.match(r"^(AC-?\d+|\d+[.)])", stripped, re.I):
            candidates.append(stripped)
    return candidates


def extract_task_candidates(text: str) -> List[str]:
    candidates: List[str] = []
    task_id_re = re.compile(r"\bP\d+-F\d+(?:-T\d+)?(?:-[A-Za-z0-9]+)?\b")
    checkbox_re = re.compile(r"^\s*-\s+\[[ xX]\]\s+(.+)$")
    for line in text.splitlines():
        stripped = line.strip()
        if task_id_re.search(stripped):
            candidates.append(stripped)
            continue
        match = checkbox_re.match(line)
        if match:
            candidates.append(match.group(1).strip())
    return candidates[:30]


def section_expectations(doc_type: str) -> Dict[str, List[str]]:
    if doc_type == "prd":
        return {
            "business_goal": ["product vision", "purpose", "goals", "success criteria"],
            "technical_goal": ["technical architecture", "core entities", "external services"],
            "acceptance_criteria": ["acceptance criteria"],
            "constraints": ["scope", "out of scope", "non-goals", "product rules"],
            "tests": ["validation method", "acceptance criteria"],
            "assumptions": ["assumptions"],
            "clarifications": ["open questions", "blocked items"],
            "risks": ["security", "privacy", "reliability", "failure modes"],
        }
    if doc_type == "implementation_plan":
        return {
            "business_goal": ["short prd understanding", "business goal", "prd reference"],
            "technical_goal": ["implementation plan by phases", "task id", "deliverable"],
            "acceptance_criteria": ["traceability", "acceptance criteria", "prd requirement"],
            "constraints": ["dependencies", "blocked high-risk areas", "code-level clarification"],
            "tests": ["validation", "traceability"],
            "assumptions": ["safe progress", "questions for clarification"],
            "clarifications": ["questions for clarification", "code-level clarification"],
            "risks": ["blocked high-risk areas", "risk"],
        }
    if doc_type == "trd":
        return {
            "business_goal": ["related prd sections", "goals"],
            "technical_goal": ["functional requirements (task-level)", "api / service", "data & schema", "frontend / ux"],
            "acceptance_criteria": ["acceptance criteria"],
            "constraints": ["non-goals", "constraints", "trade-offs"],
            "tests": ["testing and evidence", "validation"],
            "assumptions": ["assumptions"],
            "clarifications": ["open questions"],
            "risks": ["risks", "mitigations"],
        }
    if doc_type == "task_list":
        return {
            "business_goal": ["source documents", "prd"],
            "technical_goal": ["tasks", "relevant files"],
            "acceptance_criteria": ["acceptance criteria coverage"],
            "constraints": ["notes", "validation checklist"],
            "tests": ["validation checklist", "evidence"],
            "assumptions": ["notes"],
            "clarifications": ["notes", "tbd"],
            "risks": ["high-risk", "blocked"],
        }
    return KEYWORDS

def analyze(path: Path) -> Dict[str, object]:
    text = read_text(path)
    text_l = text.lower()
    doc_type = infer_doc_type(path, text_l)
    expected = section_expectations(doc_type)
    sections = {name: has_any(text_l, kws) for name, kws in expected.items()}
    acs = extract_acceptance_candidates(text)
    tasks = extract_task_candidates(text)
    ambiguous = [p for p in AMBIGUOUS_PHRASES if p in text_l]
    high_risk = [p for p in HIGH_RISK_TERMS if p in text_l]

    findings: List[Dict[str, str]] = []
    if not sections["business_goal"]:
        findings.append({"severity": "medium", "area": "spec", "message": "Business/user goal is not explicit."})
    if not sections["technical_goal"]:
        findings.append({"severity": "medium", "area": "spec", "message": "Technical goal or implementation target is not explicit."})
    if not sections["acceptance_criteria"] and not acs:
        findings.append({"severity": "high", "area": "acceptance", "message": "Acceptance criteria are missing or hard to identify."})
    if doc_type in {"implementation_plan", "task_list"} and not tasks:
        findings.append({"severity": "high", "area": "tasks", "message": "Task IDs or executable task rows are missing."})
    if not sections["tests"]:
        findings.append({"severity": "medium", "area": "validation", "message": "Validation/test expectations are missing."})
    if ambiguous:
        findings.append({"severity": "medium", "area": "ambiguity", "message": "Ambiguous phrases detected: " + ", ".join(sorted(set(ambiguous)))})
    if high_risk:
        findings.append({"severity": "high", "area": "risk", "message": "High-risk terms detected; confirm scope/approval: " + ", ".join(sorted(set(high_risk)))})

    score = 100
    for f in findings:
        score -= 25 if f["severity"] == "high" else 10
    score = max(score, 0)

    return {
        "spec": str(path),
        "doc_type": doc_type,
        "score": score,
        "sections_detected": sections,
        "acceptance_criteria_candidates": acs,
        "task_candidates": tasks,
        "findings": findings,
        "recommendation": "Proceed" if score >= 70 and not any(f["severity"] == "high" for f in findings) else "Clarify high-risk or missing acceptance items before risky implementation; continue safe progress only where possible.",
    }


def to_markdown(report: Dict[str, object]) -> str:
    lines = ["# Spec Quality Report", "", f"Spec: `{report['spec']}`", f"Document type: **{report['doc_type']}**", f"Score: **{report['score']} / 100**", ""]
    lines.append("## Sections detected")
    for key, val in report["sections_detected"].items():
        lines.append(f"- {key}: {'yes' if val else 'no'}")
    lines.append("")
    lines.append("## Acceptance criteria candidates")
    acs = report["acceptance_criteria_candidates"]
    if acs:
        for ac in acs:
            lines.append(f"- {ac}")
    else:
        lines.append("- None detected")
    lines.append("")
    lines.append("## Task candidates")
    tasks = report["task_candidates"]
    if tasks:
        for task in tasks:
            lines.append(f"- {task}")
    else:
        lines.append("- None detected")
    lines.append("")
    lines.append("## Findings")
    findings = report["findings"]
    if findings:
        for f in findings:
            lines.append(f"- **{f['severity']}** `{f['area']}`: {f['message']}")
    else:
        lines.append("- No major spec issues detected by heuristic scan.")
    lines.append("")
    lines.append("## Recommendation")
    lines.append(str(report["recommendation"]))
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--spec", required=True, help="Path to markdown/yaml/text task spec")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown")
    args = parser.parse_args()
    path = Path(args.spec)
    if not path.exists():
        raise SystemExit(f"Spec not found: {path}")
    report = analyze(path)
    if args.format == "json":
        print(json.dumps(report, indent=2))
    else:
        print(to_markdown(report))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
