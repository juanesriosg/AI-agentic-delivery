#!/usr/bin/env python3
"""Append-only agent activity logging for the v4 agentic SDLC."""
from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def csv_list(values: list[str] | None) -> list[str]:
    if not values:
        return []
    out: list[str] = []
    for value in values:
        for item in value.split(','):
            item = item.strip()
            if item:
                out.append(item)
    return out


def safe_story_id(story: str) -> str:
    return ''.join(c if c.isalnum() or c in ('-', '_', '.') else '-' for c in story.strip()) or 'unknown-story'


def append_jsonl(path: Path, item: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('a', encoding='utf-8') as f:
        f.write(json.dumps(item, ensure_ascii=False, sort_keys=True) + '\n')


def append_markdown(path: Path, item: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text('# Agents Log\n\n| Time UTC | Story | Agent | Stage | Status | Action | Evidence | Notes |\n|---|---|---|---|---|---|---|---|\n', encoding='utf-8')
    evidence = ', '.join(item.get('evidence_refs', []))
    notes = (item.get('notes') or '').replace('\n', ' ')
    action = (item.get('action') or '').replace('\n', ' ')
    with path.open('a', encoding='utf-8') as f:
        f.write(f"| {item['timestamp_utc']} | {item['story_id']} | {item['agent']} | {item['stage']} | {item['status']} | {action} | {evidence} | {notes} |\n")


def main() -> int:
    parser = argparse.ArgumentParser(description='Append an agent activity entry to .agent logs.')
    parser.add_argument('--agent', required=True)
    parser.add_argument('--story', '--story-id', dest='story_id', required=True)
    parser.add_argument('--stage', required=True)
    parser.add_argument('--action', required=True)
    parser.add_argument('--status', required=True, choices=['started','in_progress','completed','passed','failed','blocked','feedback_created','feedback_closed','deferred','escalated'])
    parser.add_argument('--iteration', default=os.environ.get('AGENT_ITERATION', '1'))
    parser.add_argument('--input', dest='input_refs', action='append', help='Input refs, comma-separated or repeated.')
    parser.add_argument('--output', dest='output_refs', action='append', help='Output refs, comma-separated or repeated.')
    parser.add_argument('--evidence', dest='evidence_refs', action='append', help='Evidence refs, comma-separated or repeated.')
    parser.add_argument('--feedback', dest='feedback_refs', action='append', help='Feedback refs, comma-separated or repeated.')
    parser.add_argument('--notes', default='')
    parser.add_argument('--risk', default='none', choices=['none','low','medium','high','critical'])
    parser.add_argument('--next-agent', default='')
    parser.add_argument('--next-action', default='')
    parser.add_argument('--root', default='.', help='Repository root. Default: current directory.')
    args = parser.parse_args()

    root = Path(args.root)
    story = safe_story_id(args.story_id)
    item: dict[str, Any] = {
        'timestamp_utc': datetime.now(timezone.utc).isoformat(timespec='seconds'),
        'agent': args.agent,
        'story_id': story,
        'stage': args.stage,
        'action': args.action,
        'status': args.status,
        'iteration': args.iteration,
        'input_refs': csv_list(args.input_refs),
        'output_refs': csv_list(args.output_refs),
        'evidence_refs': csv_list(args.evidence_refs),
        'feedback_refs': csv_list(args.feedback_refs),
        'notes': args.notes,
        'risk': args.risk,
        'next_agent': args.next_agent,
        'next_action': args.next_action,
    }

    append_jsonl(root / '.agent' / 'agents.log.jsonl', item)
    append_markdown(root / '.agent' / 'reports' / 'agents.log.md', item)
    append_jsonl(root / '.agent' / 'stories' / story / 'agents.log.jsonl', item)
    append_markdown(root / '.agent' / 'stories' / story / 'agents.log.md', item)
    print(json.dumps(item, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
