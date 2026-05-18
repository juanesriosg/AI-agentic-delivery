#!/usr/bin/env python3
"""Create or update a v4 story lifecycle state file."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def safe_id(text: str) -> str:
    return ''.join(c if c.isalnum() or c in ('-', '_', '.') else '-' for c in text.strip()) or 'unknown-story'


def main() -> int:
    parser = argparse.ArgumentParser(description='Update .agent/stories/<story>/state.json')
    parser.add_argument('--story', '--story-id', dest='story_id', required=True)
    parser.add_argument('--state', required=True)
    parser.add_argument('--agent', required=True)
    parser.add_argument('--status', default='in_progress')
    parser.add_argument('--note', default='')
    parser.add_argument('--artifact', action='append', default=[])
    parser.add_argument('--root', default='.')
    args = parser.parse_args()

    root = Path(args.root)
    story = safe_id(args.story_id)
    path = root / '.agent' / 'stories' / story / 'state.json'
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        data: dict[str, Any] = json.loads(path.read_text(encoding='utf-8'))
    else:
        data = {'story_id': story, 'history': [], 'artifacts': []}
    entry = {
        'timestamp_utc': datetime.now(timezone.utc).isoformat(timespec='seconds'),
        'state': args.state,
        'status': args.status,
        'agent': args.agent,
        'note': args.note,
        'artifacts': args.artifact,
    }
    data['current_state'] = args.state
    data['status'] = args.status
    data['updated_by'] = args.agent
    data['updated_at_utc'] = entry['timestamp_utc']
    data.setdefault('history', []).append(entry)
    for artifact in args.artifact:
        if artifact not in data.setdefault('artifacts', []):
            data['artifacts'].append(artifact)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(data, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
