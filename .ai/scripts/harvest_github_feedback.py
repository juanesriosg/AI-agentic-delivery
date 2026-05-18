#!/usr/bin/env python3
"""Harvest GitHub PR/issue feedback into the agent feedback store.

Requires GitHub CLI (`gh`) authenticated with read access. The script is best-effort
and never fails the workflow when GitHub data is unavailable unless --strict is used.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

ISO = "%Y-%m-%dT%H:%M:%SZ"
KEYWORDS = [
    "agent", "codex", "qa", "pm", "test", "spec", "evidence", "review", "bug", "failure",
    "missing", "incorrect", "confusing", "too long", "too broad", "unsafe", "rollback", "screenshot",
]


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime(ISO)


def run_gh(args: List[str]) -> Optional[Any]:
    if not shutil.which("gh"):
        return None
    proc = subprocess.run(["gh", *args], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if proc.returncode != 0:
        return None
    try:
        return json.loads(proc.stdout or "null")
    except json.JSONDecodeError:
        return None


def event_id(payload: Dict[str, Any]) -> str:
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return "ghfb-" + hashlib.sha256(raw).hexdigest()[:12]


def is_signal(text: str) -> bool:
    lower = text.lower()
    return any(k in lower for k in KEYWORDS)


def classify(text: str) -> str:
    lower = text.lower()
    if "codex" in lower:
        return "codex_review_failure"
    if "qa" in lower:
        return "qa_failure"
    if "pm" in lower or "product" in lower:
        return "pm_failure"
    if "test" in lower or "ci" in lower:
        return "ci_failure"
    if "spec" in lower or "requirement" in lower:
        return "spec_gap"
    if "security" in lower or "unsafe" in lower:
        return "security_finding"
    return "manager_comment"


def severity(text: str) -> str:
    lower = text.lower()
    if any(x in lower for x in ["critical", "p0", "security", "secret", "data loss"]):
        return "critical"
    if any(x in lower for x in ["block", "p1", "must", "unsafe", "fail"]):
        return "high"
    if any(x in lower for x in ["should", "missing", "incorrect", "confusing"]):
        return "medium"
    return "low"


def to_event(pr: Dict[str, Any], source: str, body: str, author: str, url: str) -> Dict[str, Any]:
    summary = re.sub(r"\s+", " ", body).strip()[:240]
    payload = {
        "schema": "agentic.feedback_event.v1",
        "created_at": now(),
        "source": source,
        "signal_type": classify(body),
        "target_agent": "unknown",
        "target_skill": "unknown",
        "task_id": pr.get("headRefName") or "unknown",
        "spec_id": "unknown",
        "severity": severity(body),
        "summary": summary or f"Feedback on PR {pr.get('number')}",
        "rationale": "Harvested from GitHub PR/issue feedback. Human or Codex comment may need clustering before policy changes.",
        "accepted": "unresolved",
        "evidence": [url or pr.get("url", "")],
        "suggested_improvement": "Infer whether a skill/eval/routing update would prevent this issue in future.",
        "github": {
            "pr_number": pr.get("number"),
            "pr_title": pr.get("title"),
            "author": author,
            "url": url or pr.get("url"),
        },
    }
    payload["event_id"] = event_id(payload)
    return payload


def append_jsonl(path: Path, events: Iterable[Dict[str, Any]]) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    existing = set()
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            try:
                existing.add(json.loads(line).get("event_id"))
            except Exception:
                pass
    with path.open("a", encoding="utf-8") as fh:
        for event in events:
            if event.get("event_id") in existing:
                continue
            fh.write(json.dumps(event, sort_keys=True, ensure_ascii=False) + "\n")
            count += 1
    return count


def main() -> int:
    p = argparse.ArgumentParser(description="Harvest GitHub feedback into .agent/feedback/feedback.jsonl")
    p.add_argument("--limit", type=int, default=30)
    p.add_argument("--output", default=".agent/feedback/feedback.jsonl")
    p.add_argument("--strict", action="store_true")
    args = p.parse_args()

    prs = run_gh(["pr", "list", "--state", "all", "--limit", str(args.limit), "--json", "number,title,url,headRefName,updatedAt,labels"])
    if prs is None:
        msg = "GitHub CLI unavailable or not authenticated; skipping GitHub feedback harvest."
        print(msg)
        return 1 if args.strict else 0

    events: List[Dict[str, Any]] = []
    for pr in prs:
        number = str(pr.get("number"))
        detail = run_gh(["pr", "view", number, "--json", "number,title,url,headRefName,comments,reviews"])
        if not detail:
            continue
        pr.update(detail)
        for comment in detail.get("comments") or []:
            body = comment.get("body") or ""
            if is_signal(body):
                events.append(to_event(pr, "github_pr_comment", body, (comment.get("author") or {}).get("login", "unknown"), comment.get("url", pr.get("url", ""))))
        for review in detail.get("reviews") or []:
            body = review.get("body") or ""
            state = review.get("state") or ""
            if body and (is_signal(body) or state.upper() in {"CHANGES_REQUESTED", "DISMISSED"}):
                events.append(to_event(pr, "github_pr_review", body, (review.get("author") or {}).get("login", "unknown"), pr.get("url", "")))

    count = append_jsonl(Path(args.output), events)
    print(json.dumps({"harvested": count, "candidates": len(events), "output": args.output}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
