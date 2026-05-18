#!/usr/bin/env python3
"""Generate a visual QA report from screenshots and annotations."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def safe_id(text: str) -> str:
    return ''.join(c if c.isalnum() or c in ('-', '_', '.') else '-' for c in text.strip()) or 'unknown-story'


def main() -> int:
    parser = argparse.ArgumentParser(description='Generate visual QA report.')
    parser.add_argument('--story', '--story-id', dest='story_id', required=True)
    parser.add_argument('--root', default='.')
    parser.add_argument('--out', default='')
    args = parser.parse_args()

    root = Path(args.root)
    story = safe_id(args.story_id)
    story_dir = root / '.agent' / 'stories' / story
    screenshots = sorted((story_dir / 'screenshots').glob('*')) if (story_dir / 'screenshots').exists() else []
    annotations = sorted((story_dir / 'annotations').glob('*.json')) if (story_dir / 'annotations').exists() else []
    lines = [f'# Visual QA Report — {story}', '', '## Screenshots', '']
    if screenshots:
        for path in screenshots:
            lines.append(f'- `{path}`')
    else:
        lines.append('- No screenshots found. Visual evidence gap must be justified.')
    lines += ['', '## Annotations / defects', '']
    if annotations:
        for path in annotations:
            try:
                data = json.loads(path.read_text(encoding='utf-8'))
            except Exception:
                lines.append(f'- `{path}`: invalid JSON')
                continue
            items = data if isinstance(data, list) else data.get('annotations', [data]) if isinstance(data, dict) else []
            for item in items:
                lines.append(f"- `{path}` — {item.get('id','ANN')}: {item.get('severity','unknown')} — {item.get('actual','')}")
    else:
        lines.append('- No visual annotations found.')
    lines += ['', '## Decision', '', 'Visual QA decision: Pending', '']
    out = Path(args.out) if args.out else story_dir / 'visual-evidence.md'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text('\n'.join(lines), encoding='utf-8')
    print('\n'.join(lines))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
