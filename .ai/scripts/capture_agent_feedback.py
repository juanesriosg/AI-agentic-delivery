#!/usr/bin/env python3
"""Capture structured feedback for the agent self-improvement loop.

The script is intentionally dependency-free. It writes JSONL feedback events to
.agent/feedback/feedback.jsonl by default and can also emit a committed Markdown
record under docs/agentic-feedback/ when --commit-ready is used.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
from pathlib import Path
from typing import Any, Dict, List

ISO = "%Y-%m-%dT%H:%M:%SZ"
VALID_SEVERITIES = {"low", "medium", "high", "critical"}
VALID_ACCEPTED = {"true", "false", "unresolved"}


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime(ISO)


def slug(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9_.-]+", "-", value.strip().lower()).strip("-._")
    return value[:80] or "feedback"


def event_id(payload: Dict[str, Any]) -> str:
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return "fb-" + hashlib.sha256(raw).hexdigest()[:12]


def append_jsonl(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(payload, sort_keys=True, ensure_ascii=False) + "\n")


def markdown(payload: Dict[str, Any]) -> str:
    evidence = payload.get("evidence") or []
    evidence_md = "\n".join(f"- {item}" for item in evidence) if evidence else "- none provided"
    return f"""# Agent feedback: {payload['event_id']}

## Summary
{payload['summary']}

## Rationale
{payload['rationale']}

## Classification

| Field | Value |
|---|---|
| Created at | {payload['created_at']} |
| Source | {payload['source']} |
| Signal type | {payload['signal_type']} |
| Severity | {payload['severity']} |
| Accepted | {payload['accepted']} |
| Target agent | {payload.get('target_agent') or 'unknown'} |
| Target skill | {payload.get('target_skill') or 'unknown'} |
| Task ID | {payload.get('task_id') or 'unknown'} |
| Spec ID | {payload.get('spec_id') or 'unknown'} |

## Evidence
{evidence_md}

## Suggested improvement
{payload.get('suggested_improvement') or 'Not specified.'}
"""


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Capture structured agent feedback.")
    p.add_argument("--source", required=True, help="Where feedback came from: manager_review, qa, pm, codex_review, ci, issue, etc.")
    p.add_argument("--signal-type", default="manager_comment")
    p.add_argument("--target-agent", default="unknown")
    p.add_argument("--target-skill", default="unknown")
    p.add_argument("--task-id", default="unknown")
    p.add_argument("--spec-id", default="unknown")
    p.add_argument("--severity", default="medium", choices=sorted(VALID_SEVERITIES))
    p.add_argument("--summary", required=True)
    p.add_argument("--rationale", required=True)
    p.add_argument("--accepted", default="unresolved", choices=sorted(VALID_ACCEPTED))
    p.add_argument("--evidence", action="append", default=[])
    p.add_argument("--suggested-improvement", default="")
    p.add_argument("--jsonl", default=".agent/feedback/feedback.jsonl")
    p.add_argument("--commit-ready", action="store_true", help="Also write Markdown under docs/agentic-feedback/ for reviewable feedback.")
    p.add_argument("--markdown-dir", default="docs/agentic-feedback/events")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    base: Dict[str, Any] = {
        "schema": "agentic.feedback_event.v1",
        "created_at": now(),
        "source": args.source,
        "signal_type": args.signal_type,
        "target_agent": args.target_agent,
        "target_skill": args.target_skill,
        "task_id": args.task_id,
        "spec_id": args.spec_id,
        "severity": args.severity,
        "summary": args.summary.strip(),
        "rationale": args.rationale.strip(),
        "accepted": args.accepted,
        "evidence": args.evidence,
        "suggested_improvement": args.suggested_improvement.strip(),
    }
    base["event_id"] = event_id(base)
    append_jsonl(Path(args.jsonl), base)
    if args.commit_ready:
        out = Path(args.markdown_dir) / f"{base['event_id']}-{slug(args.summary)}.md"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(markdown(base), encoding="utf-8")
    print(json.dumps(base, indent=2, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
