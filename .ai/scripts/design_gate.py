#!/usr/bin/env python3
"""Design-first spec gate for Agentic Delivery OS v12.

Blocks autonomous implementation until a spec contains a clear design blueprint:
requirements, architecture, data model, API/cloud contracts, testing strategy,
layer order, and programming paradigm decision. The script intentionally uses
only the Python standard library.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

PLACEHOLDERS = ["{{", "}}", "<feature", "<change", "<todo", "<fill", "tbd", "todo:"]

REQUIRED_GROUPS: Dict[str, List[str]] = {
    "description": ["description", "summary", "what"],
    "business_need": ["business need", "business goal", "why", "problem"],
    "requirements": ["requirements", "functional requirements", "non-functional requirements"],
    "design": ["design", "ux", "ui", "user flow", "solution design"],
    "architecture": ["architecture", "component design", "system design", "technical design"],
    "data_model": ["data model", "data requirements", "schema", "database", "entities", "domain model", "database contract"],
    "api_contract": ["api contract", "contract", "endpoints", "backend contract", "interface"],
    "cloud_infrastructure": ["cloud", "aws", "infrastructure", "terraform"],
    "testing_strategy": ["testing strategy", "test strategy", "testing expectations", "test plan"],
    "layer_order": ["layer order", "dependency order", "layer sequencing", "db api front", "database api frontend", "database api frontend", "db → api → frontend", "database → api → frontend"],
    "paradigm": ["paradigm", "programming paradigm", "programming model", "design pattern decision", "data-driven", "object-oriented", "event-driven"],
    "acceptance_criteria": ["acceptance criteria", "definition of done", "done"],
    "files_to_touch": ["files", "areas to touch", "files to touch", "paths"],
}

NOT_APPLICABLE_PATTERNS = [
    r"\bnot applicable\b",
    r"\bn/a\b",
    r"\bno new\b",
    r"\bnone required\b",
    r"\bdoes not apply\b",
]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def strip_front_matter(text: str) -> str:
    if text.startswith("---\n"):
        end = text.find("\n---\n", 4)
        if end != -1:
            return text[end + 5:]
    return text


def headings(text: str) -> List[Tuple[int, str, int]]:
    result: List[Tuple[int, str, int]] = []
    for i, line in enumerate(strip_front_matter(text).splitlines()):
        m = re.match(r"^(#{1,6})\s+(.*)$", line.strip())
        if m:
            result.append((len(m.group(1)), m.group(2).strip(), i))
    return result


def find_section(text: str, keywords: Iterable[str]) -> str:
    body = strip_front_matter(text)
    lines = body.splitlines()
    start = None
    start_level = 999
    keys = [k.lower() for k in keywords]
    for i, line in enumerate(lines):
        m = re.match(r"^(#{1,6})\s+(.*)$", line.strip())
        if not m:
            continue
        level = len(m.group(1))
        title = m.group(2).strip().lower()
        if any(k in title for k in keys):
            start = i + 1
            start_level = level
            break
    if start is None:
        return ""
    out: List[str] = []
    for line in lines[start:]:
        m = re.match(r"^(#{1,6})\s+(.*)$", line.strip())
        if m and len(m.group(1)) <= start_level:
            break
        out.append(line)
    return "\n".join(out).strip()


def is_not_applicable(text: str) -> bool:
    lower = text.lower()
    return any(re.search(pattern, lower) for pattern in NOT_APPLICABLE_PATTERNS)


def has_real_content(text: str, allow_na: bool) -> bool:
    cleaned = re.sub(r"[`*_#|\-\s]", "", text).strip().lower()
    if allow_na and is_not_applicable(text):
        return True
    if len(cleaned) < 20:
        return False
    if any(p in cleaned for p in ["<", ">", "{{", "}}"]):
        return False
    return True


def unresolved_placeholders(text: str) -> List[str]:
    lower = text.lower()
    findings = []
    for marker in PLACEHOLDERS:
        if marker in lower:
            findings.append(marker)
    # detect markdown table rows that still look like placeholders
    if re.search(r"\|\s*<[^|>]+>\s*\|", text):
        findings.append("table placeholder cells")
    return sorted(set(findings))


def evaluate(text: str, allow_na: bool) -> Dict[str, object]:
    sections = {}
    failures: List[str] = []
    warnings: List[str] = []
    for name, keys in REQUIRED_GROUPS.items():
        section = find_section(text, keys)
        ok = bool(section) and has_real_content(section, allow_na=allow_na)
        sections[name] = {"present": bool(section), "ok": ok, "not_applicable": bool(section and is_not_applicable(section))}
        if not ok:
            failures.append(f"Missing or weak design section: {name}")
    ph = unresolved_placeholders(text)
    if ph:
        failures.append("Unresolved placeholders exist: " + ", ".join(ph))
    # Heuristic warnings for missing cross-layer design details.
    lower = text.lower()
    if "database" in lower and "api" in lower and "frontend" in lower:
        if not re.search(r"database.*api.*front|db.*api.*front", lower, re.S):
            warnings.append("Spec mentions database, API, and frontend but does not clearly state DB → API → frontend sequencing.")
    if not any(word in lower for word in ["data-driven", "object-oriented", "event-driven", "oop"]):
        warnings.append("Programming paradigm decision is not explicit.")
    return {
        "status": "PASS" if not failures else "FAIL",
        "failures": failures,
        "warnings": warnings,
        "sections": sections,
    }


def markdown_report(report: Dict[str, object], spec: Path) -> str:
    lines = [f"# Design Gate Report", "", f"Spec: `{spec}`", "", f"Status: **{report['status']}**", ""]
    failures = report.get("failures", [])
    warnings = report.get("warnings", [])
    if failures:
        lines.extend(["## Blocking findings", ""])
        lines.extend(f"- {item}" for item in failures)
        lines.append("")
    if warnings:
        lines.extend(["## Warnings", ""])
        lines.extend(f"- {item}" for item in warnings)
        lines.append("")
    lines.extend(["## Section checklist", "", "| Section | Present | OK | N/A |", "|---|---:|---:|---:|"])
    for name, data in (report.get("sections") or {}).items():
        lines.append(f"| {name} | {data.get('present')} | {data.get('ok')} | {data.get('not_applicable')} |")
    lines.extend(["", "## Rule", "", "Implementation is allowed only after design, data model, API/cloud contracts, test strategy, layer order, and paradigm are explicit or intentionally marked not applicable."])
    return "\n".join(lines) + "\n"


def main() -> int:
    p = argparse.ArgumentParser(description="Validate a spec is design-ready before agents implement it.")
    p.add_argument("--spec", required=True, type=Path)
    p.add_argument("--allow-not-applicable", action="store_true")
    p.add_argument("--format", choices=["json", "markdown"], default="markdown")
    p.add_argument("--markdown-output", type=Path)
    args = p.parse_args()
    text = read(args.spec)
    report = evaluate(text, allow_na=args.allow_not_applicable)
    if args.markdown_output:
        args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
        args.markdown_output.write_text(markdown_report(report, args.spec), encoding="utf-8")
    if args.format == "json":
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(markdown_report(report, args.spec))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
