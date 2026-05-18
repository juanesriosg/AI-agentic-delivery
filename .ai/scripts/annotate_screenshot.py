#!/usr/bin/env python3
"""Annotate screenshots using JSON annotations. Uses Pillow if available."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load_annotations(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding='utf-8'))
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and isinstance(data.get('annotations'), list):
        return data['annotations']
    if isinstance(data, dict):
        return [data]
    return []


def main() -> int:
    parser = argparse.ArgumentParser(description='Annotate screenshot with boxes and labels.')
    parser.add_argument('--image', required=True)
    parser.add_argument('--annotations', required=True)
    parser.add_argument('--out', required=True)
    parser.add_argument('--report', default='')
    args = parser.parse_args()

    image = Path(args.image)
    annotations_path = Path(args.annotations)
    out = Path(args.out)
    annotations = load_annotations(annotations_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    report_lines = [f'# Screenshot Annotation Report', '', f'- Image: {image}', f'- Annotations: {annotations_path}', '']
    for a in annotations:
        report_lines.append(f"- {a.get('id','ANN')}: {a.get('severity','unknown')} — {a.get('actual','')} Expected: {a.get('expected','')}")

    try:
        from PIL import Image, ImageDraw, ImageFont  # type: ignore
    except Exception:
        report = Path(args.report) if args.report else out.with_suffix('.annotation-report.md')
        report.write_text('\n'.join(report_lines) + '\n\nPillow is not installed, so no image was drawn. JSON annotations are still valid.\n', encoding='utf-8')
        print(f'Pillow unavailable. Wrote annotation report to {report}')
        return 0

    img = Image.open(image).convert('RGB')
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.load_default()
    except Exception:
        font = None
    for a in annotations:
        box = a.get('box') or {}
        if all(k in box for k in ('x','y','width','height')):
            x, y, width, height = int(box['x']), int(box['y']), int(box['width']), int(box['height'])
            draw.rectangle((x, y, x + width, y + height), outline='red', width=3)
            label = f"{a.get('id','ANN')} {a.get('severity','')}"
            draw.text((x, max(0, y - 14)), label, fill='red', font=font)
    img.save(out)
    report = Path(args.report) if args.report else out.with_suffix('.annotation-report.md')
    report.write_text('\n'.join(report_lines) + '\n', encoding='utf-8')
    print(f'Wrote annotated screenshot to {out}')
    print(f'Wrote annotation report to {report}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
