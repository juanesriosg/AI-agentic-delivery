#!/usr/bin/env python3
"""Detect new/modified implementation-ready spec files on watched branches.

The script is intentionally dependency-free so it works in local machines,
Codex Cloud, and GitHub Actions. It ignores reusable templates/examples and
only dispatches specs whose status is ready for agents unless explicitly told to
process specs without a status.
"""
from __future__ import annotations

import argparse
import fnmatch
import json
import os
import re
import subprocess
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

DEFAULT_BRANCH_PATTERNS = [
    "develop",
    "dev/**",
    "spec/**",
    "chatgpt/**",
    "ai-spec/**",
    "feature/spec/**",
]

DEFAULT_SPEC_PATTERNS = [
    "specs/*.md",
    "specs/**/*.md",
    "specs/*.markdown",
    "specs/**/*.markdown",
    "specs/*.yml",
    "specs/**/*.yml",
    "specs/*.yaml",
    "specs/**/*.yaml",
    "specs/*.json",
    "specs/**/*.json",
    ".ai/inbox/specs/*.md",
    ".ai/inbox/specs/**/*.md",
    ".ai/inbox/specs/*.yml",
    ".ai/inbox/specs/**/*.yml",
    ".ai/inbox/specs/*.yaml",
    ".ai/inbox/specs/**/*.yaml",
    ".codex/specs/*.md",
    ".codex/specs/**/*.md",
    "docs/specs/*.md",
    "docs/specs/**/*.md",
    "requirements/specs/*.md",
    "requirements/specs/**/*.md",
]

DEFAULT_IGNORE_PATTERNS = [
    "**/_TEMPLATE.*",
    "**/_TEMPLATE*",
    "**/template.*",
    "**/*.template.*",
    "**/*.example.*",
    "**/example-*",
    ".ai/examples/**",
    "**/README.md",
    "**/.archived/**",
    "**/drafts/**",
]

DELETE_STATUSES = {"D"}
CHANGE_STATUSES = {"A", "M", "R", "C"}
DEFAULT_READY_STATUSES = ["ready_for_agents", "ready", "approved", "implementation_ready"]
PLACEHOLDER_PATTERNS = [
    r"\{\{[^}]+\}\}",
    r"<[^>\n]*(feature|story|repo|owner|path|file|todo|tbd|fill|short name|application|workload)[^>\n]*>",
    r"YYYY-MM-DD",
    r"SPEC-YYYYMMDD",
    r"@your-github-user",
    r"owner/repo",
]


def run(cmd: List[str]) -> str:
    try:
        return subprocess.check_output(cmd, text=True, stderr=subprocess.DEVNULL).strip()
    except subprocess.CalledProcessError:
        return ""


def load_event() -> Dict[str, Any]:
    event_path = os.environ.get("GITHUB_EVENT_PATH")
    if not event_path:
        return {}
    path = Path(event_path)
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def current_branch(event: Dict[str, Any]) -> str:
    ref_name = os.environ.get("GITHUB_REF_NAME")
    if ref_name:
        return ref_name
    ref = event.get("ref", "")
    if ref.startswith("refs/heads/"):
        return ref.removeprefix("refs/heads/")
    return run(["git", "rev-parse", "--abbrev-ref", "HEAD"]) or "unknown"


def current_sha(event: Dict[str, Any]) -> str:
    return os.environ.get("GITHUB_SHA") or event.get("after") or run(["git", "rev-parse", "HEAD"])


def base_sha(event: Dict[str, Any]) -> str:
    before = event.get("before") or os.environ.get("BASE_SHA") or ""
    if before and set(before) == {"0"}:
        return ""
    return before


def split_csv(values: str | None, default: List[str]) -> List[str]:
    if not values:
        return list(default)
    return [v.strip() for v in values.split(",") if v.strip()]


def normalize_status(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", (value or "").strip().lower()).strip("_")


def matches_any(path: str, patterns: Iterable[str]) -> bool:
    normalized = path.replace("\\", "/")
    for pattern in patterns:
        candidates = [pattern, pattern.replace("**/", "")]
        if any(fnmatch.fnmatch(normalized, candidate) for candidate in candidates):
            return True
    return False


def branch_allowed(branch: str, patterns: Iterable[str]) -> bool:
    return matches_any(branch, patterns)


def is_template_or_ignored_spec(path: str, ignore_patterns: Iterable[str]) -> bool:
    normalized = path.replace("\\", "/")
    name = Path(normalized).name.lower()
    lowered = normalized.lower()
    hard_template = (
        name.startswith("_template")
        or name.startswith("template.")
        or ".template." in name
        or "generic-agentic-spec-template" in name
        or "/examples/" in lowered
        or name in {"readme.md", "readme.markdown"}
    )
    return hard_template or matches_any(normalized, ignore_patterns)


def read_file(path: str) -> str:
    p = Path(path)
    if not p.exists() or not p.is_file():
        return ""
    try:
        return p.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""


def parse_front_matter_status(text: str) -> str:
    if not text.startswith("---\n"):
        return ""
    end = text.find("\n---\n", 4)
    if end == -1:
        return ""
    for line in text[4:end].splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or ":" not in stripped:
            continue
        key, value = stripped.split(":", 1)
        if normalize_status(key) in {"status", "spec_status", "agent_status", "implementation_status"}:
            value = value.strip().strip('"').strip("'")
            if " #" in value:
                value = value.split(" #", 1)[0].strip()
            return value
    return ""


def parse_body_status(text: str) -> str:
    for line in text.splitlines():
        m = re.match(r"^\s*(?:[-*]\s*)?(?:\*\*)?(status|spec_status|agent_status|implementation_status)(?:\*\*)?\s*[:=]\s*`?([^`#]+)`?", line, re.I)
        if m:
            return m.group(2).strip().split()[0].strip('"').strip("'")
    return ""


def spec_status(path: str) -> str:
    text = read_file(path)
    return parse_front_matter_status(text) or parse_body_status(text)


def placeholder_hits(path: str) -> List[str]:
    text = read_file(path)
    hits: List[str] = []
    for pattern in PLACEHOLDER_PATTERNS:
        hits.extend(str(x) for x in re.findall(pattern, text, flags=re.IGNORECASE | re.MULTILINE))
    return sorted(set(hits))


def parse_name_status(line: str) -> Tuple[str, str]:
    parts = line.split("\t")
    if not parts:
        return "", ""
    status = parts[0]
    if status.startswith("R") or status.startswith("C"):
        return status[0], parts[-1] if len(parts) >= 3 else ""
    return status[0], parts[1] if len(parts) >= 2 else ""


def changed_files(base: str, head: str) -> List[Tuple[str, str]]:
    if base:
        output = run(["git", "diff", "--name-status", base, head])
    else:
        output = run(["git", "diff-tree", "--no-commit-id", "--name-status", "-r", head])
        if not output:
            all_files = run(["git", "ls-files"])
            return [("A", line.strip()) for line in all_files.splitlines() if line.strip()]
    changes: List[Tuple[str, str]] = []
    for line in output.splitlines():
        status, path = parse_name_status(line)
        if status and path:
            changes.append((status, path))
    return changes


def detect(
    branch_patterns: List[str],
    spec_patterns: List[str],
    ignore_patterns: List[str],
    ready_statuses: List[str],
    process_without_status: bool,
) -> Dict[str, Any]:
    event = load_event()
    branch = current_branch(event)
    head = current_sha(event)
    base = base_sha(event)
    allowed = branch_allowed(branch, branch_patterns)
    ready_normalized = {normalize_status(s) for s in ready_statuses}

    changes = changed_files(base, head)
    specs: List[Dict[str, Any]] = []
    ignored: List[Dict[str, Any]] = []

    for status, path in changes:
        if not matches_any(path, spec_patterns):
            continue
        item: Dict[str, Any] = {"status": status, "path": path, "exists": Path(path).exists()}
        if is_template_or_ignored_spec(path, ignore_patterns):
            item["dispatch"] = False
            item["reason"] = "ignored template, example, readme, draft, or archived spec path"
            ignored.append(item)
            continue
        if status in DELETE_STATUSES:
            item["dispatch"] = False
            item["reason"] = "deleted spec; deletion requires manager review"
            ignored.append(item)
            continue
        if not allowed or status not in CHANGE_STATUSES:
            item["dispatch"] = False
            item["reason"] = "branch not watched or unsupported status"
            ignored.append(item)
            continue
        raw_status = spec_status(path)
        normalized = normalize_status(raw_status)
        item["spec_status"] = raw_status
        unresolved = placeholder_hits(path)
        if unresolved:
            item["dispatch"] = False
            item["reason"] = "unresolved template placeholders remain"
            item["placeholder_count"] = len(unresolved)
            ignored.append(item)
        elif normalized in ready_normalized or (not normalized and process_without_status):
            item["dispatch"] = True
            specs.append(item)
        else:
            item["dispatch"] = False
            item["reason"] = f"spec status is {raw_status or 'missing'}; expected {ready_statuses}"
            ignored.append(item)

    return {
        "repository": os.environ.get("GITHUB_REPOSITORY", "local"),
        "branch": branch,
        "branch_allowed": allowed,
        "base_sha": base,
        "head_sha": head,
        "branch_patterns": branch_patterns,
        "spec_patterns": spec_patterns,
        "ignore_patterns": ignore_patterns,
        "ready_statuses": ready_statuses,
        "process_without_status": process_without_status,
        "specs": specs,
        "ignored": ignored,
    }


def markdown(report: Dict[str, Any]) -> str:
    lines = [
        "# Agent Spec Ingestion Detection",
        "",
        f"Repository: `{report['repository']}`",
        f"Branch: `{report['branch']}`",
        f"Branch watched: **{'yes' if report['branch_allowed'] else 'no'}**",
        f"Head SHA: `{report['head_sha']}`",
        "",
        "## Dispatchable specs",
    ]
    specs = report.get("specs", [])
    if specs:
        for spec in specs:
            lines.append(f"- `{spec['path']}` ({spec['status']}) status=`{spec.get('spec_status', '')}`")
    else:
        lines.append("- None")
    lines.append("")
    lines.append("## Ignored spec changes")
    ignored = report.get("ignored", [])
    if ignored:
        for item in ignored:
            lines.append(f"- `{item['path']}` ({item['status']}): {item.get('reason', 'ignored')}")
    else:
        lines.append("- None")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--branch-patterns", default=os.environ.get("AGENT_SPEC_BRANCH_PATTERNS"))
    parser.add_argument("--spec-patterns", default=os.environ.get("AGENT_SPEC_PATH_PATTERNS"))
    parser.add_argument("--ignore-patterns", default=os.environ.get("AGENT_SPEC_IGNORE_PATTERNS"))
    parser.add_argument("--ready-statuses", default=os.environ.get("AGENT_SPEC_READY_STATUSES", ",".join(DEFAULT_READY_STATUSES)))
    parser.add_argument("--process-without-status", action="store_true", default=os.environ.get("AGENT_SPEC_PROCESS_WITHOUT_STATUS", "false").lower() == "true")
    parser.add_argument("--out", default=".agent/reports/detected-specs.json")
    parser.add_argument("--format", choices=["json", "markdown"], default="json")
    args = parser.parse_args()

    branch_patterns = split_csv(args.branch_patterns, DEFAULT_BRANCH_PATTERNS)
    spec_patterns = split_csv(args.spec_patterns, DEFAULT_SPEC_PATTERNS)
    ignore_patterns = split_csv(args.ignore_patterns, DEFAULT_IGNORE_PATTERNS)
    ready_statuses = split_csv(args.ready_statuses, DEFAULT_READY_STATUSES)
    report = detect(branch_patterns, spec_patterns, ignore_patterns, ready_statuses, args.process_without_status)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")

    if args.format == "markdown":
        print(markdown(report))
    else:
        print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
