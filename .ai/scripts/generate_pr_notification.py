#!/usr/bin/env python3
"""Generate manager-ready PR notification from story artifacts."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def safe_id(text: str) -> str:
    return ''.join(c if c.isalnum() or c in ('-', '_', '.') else '-' for c in text.strip()) or 'unknown-story'


def read_text(path: Path, default: str = '') -> str:
    return path.read_text(encoding='utf-8', errors='replace') if path.exists() else default


def summarize_log(path: Path, limit: int = 30) -> list[str]:
    if not path.exists():
        return ['No agents.log found.']
    rows = []
    for line in path.read_text(encoding='utf-8', errors='replace').splitlines()[-limit:]:
        try:
            item = json.loads(line)
            rows.append(f"| {item.get('agent','')} | {item.get('stage','')} | {item.get('status','')} | {item.get('action','')} |")
        except Exception:
            continue
    return rows or ['No parseable log entries found.']


def main() -> int:
    parser = argparse.ArgumentParser(description='Generate PR notification for human AI PM.')
    parser.add_argument('--story', '--story-id', dest='story_id', required=True)
    parser.add_argument('--pr-url', default='')
    parser.add_argument('--source-spec', default='')
    parser.add_argument('--summary', default='')
    parser.add_argument('--risk', default='TBD')
    parser.add_argument('--rollback', default='TBD')
    parser.add_argument('--root', default='.')
    parser.add_argument('--out', default='')
    args = parser.parse_args()

    root = Path(args.root)
    story = safe_id(args.story_id)
    story_dir = root / '.agent' / 'stories' / story
    qa = 'present' if (story_dir / 'qa-checklist.md').exists() else 'missing'
    pm = 'present' if (story_dir / 'pm-checklist.md').exists() else 'missing'
    visual = 'present' if (story_dir / 'visual-evidence.md').exists() else 'missing/not required'
    log_rows = summarize_log(story_dir / 'agents.log.jsonl')
    screenshots = sorted((story_dir / 'screenshots').glob('*')) if (story_dir / 'screenshots').exists() else []
    annotations = sorted((story_dir / 'annotations').glob('*.json')) if (story_dir / 'annotations').exists() else []

    lines = [
        f'# PR Notification to Human AI PM — {story}', '',
        '## Story', '',
        f'- Story ID: {story}',
        f'- PR: {args.pr_url or "TBD"}',
        f'- Source spec: {args.source_spec or "TBD"}', '',
        '## Summary of changes', '',
        args.summary or 'TBD by implementing agent.', '',
        '## Gate status', '',
        f'- QA checklist: {qa}',
        f'- PM checklist: {pm}',
        f'- Visual evidence: {visual}',
        '- Codex PR Review Gate: required; pending until `Agentic Codex PR Review / codex_review_gate` passes.',
        '',
        '## Agents involved / iterations', '',
        '| Agent | Stage | Status | Action |', '|---|---|---|---|',
    ]
    lines.extend(log_rows)
    lines += ['', '## Screenshots', '']
    lines.extend([f'- `{p}`' for p in screenshots] or ['- No screenshots attached or not UI-related.'])
    lines += ['', '## Annotations', '']
    lines.extend([f'- `{p}`' for p in annotations] or ['- No visual annotations.'])
    lines += ['', '## Validation evidence', '', '- See QA checklist, PM checklist, visual evidence, and PR validation output.', '', '## Risk and rollback', '', f'- Risk: {args.risk}', f'- Rollback: {args.rollback}', '', '## Human AI PM requested action', '', 'Review the PR, check the evidence, and approve/request changes/decide tradeoffs.', '']
    out = Path(args.out) if args.out else story_dir / 'pr-notification.md'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text('\n'.join(lines), encoding='utf-8')
    print('\n'.join(lines))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
