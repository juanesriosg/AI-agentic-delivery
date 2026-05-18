#!/usr/bin/env python3
"""Create and track feedback between agents."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def safe_id(text: str) -> str:
    return ''.join(c if c.isalnum() or c in ('-', '_', '.') else '-' for c in text.strip()) or 'unknown'


def next_feedback_id(story_dir: Path) -> str:
    feedback_dir = story_dir / 'feedback'
    feedback_dir.mkdir(parents=True, exist_ok=True)
    existing = sorted(feedback_dir.glob('FB-*.json'))
    return f"FB-{len(existing)+1:03d}"


def append_jsonl(path: Path, item: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('a', encoding='utf-8') as f:
        f.write(json.dumps(item, ensure_ascii=False, sort_keys=True) + '\n')


def main() -> int:
    parser = argparse.ArgumentParser(description='Create agent-to-agent feedback.')
    parser.add_argument('--from-agent', required=True)
    parser.add_argument('--to-agent', '--recommended-owner-agent', dest='to_agent', required=True)
    parser.add_argument('--story', '--story-id', dest='story_id', required=True)
    parser.add_argument('--stage', default='feedback')
    parser.add_argument('--severity', required=True, choices=['low','medium','high','critical'])
    parser.add_argument('--summary', required=True)
    parser.add_argument('--expected', default='')
    parser.add_argument('--actual', default='')
    parser.add_argument('--suggested-fix', default='')
    parser.add_argument('--verification-required', default='')
    parser.add_argument('--blocking', default='true', choices=['true','false'])
    parser.add_argument('--evidence', action='append', default=[])
    parser.add_argument('--feedback-id', default='')
    parser.add_argument('--root', default='.')
    args = parser.parse_args()

    root = Path(args.root)
    story = safe_id(args.story_id)
    story_dir = root / '.agent' / 'stories' / story
    feedback_id = args.feedback_id or next_feedback_id(story_dir)
    item: dict[str, Any] = {
        'feedback_id': feedback_id,
        'timestamp_utc': datetime.now(timezone.utc).isoformat(timespec='seconds'),
        'story_id': story,
        'from_agent': args.from_agent,
        'recommended_owner_agent': args.to_agent,
        'severity': args.severity,
        'stage': args.stage,
        'blocking': args.blocking == 'true',
        'summary': args.summary,
        'expected': args.expected,
        'actual': args.actual,
        'suggested_fix': args.suggested_fix,
        'verification_required': args.verification_required,
        'evidence': args.evidence,
        'status': 'open',
    }
    feedback_path = story_dir / 'feedback' / f'{feedback_id}.json'
    feedback_path.parent.mkdir(parents=True, exist_ok=True)
    feedback_path.write_text(json.dumps(item, ensure_ascii=False, indent=2), encoding='utf-8')
    append_jsonl(root / '.agent' / 'feedback.jsonl', item)

    log_script = root / '.ai' / 'scripts' / 'agent_log.py'
    if log_script.exists():
        subprocess.run([
            os.environ.get('PYTHON', 'python'), str(log_script),
            '--agent', args.from_agent,
            '--story', story,
            '--stage', args.stage,
            '--action', f'Created feedback {feedback_id}: {args.summary}',
            '--status', 'feedback_created',
            '--evidence', str(feedback_path),
            '--risk', args.severity if args.severity in ('low','medium','high','critical') else 'medium',
            '--next-agent', args.to_agent,
            '--next-action', args.verification_required or 'Review and fix feedback',
            '--root', str(root),
        ], check=False)

    print(json.dumps(item, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
