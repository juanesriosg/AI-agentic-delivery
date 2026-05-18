#!/usr/bin/env python3
"""Build a concise business context pack from specs, PR summaries, and rules."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import textwrap
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable, List, Sequence

DEFAULT_PATTERNS = [
    "specs/**/*.md",
    "specs/**/*.yml",
    "specs/**/*.yaml",
    "docs/specs/**/*.md",
    ".ai/inbox/specs/**/*.md",
    ".codex/specs/**/*.md",
    "docs/business-rules/**/*.md",
    "docs/agentic-evidence/**/pr-notification.md",
    "docs/agentic-evidence/**/pm-checklist.md",
    "docs/agentic-evidence/**/qa-checklist.md",
    "docs/agentic-evidence/**/data-analysis.md",
    "docs/releases/**/*.md",
    "CHANGELOG.md",
]

IGNORE_PARTS = {
    "node_modules",
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    ".agent",
}

IGNORE_NAME_PATTERNS = [
    re.compile(r"_TEMPLATE", re.I),
    re.compile(r"\.template\.", re.I),
]


@dataclass
class ContextItem:
    path: str
    kind: str
    title: str
    headings: List[str]
    excerpt: str


def is_ignored(path: Path) -> bool:
    if any(part in IGNORE_PARTS for part in path.parts):
        return True
    return any(p.search(path.name) for p in IGNORE_NAME_PATTERNS)


def read_text(path: Path, max_chars: int) -> str:
    try:
        data = path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""
    return data[:max_chars]


def extract_title(text: str, fallback: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            return stripped.lstrip("#").strip() or fallback
        if stripped.lower().startswith("title:"):
            return stripped.split(":", 1)[1].strip().strip('"') or fallback
    return fallback


def extract_headings(text: str, limit: int = 12) -> List[str]:
    out: List[str] = []
    for line in text.splitlines():
        if line.startswith("#"):
            out.append(line.strip())
            if len(out) >= limit:
                break
    return out


def classify(path: Path) -> str:
    s = str(path).lower()
    if "business-rules" in s:
        return "business_rule"
    if "pr-notification" in s:
        return "pr_summary"
    if "pm-checklist" in s:
        return "pm_evidence"
    if "qa-checklist" in s:
        return "qa_evidence"
    if "data-analysis" in s:
        return "data_analysis"
    if "spec" in s:
        return "spec"
    if "changelog" in s or "release" in s:
        return "release_note"
    return "context"


def gather_files(root: Path, patterns: Sequence[str], max_file_chars: int) -> List[ContextItem]:
    seen: set[Path] = set()
    items: List[ContextItem] = []
    for pattern in patterns:
        for path in root.glob(pattern):
            if not path.is_file() or is_ignored(path):
                continue
            real = path.resolve()
            if real in seen:
                continue
            seen.add(real)
            text = read_text(path, max_file_chars)
            if not text.strip():
                continue
            rel = str(path.relative_to(root))
            items.append(ContextItem(
                path=rel,
                kind=classify(path),
                title=extract_title(text, path.stem),
                headings=extract_headings(text),
                excerpt=textwrap.shorten(re.sub(r"\s+", " ", text), width=max_file_chars, placeholder=" ..."),
            ))
    return items


def gh_pr_summaries(limit: int) -> List[ContextItem]:
    cmd = [
        "gh", "pr", "list",
        "--state", "all",
        "--limit", str(limit),
        "--json", "number,title,state,mergedAt,updatedAt,baseRefName,headRefName,author",
    ]
    try:
        raw = subprocess.check_output(cmd, text=True, stderr=subprocess.DEVNULL)
        prs = json.loads(raw)
    except Exception:
        return []
    items: List[ContextItem] = []
    for pr in prs:
        author = pr.get("author") or {}
        title = f"PR #{pr.get('number')}: {pr.get('title')}"
        excerpt = (
            f"State: {pr.get('state')}; base: {pr.get('baseRefName')}; "
            f"head: {pr.get('headRefName')}; author: {author.get('login')}; "
            f"mergedAt: {pr.get('mergedAt')}; updatedAt: {pr.get('updatedAt')}"
        )
        items.append(ContextItem(
            path=f"github/pr/{pr.get('number')}",
            kind="github_pr_summary",
            title=title,
            headings=[],
            excerpt=excerpt,
        ))
    return items


def group_by_kind(items: Sequence[ContextItem]) -> dict[str, List[ContextItem]]:
    grouped: dict[str, List[ContextItem]] = {}
    for item in items:
        grouped.setdefault(item.kind, []).append(item)
    return grouped


def render_markdown(items: Sequence[ContextItem], max_total_chars: int) -> str:
    grouped = group_by_kind(items)
    lines: List[str] = []
    lines.append("# Agentic Business Context Pack")
    lines.append("")
    lines.append("Generated from repository specs, PR summaries, business rules, QA/PM evidence, release notes, and optional GitHub PR metadata.")
    lines.append("")
    lines.append("## Source counts")
    lines.append("")
    for kind in sorted(grouped):
        lines.append(f"- {kind}: {len(grouped[kind])}")
    lines.append("")

    for kind in sorted(grouped):
        lines.append(f"## {kind.replace('_', ' ').title()}")
        lines.append("")
        for item in grouped[kind]:
            lines.append(f"### {item.title}")
            lines.append(f"Path: `{item.path}`")
            if item.headings:
                lines.append("")
                lines.append("Headings:")
                for heading in item.headings[:8]:
                    lines.append(f"- {heading}")
            lines.append("")
            lines.append("Excerpt:")
            lines.append("")
            lines.append(item.excerpt)
            lines.append("")
        lines.append("")
    text = "\n".join(lines).strip() + "\n"
    if len(text) > max_total_chars:
        text = text[:max_total_chars] + "\n\n[TRUNCATED: context pack exceeded max_total_chars]\n"
    return text


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build an agentic business context pack.")
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--output", default="docs/agentic-business-context/context-pack.md")
    parser.add_argument("--json-output", default="docs/agentic-business-context/context-pack.json")
    parser.add_argument("--max-file-chars", type=int, default=6000)
    parser.add_argument("--max-total-chars", type=int, default=120000)
    parser.add_argument("--include-github-prs", action="store_true")
    parser.add_argument("--github-limit", type=int, default=30)
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    items = gather_files(root, DEFAULT_PATTERNS, args.max_file_chars)
    if args.include_github_prs:
        items.extend(gh_pr_summaries(args.github_limit))

    md = render_markdown(items, args.max_total_chars)
    out = root / args.output
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(md, encoding="utf-8")

    json_out = root / args.json_output
    json_out.parent.mkdir(parents=True, exist_ok=True)
    json_out.write_text(json.dumps({"items": [asdict(i) for i in items]}, indent=2), encoding="utf-8")

    print(f"Wrote {out}")
    print(f"Wrote {json_out}")
    print(f"Context items: {len(items)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
