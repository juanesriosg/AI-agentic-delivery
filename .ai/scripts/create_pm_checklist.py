#!/usr/bin/env python3
"""Generate a PM/product acceptance checklist."""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def safe_id(text: str) -> str:
    return ''.join(c if c.isalnum() or c in ('-', '_', '.') else '-' for c in text.strip()) or 'unknown-story'


def find_business_goal(text: str) -> str:
    patterns = [r'Business goal\s*[:\-]\s*(.+)', r'Goal\s*[:\-]\s*(.+)', r'Why\s*[:\-]\s*(.+)']
    for pattern in patterns:
        m = re.search(pattern, text, re.I)
        if m:
            return m.group(1).strip()
    return 'Confirm the implementation delivers the user/business value described in the spec.'


def main() -> int:
    parser = argparse.ArgumentParser(description='Generate PM checklist from spec.')
    parser.add_argument('--story', '--story-id', dest='story_id', required=True)
    parser.add_argument('--spec', required=True)
    parser.add_argument('--out-dir', default='')
    args = parser.parse_args()

    story = safe_id(args.story_id)
    spec_path = Path(args.spec)
    text = spec_path.read_text(encoding='utf-8', errors='replace') if spec_path.exists() else args.spec
    business_goal = find_business_goal(text)
    checks = [
        ('PM-001','user_value','Does the implementation solve the stated user/business problem?','User receives the intended value.'),
        ('PM-002','intuitiveness','Can the primary user understand the main action without explanation?','Primary action and next step are obvious.'),
        ('PM-003','integration_with_app','Does the story fit the rest of the app flow and patterns?','Navigation, UI, and behavior feel consistent.'),
        ('PM-004','copy_and_language','Is the copy clear, helpful, and action-oriented?','Labels, buttons, and messages reduce confusion.'),
        ('PM-005','edge_cases','Are empty, loading, error, and success states understandable?','User is never left guessing what happened.'),
        ('PM-006','accessibility_inclusion','Is the experience accessible enough for the scope?','Basic accessibility does not block task completion.'),
        ('PM-007','product_risk','Are there tradeoffs needing human AI PM decision?','Risks are explicit and ready for human judgment.'),
    ]
    data: dict[str, Any] = {
        'story_id': story,
        'checklist_id': f'PM-{story}',
        'generated_by_agent': 'product-manager-acceptance',
        'generated_at': datetime.now(timezone.utc).isoformat(timespec='seconds'),
        'business_goal': business_goal,
        'items': [
            {
                'id': cid,
                'category': cat,
                'question': question,
                'expected_product_outcome': expected,
                'status': 'manager_decision_needed' if cid == 'PM-007' else 'not_applicable',
                'evidence': [],
                'feedback_if_failed': '',
                'owner_agent_if_failed': '',
            }
            for cid, cat, question, expected in checks
        ],
    }
    out_dir = Path(args.out_dir) if args.out_dir else Path('.agent') / 'stories' / story
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / 'pm-checklist.json').write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    md = [f'# Product Manager Checklist — {story}', '', f'- Business goal: {business_goal}', f'- Generated at: {data["generated_at"]}', '', '| ID | Question | Expected | Status | Evidence | Feedback / owner |', '|---|---|---|---|---|---|']
    for item in data['items']:
        md.append(f"| {item['id']} | {item['question']} | {item['expected_product_outcome']} | {item['status']} |  |  |")
    md += ['', '## Decision', '', 'PM decision: Pending', '']
    md_text = '\n'.join(md)
    (out_dir / 'pm-checklist.md').write_text(md_text, encoding='utf-8')
    print(md_text)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
