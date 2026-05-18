#!/usr/bin/env python3
"""Dispatch detected spec files as agent tasks.

Outputs task markdown files and optionally creates GitHub issues and/or posts to a webhook.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import urllib.request
from pathlib import Path
from typing import Any, Dict, List

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
from spec_to_agent_task import render_markdown, render_payload  # noqa: E402


def run(cmd: List[str], env: Dict[str, str] | None = None) -> int:
    print("+ " + " ".join(cmd))
    return subprocess.call(cmd, env=env)


def ensure_labels(labels: List[str]) -> None:
    for label in labels:
        subprocess.call(["gh", "label", "create", label, "--color", "5319e7", "--description", "AI agent workflow label"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def create_issue(title: str, body_file: Path, labels: List[str]) -> None:
    ensure_labels(labels)
    cmd = ["gh", "issue", "create", "--title", title, "--body-file", str(body_file)]
    for label in labels:
        cmd += ["--label", label]
    rc = run(cmd)
    if rc != 0:
        raise SystemExit(f"gh issue create failed for {body_file}")


def post_webhook(url: str, payload: Dict[str, Any]) -> None:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=30) as response:  # nosec - user-configured internal URL
        print(f"Webhook status: {response.status}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--detected", default=".agent/reports/detected-specs.json")
    parser.add_argument("--out-dir", default=".agent/dispatch")
    parser.add_argument("--create-issues", action="store_true")
    parser.add_argument("--webhook-env", default="AGENT_DISPATCH_WEBHOOK_URL")
    parser.add_argument("--labels", default="ai:ready,ai:from-spec")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    detected_path = Path(args.detected)
    if not detected_path.exists():
        raise SystemExit(f"Detected spec report not found: {detected_path}")

    detected = json.loads(detected_path.read_text(encoding="utf-8"))
    specs = detected.get("specs", [])
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    labels = [label.strip() for label in args.labels.split(",") if label.strip()]
    webhook_url = os.environ.get(args.webhook_env, "").strip()

    summary: List[Dict[str, Any]] = []
    for item in specs:
        spec_path = Path(item["path"])
        if not spec_path.exists():
            summary.append({"spec_path": str(spec_path), "status": "skipped", "reason": "file does not exist"})
            continue

        payload = render_payload(
            spec_path=spec_path,
            branch=detected.get("branch", os.environ.get("GITHUB_REF_NAME", "unknown")),
            sha=detected.get("head_sha", os.environ.get("GITHUB_SHA", "unknown")),
            repo=detected.get("repository", os.environ.get("GITHUB_REPOSITORY", "local")),
        )
        task_body = render_markdown(payload)
        safe_name = payload["implementation_branch"].replace("/", "-")
        body_file = out_dir / f"{safe_name}.md"
        json_file = out_dir / f"{safe_name}.json"
        body_file.write_text(task_body, encoding="utf-8")
        json_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")

        issue_title = f"AI implementation from spec: {payload['title']}"
        if args.create_issues and not args.dry_run:
            create_issue(issue_title, body_file, labels)
        if webhook_url and not args.dry_run:
            post_webhook(webhook_url, payload)

        summary.append({
            "spec_path": str(spec_path),
            "title": payload["title"],
            "implementation_branch": payload["implementation_branch"],
            "task_file": str(body_file),
            "issue_created": bool(args.create_issues and not args.dry_run),
            "webhook_sent": bool(webhook_url and not args.dry_run),
        })

    summary_file = out_dir / "summary.json"
    summary_file.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
