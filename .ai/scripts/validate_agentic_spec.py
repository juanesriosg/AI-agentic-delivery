#!/usr/bin/env python3
"""Validate agentic spec files before autonomous implementation.

The validator is intentionally dependency-light. It checks that a ChatGPT-created
spec is not just a reusable template, has implementation-ready status, contains
clear requirements/acceptance criteria, and includes files-to-touch, testing,
QA/PM, and definition-of-done signals.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

REQUIRED_FRONT_MATTER_ALIASES = {
    "spec_id": ["spec_id"],
    "title": ["title"],
    "status": ["status"],
    "manager_or_owner": ["manager", "owner"],
    "source_branch": ["source_branch"],
    "target_branch": ["target_branch"],
    "priority": ["priority"],
    "risk": ["risk", "risk_level"],
    "pr_strategy": ["pr_strategy", "expected_pr_strategy"],
}
OPTIONAL_FRONT_MATTER_ALIASES = {
    "spec_version": ["spec_version"],
    "repo": ["repo"],
    "autonomy_level": ["autonomy_level"],
}

REQUIRED_SECTION_SIGNALS = {
    "description": ["description", "summary"],
    "needs_context": ["needs and context", "business need", "user needs"],
    "scope": ["scope", "in scope"],
    "requirements": ["requirements", "functional requirements"],
    "acceptance_criteria": ["acceptance criteria"],
    "files_to_touch": ["files and areas to touch", "files / directories to touch", "expected files"],
    "testing": ["testing requirements", "testing expectations", "unit tests"],
    "agent_routing": ["agent routing", "task breakdown", "owner agent"],
    "risks_guardrails": ["risks and guardrails", "risks", "guardrails"],
    "clarifications": ["clarifications", "questions"],
    "definition_of_done": ["definition of done", "done when"],
}

HIGH_RISK_WORDS = [
    "auth", "authorization", "billing", "payment", "migration", "infrastructure",
    "terraform", "aws", "lambda", "ec2", "rds", "dynamodb", "s3", "iam",
    "production", "delete", "destructive", "public api",
]

DEFAULT_ALLOWED_READY_STATUSES = ["ready_for_agents", "ready-for-agents", "ready"]

UNRESOLVED_TEMPLATE_PATTERNS = [
    r"\{\{[^}]+\}\}",
    r"<[^>\n]*(feature|story|capability|change|repo|owner|persona|path|file|todo|tbd|fill|short name|application|workload)[^>\n]*>",
    r"Write a short explanation",
    r"Describe the current problem",
    r"List exactly what agents are allowed",
    r"US-00\d:\s*$",
    r"REQ-[A-Z]+-00\d:\s*$",
    r"AC-00\d:\s*$",
    r"PR-00\d:\s*$",
]

SPEC_ID_RE = re.compile(r"\bSPEC-[A-Za-z0-9_.-]+\b", re.I)
REQ_RE = re.compile(r"\b(?:REQ-[A-Z]+|FR|NFR-[A-Z]+)-\d{1,3}\b", re.I)
AC_RE = re.compile(r"\bAC-\d{1,3}\b", re.I)
US_RE = re.compile(r"\bUS-\d{1,3}\b", re.I)
PR_RE = re.compile(r"\bPR-\d+\b", re.I)
TASK_ID_RE = re.compile(r"\bP\d+-F\d+(?:-T\d+)?(?:-[A-Za-z0-9]+)?\b", re.I)
CHECKBOX_RE = re.compile(r"^\s*-\s+\[[ xX]\]\s+.+$", re.M)

DOC_TYPE_SIGNALS = {
    "prd": ["prd master", "product requirements", "product vision", "personas", "use cases", "product rules"],
    "implementation_plan": ["implementation plan by phases", "short prd understanding", "task id", "deliverable"],
    "trd": ["task requirements document", "functional requirements (task-level)", "context & links"],
    "task_list": ["task list", "relevant files", "acceptance criteria coverage", "- [ ]"],
}

PACKAGE_REQUIRED_SIGNALS = {
    "prd": {
        "product_vision": ["product vision", "purpose", "goals", "success criteria"],
        "users_requirements": ["personas", "use cases", "functional requirements"],
        "acceptance_criteria": ["acceptance criteria"],
        "scope_guardrails": ["scope", "out of scope", "non-goals"],
        "technical_architecture": ["technical architecture", "core entities", "external services"],
        "open_questions": ["open questions", "assumptions", "blocked items"],
        "change_log": ["change log"],
    },
    "implementation_plan": {
        "prd_understanding": ["short prd understanding"],
        "clarifications": ["questions for clarification"],
        "current_priority": ["current execution priority"],
        "phases": ["implementation plan by phases", "phase 0", "task id"],
        "dependencies": ["dependencies"],
        "deliverables": ["deliverable"],
        "traceability": ["traceability"],
    },
    "trd": {
        "purpose": ["purpose of this trd"],
        "context": ["context & links", "related prd sections"],
        "goals": ["goals & non-goals"],
        "functional_requirements": ["functional requirements (task-level)", "fr-"],
        "acceptance_criteria": ["acceptance criteria", "ac-"],
        "testing": ["testing and evidence", "validation"],
        "risks_questions": ["risks", "open questions", "assumptions"],
    },
    "task_list": {
        "source_documents": ["source documents"],
        "acceptance_coverage": ["acceptance criteria coverage"],
        "relevant_files": ["relevant files"],
        "tasks": ["## tasks", "- [ ]"],
        "validation": ["validation checklist"],
    },
}


@dataclass
class SpecValidationResult:
    path: str
    passed: bool
    score: int
    max_score: int
    status: str
    errors: List[str]
    warnings: List[str]
    findings: Dict[str, Any]


def is_template_path(path: Path) -> bool:
    name = path.name.lower()
    return name.startswith("_template") or name.startswith("template.") or ".template." in name or name.endswith(".template.md") or name.endswith(".template.yml") or name.endswith(".template.yaml")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def normalize_doc_type(value: str) -> str:
    return normalize_status(value).replace("document", "").strip("_")


def infer_doc_type(path: Path, text: str, front: Dict[str, str] | None = None) -> str:
    front = front or {}
    explicit = front.get("doc_type") or front.get("document_type") or ""
    normalized = normalize_doc_type(explicit)
    if normalized in PACKAGE_REQUIRED_SIGNALS:
        return normalized

    name = path.name.lower()
    text_l = text.lower()
    if name.startswith("tasks-") or "task list" in name:
        return "task_list"
    scores = {
        doc_type: sum(1 for signal in signals if signal in text_l)
        for doc_type, signals in DOC_TYPE_SIGNALS.items()
    }
    doc_type, score = max(scores.items(), key=lambda item: item[1])
    return doc_type if score >= 2 else "agentic"


def parse_front_matter(text: str) -> Tuple[Dict[str, str], str]:
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}, text
    raw = text[4:end]
    body = text[end + 5:]
    data: Dict[str, str] = {}
    for line in raw.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or ":" not in stripped:
            continue
        key, value = stripped.split(":", 1)
        value = value.strip().strip('"').strip("'")
        if " #" in value:
            value = value.split(" #", 1)[0].strip()
        data[key.strip()] = value
    return data, body


def normalize_status(value: str) -> str:
    return value.strip().lower().replace("-", "_")


def front_has(front: Dict[str, str], aliases: Iterable[str]) -> bool:
    return any(front.get(alias) for alias in aliases)


def has_any(text_l: str, signals: Iterable[str]) -> bool:
    return any(signal.lower() in text_l for signal in signals)


def count_pattern(text: str, pattern: re.Pattern[str]) -> int:
    return len(pattern.findall(text))


def template_result(path: Path) -> SpecValidationResult:
    return SpecValidationResult(
        path=str(path),
        passed=True,
        score=1,
        max_score=1,
        status="template",
        errors=[],
        warnings=["Template file skipped for implementation validation; copy it and complete a real spec before agents implement."],
        findings={"template": True},
    )


def validate_package_markdown(
    path: Path,
    text: str,
    front: Dict[str, str],
    doc_type: str,
    allowed_statuses: List[str],
) -> SpecValidationResult:
    text_l = text.lower()
    errors: List[str] = []
    warnings: List[str] = []
    findings: Dict[str, Any] = {"doc_type": doc_type}
    score = 0
    max_score = 0

    required_front = {
        "spec_id": ["spec_id"],
        "title": ["title"],
        "status": ["status"],
        "doc_type": ["doc_type"],
        "source_branch": ["source_branch"],
        "target_branch": ["target_branch"],
    }
    for key, aliases in required_front.items():
        max_score += 1
        if front_has(front, aliases):
            score += 1
        else:
            errors.append(f"missing front matter for {doc_type}: {key}")

    raw_status = front.get("status", "").strip()
    status = normalize_status(raw_status)
    allowed_normalized = [normalize_status(x) for x in allowed_statuses]
    if status not in allowed_normalized:
        errors.append(f"status `{raw_status or 'unknown'}` is not allowed for autonomous implementation; expected one of: {', '.join(allowed_statuses)}")

    for section, signals in PACKAGE_REQUIRED_SIGNALS[doc_type].items():
        max_score += 2
        if has_any(text_l, signals):
            score += 2
        else:
            errors.append(f"missing required {doc_type} section/signal: {section}")

    req_count = count_pattern(text, REQ_RE)
    ac_count = count_pattern(text, AC_RE)
    task_count = count_pattern(text, TASK_ID_RE)
    checkbox_count = len(CHECKBOX_RE.findall(text))
    findings.update({
        "requirements": req_count,
        "acceptance_criteria": ac_count,
        "task_ids": task_count,
        "checkbox_tasks": checkbox_count,
    })

    if doc_type in {"prd", "trd"}:
        max_score += 6
        if req_count >= 1:
            score += 3
        else:
            errors.append(f"{doc_type} needs at least one FR-* or requirement ID")
        if ac_count >= 1:
            score += 3
        else:
            errors.append(f"{doc_type} needs at least one AC-* acceptance criterion")

    if doc_type == "implementation_plan":
        max_score += 6
        if task_count >= 1:
            score += 4
        else:
            errors.append("implementation plan needs at least one stable task ID such as P0-F0-T1")
        if "code-level clarification task" in text_l:
            score += 2
        else:
            warnings.append("implementation plan should include code-level clarification tasks where code inspection is needed")

    if doc_type == "task_list":
        max_score += 8
        if checkbox_count >= 3:
            score += 4
        else:
            errors.append("task list needs executable checkbox tasks and sub-tasks")
        if ac_count >= 1:
            score += 2
        else:
            errors.append("task list needs AC-* coverage copied or mapped from the TRD")
        if front.get("source_trd"):
            score += 2
        else:
            errors.append("task list needs source_trd front matter")

    high_risk_found = [word for word in HIGH_RISK_WORDS if word in text_l]
    findings["high_risk_terms_found"] = len(high_risk_found)
    if high_risk_found and not has_any(text_l, ["approval required", "blocked", "terraform", "manager"]):
        warnings.append("high-risk terms found; approval or blocker handling should be explicit")

    unresolved = [pattern for pattern in UNRESOLVED_TEMPLATE_PATTERNS if re.search(pattern, text, re.IGNORECASE | re.MULTILINE)]
    findings["unresolved_template_markers"] = len(unresolved)
    if unresolved:
        errors.append("unresolved template placeholders or empty template IDs remain; complete the package document before agents implement")

    if score > max_score:
        score = max_score
    passed = not errors and (score / max_score >= 0.72 if max_score else False)
    return SpecValidationResult(str(path), passed, score, max_score, status, errors, warnings, findings)

def validate_markdown(path: Path, allowed_statuses: List[str]) -> SpecValidationResult:
    text = read_text(path)
    text_l = text.lower()
    front, body = parse_front_matter(text)
    errors: List[str] = []
    warnings: List[str] = []
    findings: Dict[str, Any] = {}
    score = 0
    max_score = 0

    if is_template_path(path):
        return template_result(path)

    doc_type = infer_doc_type(path, text, front)
    if doc_type in PACKAGE_REQUIRED_SIGNALS:
        return validate_package_markdown(path, text, front, doc_type, allowed_statuses)

    for key, aliases in REQUIRED_FRONT_MATTER_ALIASES.items():
        max_score += 1
        if front_has(front, aliases):
            score += 1
        else:
            errors.append(f"missing front matter: {key} ({' or '.join(aliases)})")

    for key, aliases in OPTIONAL_FRONT_MATTER_ALIASES.items():
        if not front_has(front, aliases):
            warnings.append(f"optional front matter missing: {key} ({' or '.join(aliases)})")

    raw_status = front.get("status", "").strip()
    status = normalize_status(raw_status)
    allowed_normalized = [normalize_status(x) for x in allowed_statuses]
    if status not in allowed_normalized:
        errors.append(f"status `{raw_status or 'unknown'}` is not allowed for autonomous implementation; expected one of: {', '.join(allowed_statuses)}")

    for section, signals in REQUIRED_SECTION_SIGNALS.items():
        max_score += 2
        if has_any(text_l, signals):
            score += 2
        else:
            errors.append(f"missing required section/signal: {section}")

    req_count = count_pattern(text, REQ_RE)
    ac_count = count_pattern(text, AC_RE)
    us_count = count_pattern(text, US_RE)
    pr_count = count_pattern(text, PR_RE)
    findings.update({
        "requirements": req_count,
        "acceptance_criteria": ac_count,
        "user_stories": us_count,
        "pr_plan_items": pr_count,
    })

    max_score += 12
    if req_count >= 1:
        score += 3
    else:
        errors.append("no requirement IDs found; expected at least one FR-001, NFR-*-001, or REQ-*-001")
    if ac_count >= 1:
        score += 3
    else:
        errors.append("no acceptance criteria IDs found; expected at least one AC-001")
    if us_count >= 1 or req_count >= 1:
        score += 2
    else:
        errors.append("no user stories or requirements found")
    if pr_count >= 1:
        score += 2
    else:
        warnings.append("no PR plan IDs found; agents should create a one-responsibility PR plan")
    if "one_responsibility" in text_l or "one-responsibility" in text_l:
        score += 2
    else:
        warnings.append("one-responsibility PR strategy not clearly stated")

    max_score += 8
    testing_terms = ["unit", "component", "integration", "e2e", "visual", "accessibility", "regression", "qa"]
    testing_hits = sum(1 for term in testing_terms if re.search(rf"\b{re.escape(term)}\b", text_l))
    findings["testing_terms_present"] = testing_hits
    score += min(testing_hits, 4)
    if testing_hits < 3:
        warnings.append("testing requirements are thin; include unit/component/integration/E2E/visual/accessibility as relevant")

    if re.search(r"files? (and areas )?to touch|expected files to modify|files to inspect|expected files / directories to touch", text_l):
        score += 2
    else:
        errors.append("missing files-to-touch or discovery instructions")

    if re.search(r"out of scope|non-goals|must not touch|must not be touched|do not touch", text_l):
        score += 2
    else:
        errors.append("missing out-of-scope/non-goals/must-not-touch guardrails")

    high_risk_found = [word for word in HIGH_RISK_WORDS if word in text_l]
    findings["high_risk_terms_found"] = len(high_risk_found)
    if high_risk_found:
        if "terraform" in text_l or "requires_human_before_code: true" in text_l or "approval required" in text_l:
            score += 2
        else:
            warnings.append("high-risk terms found but Terraform/approval guardrails are not explicit")
    else:
        score += 2

    unresolved = [pattern for pattern in UNRESOLVED_TEMPLATE_PATTERNS if re.search(pattern, text, re.IGNORECASE | re.MULTILINE)]
    findings["unresolved_template_markers"] = len(unresolved)
    if unresolved:
        errors.append("unresolved template placeholders or empty template IDs remain; complete the spec before agents implement")

    if normalize_status(status) == "ready_for_agents" and errors:
        warnings.append("status is ready_for_agents but validation found blocking errors")

    if score > max_score:
        score = max_score
    passed = not errors and (score / max_score >= 0.72 if max_score else False)
    return SpecValidationResult(str(path), passed, score, max_score, status, errors, warnings, findings)


def parse_simple_yaml_scalars(text: str) -> Dict[str, str]:
    data: Dict[str, str] = {}
    for line in text.splitlines():
        if ":" not in line or line.lstrip().startswith("#"):
            continue
        if line.startswith(" ") or line.startswith("-"):
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip().strip('"').strip("'")
    return data


def validate_yaml_like(path: Path, allowed_statuses: List[str]) -> SpecValidationResult:
    if is_template_path(path):
        return template_result(path)
    text = read_text(path)
    text_l = text.lower()
    data = parse_simple_yaml_scalars(text)
    errors: List[str] = []
    warnings: List[str] = []
    findings: Dict[str, Any] = {}
    score = 0
    required = ["spec", "summary", "requirements", "scope", "files", "acceptance_criteria", "testing", "definition_of_done"]
    max_score = len(required) * 2 + 6
    for key in required:
        if key in data or key in text_l:
            score += 2
        else:
            errors.append(f"missing yaml key/section: {key}")
    raw_status = data.get("status", "")
    status = normalize_status(raw_status)
    allowed_normalized = [normalize_status(x) for x in allowed_statuses]
    if status and status not in allowed_normalized:
        errors.append(f"status `{raw_status}` is not allowed for autonomous implementation; expected one of: {', '.join(allowed_statuses)}")
    elif status:
        score += 2
    else:
        errors.append("missing yaml status")
    if "expected_to_touch" in text_l or "files_to_touch" in text_l:
        score += 2
    else:
        errors.append("files.expected_to_touch or files_to_touch is required")
    if "do_not_touch" in text_l or "without_approval" in text_l:
        score += 2
    else:
        errors.append("files.do_not_touch_without_approval is required")
    unresolved = [pattern for pattern in UNRESOLVED_TEMPLATE_PATTERNS if re.search(pattern, text, re.IGNORECASE | re.MULTILINE)]
    findings["unresolved_template_markers"] = len(unresolved)
    if unresolved:
        errors.append("unresolved template placeholders remain")
    return SpecValidationResult(str(path), not errors, min(score, max_score), max_score, status, errors, warnings, findings)


def validate(path: Path, allowed_statuses: List[str] | None = None) -> SpecValidationResult:
    allowed = allowed_statuses or DEFAULT_ALLOWED_READY_STATUSES
    suffixes = [s.lower() for s in path.suffixes]
    if ".md" in suffixes:
        return validate_markdown(path, allowed)
    if ".yml" in suffixes or ".yaml" in suffixes:
        return validate_yaml_like(path, allowed)
    return SpecValidationResult(str(path), False, 0, 1, "", ["unsupported spec file extension; use .md, .yml, or .yaml"], [], {})


def print_markdown(result: SpecValidationResult) -> None:
    print(f"# Spec validation report: {Path(result.path).name}\n")
    print(f"Status: `{result.status or 'unknown'}`")
    print(f"Passed: `{str(result.passed).lower()}`")
    print(f"Score: `{result.score}/{result.max_score}`\n")
    print("## Findings\n")
    for key, value in result.findings.items():
        print(f"- {key}: {value}")
    print()
    if result.errors:
        print("## Blocking errors\n")
        for item in result.errors:
            print(f"- {item}")
        print()
    if result.warnings:
        print("## Warnings\n")
        for item in result.warnings:
            print(f"- {item}")
        print()
    print("## Recommendation\n")
    if result.passed:
        print("Spec is structurally ready for agent task splitting. Agents must still perform normal comprehension, risk, QA, and PM gates.")
    else:
        print("Spec needs clarification or completion before autonomous implementation. Agents may continue safe discovery work only.")


def main(argv: List[str]) -> int:
    parser = argparse.ArgumentParser(description="Validate agentic spec files")
    parser.add_argument("spec", nargs="+", type=Path, help="Path(s) to spec files")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown")
    parser.add_argument("--json", action="store_true", help="Alias for --format json")
    parser.add_argument("--allow-status", action="append", dest="allowed_statuses", default=None, help="Allowed status. Repeatable. Defaults to ready_for_agents.")
    args = parser.parse_args(argv)
    results: List[SpecValidationResult] = []
    for spec in args.spec:
        if not spec.exists():
            results.append(SpecValidationResult(str(spec), False, 0, 1, "", [f"Spec not found: {spec}"], [], {}))
        else:
            results.append(validate(spec, allowed_statuses=args.allowed_statuses))
    if args.json or args.format == "json":
        print(json.dumps([asdict(r) for r in results], indent=2))
    else:
        for idx, result in enumerate(results):
            if idx:
                print("\n---\n")
            print_markdown(result)
    return 0 if all(r.passed for r in results) else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
