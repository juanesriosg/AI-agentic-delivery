#!/usr/bin/env python3
"""Heuristic bug-risk scanner for changed or repository files.

This is not a security scanner and does not replace tests. It points agents to
areas that deserve review: destructive operations, missing timeouts, suspicious
broad exception handling, hardcoded secrets, and unbounded operations.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path
from typing import Iterable, List, Dict

PATTERNS = [
    ("critical", "destructive_operation", re.compile(r"\b(rm\s+-rf|DROP\s+TABLE|TRUNCATE\s+TABLE|git\s+reset\s+--hard|git\s+clean\s+-fdx|kubectl\s+delete|terraform\s+destroy)\b", re.I)),
    ("high", "possible_secret", re.compile(r"(?i)(api[_-]?key|secret|token|password)\s*[:=]\s*['\"][^'\"]{8,}")),
    ("medium", "broad_exception", re.compile(r"\b(except\s+Exception|catch\s*\([^)]*Exception|catch\s*\([^)]*Throwable)")),
    ("medium", "sleep_in_test_or_async", re.compile(r"\b(sleep\(|Thread\.sleep|setTimeout\(|time\.sleep)")),
    ("medium", "missing_timeout_hint", re.compile(r"\b(requests\.(get|post|put|delete)|fetch\(|axios\.|http\.get\(|http\.post\()")),
    ("low", "todo_left", re.compile(r"\b(TODO|FIXME|HACK)\b")),
]

SKIP_DIRS = {'.git', '.agent', 'node_modules', '.venv', 'venv', '__pycache__', 'target', 'build', 'dist', '.next'}
TEXT_SUFFIXES = {'.py', '.js', '.ts', '.tsx', '.jsx', '.java', '.go', '.rs', '.rb', '.php', '.cs', '.sh', '.sql', '.yml', '.yaml', '.json', '.md', '.tf'}


def changed_files() -> List[Path]:
    try:
        out = subprocess.check_output(['git', 'diff', '--name-only', 'HEAD'], text=True)
        files = [Path(x) for x in out.splitlines() if x.strip()]
        return files
    except Exception:
        return []


def iter_files(paths: Iterable[Path]) -> Iterable[Path]:
    for p in paths:
        if not p.exists():
            continue
        if p.is_dir():
            for child in p.rglob('*'):
                if child.is_file() and child.suffix in TEXT_SUFFIXES and not any(part in SKIP_DIRS for part in child.parts):
                    yield child
        elif p.is_file() and p.suffix in TEXT_SUFFIXES and not any(part in SKIP_DIRS for part in p.parts):
            yield p


def scan_file(path: Path) -> List[Dict[str, object]]:
    try:
        text = path.read_text(encoding='utf-8')
    except Exception:
        try:
            text = path.read_text(errors='replace')
        except Exception:
            return []
    findings = []
    for idx, line in enumerate(text.splitlines(), 1):
        for severity, kind, pattern in PATTERNS:
            if pattern.search(line):
                findings.append({
                    'severity': severity,
                    'kind': kind,
                    'file': str(path),
                    'line': idx,
                    'snippet': line.strip()[:220],
                })
    return findings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--paths', nargs='*', help='Paths to scan. Defaults to changed files, or repo root if none.')
    parser.add_argument('--format', choices=['markdown', 'json'], default='markdown')
    args = parser.parse_args()

    paths = [Path(p) for p in args.paths] if args.paths else changed_files()
    if not paths:
        paths = [Path('.')]

    findings: List[Dict[str, object]] = []
    for file in iter_files(paths):
        findings.extend(scan_file(file))

    if args.format == 'json':
        print(json.dumps({'findings': findings}, indent=2))
        return 0

    print('# Agent Bug-Risk Scan')
    print('')
    if not findings:
        print('No heuristic bug-risk findings detected.')
        return 0
    print('| Severity | Kind | Location | Snippet |')
    print('|---|---|---|---|')
    for f in findings:
        snippet = str(f['snippet']).replace('|', '\\|')
        print(f"| {f['severity']} | {f['kind']} | {f['file']}:{f['line']} | `{snippet}` |")
    print('')
    print('Review these findings. They may be false positives, but each should be considered during self-review.')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
