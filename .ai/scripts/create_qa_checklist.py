#!/usr/bin/env python3
"""Generate a story-specific QA checklist from a spec."""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def safe_id(text: str) -> str:
    return ''.join(c if c.isalnum() or c in ('-', '_', '.') else '-' for c in text.strip()) or 'unknown-story'


def extract_acceptance_criteria(text: str) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    for line in text.splitlines():
        raw = line.strip()
        m = re.match(r'^(?:[-*]\s*)?(AC[-_ ]?\d+|Acceptance\s*Criterion\s*\d+)[:.)\-\s]+(.+)$', raw, re.I)
        if m:
            items.append({'id': m.group(1).replace(' ', '-').upper(), 'text': m.group(2).strip()})
    if not items:
        # Fall back to checkbox or bullet lines that look testable.
        for i, line in enumerate(text.splitlines(), 1):
            raw = line.strip()
            if raw.startswith(('-', '*', '- [ ]', '- [x]')) and any(word in raw.lower() for word in ['user', 'system', 'form', 'button', 'api', 'must', 'should', 'can']):
                items.append({'id': f'AC-{len(items)+1:03d}', 'text': raw.lstrip('-* [x]').strip()})
    return items or [{'id': 'AC-001', 'text': 'Primary story behavior from the spec is satisfied.'}]


def item(item_id: str, category: str, description: str, expected: str, method: str, ac: str = '') -> dict[str, Any]:
    return {
        'id': item_id,
        'category': category,
        'description': description,
        'acceptance_criteria': [ac] if ac else [],
        'method': method,
        'expected_result': expected,
        'status': 'not_tested_gap_documented',
        'evidence': [],
        'blocking': True,
        'owner_agent_if_failed': '',
    }


def render_md(data: dict[str, Any]) -> str:
    lines = [f"# QA Checklist — {data['story_id']}", '', f"- Source spec: {data.get('source_spec','')}", f"- Generated at: {data['generated_at']}", '']
    for category in sorted({x['category'] for x in data['items']}):
        lines += [f'## {category.replace("_", " ").title()}', '', '| ID | Check | Expected | Method | Status | Evidence | Owner if failed |', '|---|---|---|---|---|---|---|']
        for x in [i for i in data['items'] if i['category'] == category]:
            lines.append(f"| {x['id']} | {x['description']} | {x['expected_result']} | {x['method']} | {x['status']} |  | {x['owner_agent_if_failed']} |")
        lines.append('')
    lines += ['## Decision', '', 'QA decision: Pending', '']
    return '\n'.join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description='Generate QA checklist from spec.')
    parser.add_argument('--story', '--story-id', dest='story_id', required=True)
    parser.add_argument('--spec', required=True)
    parser.add_argument('--out-dir', default='')
    args = parser.parse_args()

    story = safe_id(args.story_id)
    spec_path = Path(args.spec)
    text = spec_path.read_text(encoding='utf-8', errors='replace') if spec_path.exists() else args.spec
    acs = extract_acceptance_criteria(text)
    items: list[dict[str, Any]] = []
    for ac in acs:
        items.append(item(f"QA-FUNC-{len(items)+1:03d}", 'functionality', f"Validate {ac['id']}: {ac['text']}", 'Acceptance criterion is satisfied.', 'unit/component/integration/e2e/manual as appropriate', ac['id']))
    lower = text.lower()
    if any(k in lower for k in ['form', 'input', 'button', 'page', 'ui', 'frontend', 'screen', 'placeholder']):
        items += [
            item('QA-VIS-001','style_visual','Layout has no overlap, clipping, or broken spacing.','UI is visually correct in relevant states and viewports.','visual screenshot review'),
            item('QA-VIS-002','style_visual','Labels, placeholders, and validation messages behave correctly.','Form text never overlaps containers and remains readable.','visual screenshot review'),
            item('QA-A11Y-001','accessibility','Inputs and controls have labels/accessibility names.','Keyboard and assistive users can understand controls.','manual/tool inspection'),
            item('QA-RESP-001','responsive','Mobile and desktop layouts remain usable.','Primary flow works at minimum mobile and desktop viewports.','visual/manual/e2e'),
        ]
    if any(k in lower for k in ['api', 'endpoint', 'backend', 'service', 'database', 'integration']):
        items += [
            item('QA-INT-001','integration','Frontend/backend or service contract matches.','Data and errors match documented contract.','contract/integration test'),
            item('QA-INT-002','integration','Dependency failure is handled safely.','User/service receives clear error or retry behavior.','integration/manual'),
        ]
    items.append(item('QA-REG-001','regression','Important adjacent existing behavior still works.','No obvious regression in related flow.','focused regression test/manual'))

    data = {
        'story_id': story,
        'checklist_id': f'QA-{story}',
        'generated_by_agent': 'qa-checklist-engineer',
        'generated_at': datetime.now(timezone.utc).isoformat(timespec='seconds'),
        'source_spec': str(spec_path),
        'items': items,
    }
    out_dir = Path(args.out_dir) if args.out_dir else Path('.agent') / 'stories' / story
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / 'qa-checklist.json').write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    (out_dir / 'qa-checklist.md').write_text(render_md(data), encoding='utf-8')
    print(render_md(data))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
