#!/usr/bin/env python3
"""Validate story/task gates using artifact presence, open feedback, and status text."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def safe_id(text: str) -> str:
    return ''.join(c if c.isalnum() or c in ('-', '_', '.') else '-' for c in text.strip()) or 'unknown-story'


REQUIRED = {
    'task_done': ['test-matrix.md', 'qa-checklist.md'],
    'story_done': ['qa-checklist.md', 'pm-checklist.md', 'pr-notification.md'],
    'release_readiness': ['qa-checklist.md', 'pm-checklist.md', 'release-readiness.md', 'pr-notification.md'],
}

PASS_WORDS = ('pass', 'passed', 'approved', 'ok', 'accepted', 'completed')
BAD_WORDS = ('pending_agent_verification', 'pending', 'blocked', 'fail', 'failed')
STATUS_PREFIXES = ('status:', 'qa decision:', 'pm decision:', 'decision:')


def has_open_blocking_feedback(story_dir: Path) -> list[str]:
    out: list[str] = []
    for path in (story_dir / 'feedback').glob('FB-*.json'):
        try:
            item = json.loads(path.read_text(encoding='utf-8'))
        except Exception:
            out.append(f'{path}: invalid json')
            continue
        if item.get('blocking') and item.get('status', 'open') != 'closed':
            out.append(str(path))
    return out


def gate_status_failures(story_dir: Path, required_files: list[str]) -> list[str]:
    failures: list[str] = []
    for name in required_files:
        if name not in {'qa-checklist.md', 'pm-checklist.md', 'release-readiness.md'}:
            continue
        path = story_dir / name
        if not path.exists():
            continue
        text = path.read_text(encoding='utf-8', errors='replace').lower()
        status_lines = [line.strip() for line in text.splitlines() if line.strip().startswith(STATUS_PREFIXES)]
        if not status_lines:
            failures.append(f'{name}: missing status/decision line')
            continue
        joined = '\n'.join(status_lines)
        if any(word in joined for word in BAD_WORDS):
            failures.append(f'{name}: status/decision is not passing')
        if not any(word in joined for word in PASS_WORDS):
            failures.append(f'{name}: status/decision must clearly say pass/approved')
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description='Validate v4/v7 stage gate artifacts.')
    parser.add_argument('--story', '--story-id', dest='story_id', required=True)
    parser.add_argument('--gate', required=True, choices=sorted(REQUIRED))
    parser.add_argument('--root', default='.')
    parser.add_argument('--non-strict', action='store_true')
    args = parser.parse_args()

    story = safe_id(args.story_id)
    root = Path(args.root)
    story_dir = root / '.agent' / 'stories' / story
    missing = [name for name in REQUIRED[args.gate] if not (story_dir / name).exists()]
    if not (root / '.agent' / 'agents.log.jsonl').exists() and not (story_dir / 'agents.log.jsonl').exists():
        missing.append('agents.log.jsonl')
    open_feedback = has_open_blocking_feedback(story_dir)
    status_failures = gate_status_failures(story_dir, REQUIRED[args.gate])
    result = {
        'story_id': story,
        'gate': args.gate,
        'passed': not missing and not open_feedback and not status_failures,
        'missing_artifacts': missing,
        'open_blocking_feedback': open_feedback,
        'status_failures': status_failures,
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))
    if result['passed'] or args.non_strict:
        return 0
    return 1


if __name__ == '__main__':
    raise SystemExit(main())
