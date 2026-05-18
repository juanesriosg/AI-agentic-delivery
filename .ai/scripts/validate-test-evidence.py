#!/usr/bin/env python3
"""Validate that PR/test evidence text contains minimum manager-facing sections."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

REQUIRED_PHRASES = {
    'acceptance criteria': ['acceptance criteria', 'ac-'],
    'validation': ['validation', 'test', 'command'],
    'risk': ['risk'],
    'rollback': ['rollback'],
    'bugs': ['bug', 'known gap', 'issue'],
    'qa': ['qa', 'manual verification', 'handoff'],
}


def check(text: str):
    low = text.lower()
    result = {}
    for section, words in REQUIRED_PHRASES.items():
        result[section] = any(w in low for w in words)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', required=True, help='PR body, QA handoff, or validation evidence file')
    parser.add_argument('--format', choices=['markdown', 'json'], default='markdown')
    args = parser.parse_args()
    path = Path(args.file)
    text = path.read_text(encoding='utf-8', errors='replace')
    result = check(text)
    missing = [k for k, v in result.items() if not v]
    payload = {'file': str(path), 'sections_detected': result, 'missing': missing, 'pass': not missing}
    if args.format == 'json':
        print(json.dumps(payload, indent=2))
    else:
        print('# Test Evidence Validation')
        print('')
        for k, v in result.items():
            print(f'- {k}: {"yes" if v else "no"}')
        print('')
        if missing:
            print('Missing sections: ' + ', '.join(missing))
        else:
            print('All required evidence sections detected.')
    return 0 if not missing else 2

if __name__ == '__main__':
    raise SystemExit(main())
