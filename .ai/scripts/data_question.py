#!/usr/bin/env python3
"""Create a data-analysis work item and prompt from a business question."""
from __future__ import annotations

import argparse
import json
import re
import textwrap
import time
from pathlib import Path
from typing import Sequence


def slugify(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9]+", "-", value.lower()).strip("-")
    return value[:80] or "data-question"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Create data question evidence scaffold.")
    parser.add_argument("--question", required=True)
    parser.add_argument("--decision", default="")
    parser.add_argument("--time-range", default="")
    parser.add_argument("--question-id", default="")
    parser.add_argument("--output-dir", default=".agent/data-analysis")
    args = parser.parse_args(argv)

    qid = args.question_id or f"DQ-{int(time.time())}-{slugify(args.question)}"
    out_dir = Path(args.output_dir) / qid
    out_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "question_id": qid,
        "question": args.question,
        "decision": args.decision,
        "time_range": args.time_range,
        "created_at_epoch": int(time.time()),
    }
    (out_dir / "question.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    md = textwrap.dedent(f"""
    # Data Question: {qid}

    ## Question

    {args.question}

    ## Decision this supports

    {args.decision or 'Not provided'}

    ## Time range

    {args.time_range or 'Not provided'}

    ## Required workflow

    1. Build business context with `.ai/scripts/build_business_context.py`.
    2. Create analysis plan.
    3. Use `.ai/scripts/safe_sql_query.py --lint-only` for every query.
    4. Execute only read-only SELECT queries.
    5. Save answer in `{out_dir / 'answer.md'}`.
    """).lstrip()
    (out_dir / "question.md").write_text(md, encoding="utf-8")
    print(out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
