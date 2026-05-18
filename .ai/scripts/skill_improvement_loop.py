#!/usr/bin/env python3
"""Self-improvement orchestration for agent skills.

The script can harvest feedback, prepare a feedback bundle, run deterministic
evals, and create a proposal scaffold. When Codex is available and not dry-run,
it can be used to propose a minimal skill diff. The script never merges changes.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import shutil
import subprocess
import sys
import textwrap
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

ISO = "%Y-%m-%dT%H:%M:%SZ"
CONFIG = Path(".ai/automation/agentic.config.json")
FEEDBACK_JSONL = Path(".agent/feedback/feedback.jsonl")
OUT_DIR = Path("docs/agentic-self-improvement")


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime(ISO)


def run(cmd: List[str], check: bool = True, input_text: Optional[str] = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, text=True, input=input_text, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=check)


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def read_feedback(path: Path = FEEDBACK_JSONL) -> List[Dict[str, Any]]:
    events: List[Dict[str, Any]] = []
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    # Also read committed markdown feedback files as weak signals.
    for md in Path("docs/agentic-feedback").glob("**/*.md"):
        if md.name.lower() == "readme.md":
            continue
        text = md.read_text(encoding="utf-8")[:4000]
        events.append({
            "schema": "agentic.feedback_event.v1",
            "event_id": "md-" + re.sub(r"[^a-zA-Z0-9]+", "-", str(md))[-80:],
            "created_at": now(),
            "source": "committed_markdown_feedback",
            "signal_type": "process_gap",
            "target_agent": "unknown",
            "target_skill": "unknown",
            "severity": "medium",
            "summary": text.splitlines()[0].lstrip("# ") if text.splitlines() else str(md),
            "rationale": "Committed feedback artifact.",
            "accepted": "unresolved",
            "evidence": [str(md)],
            "suggested_improvement": "Review feedback artifact for possible skill improvement.",
        })
    return events


def cluster(events: List[Dict[str, Any]]) -> Dict[str, Any]:
    by_skill = Counter(e.get("target_skill") or "unknown" for e in events)
    by_agent = Counter(e.get("target_agent") or "unknown" for e in events)
    by_type = Counter(e.get("signal_type") or "unknown" for e in events)
    by_severity = Counter(e.get("severity") or "unknown" for e in events)
    suggestions = [e for e in events if e.get("suggested_improvement")]
    top_target = by_skill.most_common(1)[0][0] if by_skill else "unknown"
    return {
        "total_events": len(events),
        "by_skill": dict(by_skill),
        "by_agent": dict(by_agent),
        "by_type": dict(by_type),
        "by_severity": dict(by_severity),
        "top_target_skill": top_target,
        "suggestions": suggestions[:20],
    }


def write_bundle(events: List[Dict[str, Any]], summary: Dict[str, Any]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "feedback-bundle.json").write_text(json.dumps({
        "schema": "agentic.feedback_bundle.v1",
        "created_at": now(),
        "summary": summary,
        "events": events,
    }, indent=2, sort_keys=True, ensure_ascii=False), encoding="utf-8")


def proposal_id(summary: Dict[str, Any]) -> str:
    target = summary.get("top_target_skill") or "unknown"
    target = re.sub(r"[^a-zA-Z0-9]+", "-", target).strip("-").lower()[:48]
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%d%H%M")
    return f"sip-{stamp}-{target or 'general'}"


def deterministic_proposal(events: List[Dict[str, Any]], summary: Dict[str, Any]) -> str:
    pid = proposal_id(summary)
    top_skill = summary.get("top_target_skill") or "unknown"
    event_lines = []
    for e in events[:10]:
        event_lines.append(f"- `{e.get('event_id', 'unknown')}` [{e.get('severity','?')}] {e.get('summary','').strip()}")
    suggestions = [e.get("suggested_improvement") for e in events if e.get("suggested_improvement")]
    suggestion_text = "\n".join(f"- {s}" for s in suggestions[:8]) or "- No direct suggestion; infer the missing principle from feedback."
    return f"""# Self-improvement proposal: {pid}

## Status
Draft. Requires Codex/local agent improvement pass, deterministic evals, Codex PR review, and human manager approval.

## Objective
Improve future agent behavior by updating the smallest relevant skill, example, eval, script, or routing rule.

## Target skill / area
`{top_skill}`

## Evidence summary

Total feedback events: {summary.get('total_events', 0)}

Top signal types: `{summary.get('by_type', {})}`

Representative feedback:

{chr(10).join(event_lines) if event_lines else '- No feedback events found. This proposal should not be merged until evidence exists.'}

## Suggested improvement themes

{suggestion_text}

## Proposed minimal change
To be completed by the Skill Improver Agent. Prefer one narrow update plus an eval case.

## Expected improvement
Future agents should make fewer repeated mistakes in the target area while preserving safety and reviewability.

## Risk assessment
Medium until the exact diff is completed and evals pass.

## Evals to add or update
Add or update at least one eval case under `.ai/evals/**` that would have caught the repeated failure.

## Rollback plan
Revert this PR. Skill files are versioned and no model weights are changed.
"""


def run_evals() -> int:
    cmd = [sys.executable, ".ai/scripts/skill_eval_runner.py", "--all"]
    proc = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(proc.stdout)
    return proc.returncode


def codex_prompt(proposal_path: Path) -> str:
    return f"""
You are the Skill Improver Agent.

Read:
- AGENTS.md
- .ai/docs/reference/SELF_IMPROVEMENT_V15.md
- .ai/skills/self-improvement-loop.skill.md
- .ai/specs/self-improvement-policy.yml
- {proposal_path}
- docs/agentic-self-improvement/feedback-bundle.json

Task:
Propose the smallest safe diff to agent skill files, examples, evals, or scripts that improves future behavior based on feedback.

Constraints:
- Do not weaken any safety, QA, PM, Codex review, branch conflict, SQL read-only, Terraform, deployment, or deletion policy.
- Do not expand autonomy.
- Add or update eval coverage if behavior changes.
- Keep core skill files concise.
- Update docs/agentic-self-improvement/changelog.md.
- Run: python .ai/scripts/skill_eval_runner.py --all
- Run: python .ai/scripts/skill_guardrails.py --base main || true if no git base exists.
- Do not merge.
""".strip()


def invoke_codex(prompt: str, dry_run: bool) -> int:
    if dry_run:
        Path(".agent/self-improvement").mkdir(parents=True, exist_ok=True)
        Path(".agent/self-improvement/codex-prompt.md").write_text(prompt + "\n", encoding="utf-8")
        print("Dry run: wrote .agent/self-improvement/codex-prompt.md")
        return 0
    codex = shutil.which("codex")
    if not codex:
        print("Codex CLI not found. Proposal scaffold created; run Codex manually with the generated prompt.", file=sys.stderr)
        Path(".agent/self-improvement").mkdir(parents=True, exist_ok=True)
        Path(".agent/self-improvement/codex-prompt.md").write_text(prompt + "\n", encoding="utf-8")
        return 2
    model = os.environ.get("AGENTIC_CODEX_MODEL", "gpt-5.5")
    effort = os.environ.get("AGENTIC_CODEX_REASONING_EFFORT", "xhigh")
    cmd = [codex, "exec", "--model", model, "-c", f"model_reasoning_effort={effort}", "--sandbox", "workspace-write", prompt]
    proc = subprocess.run(cmd, text=True)
    return proc.returncode


def create_branch(branch: str) -> None:
    subprocess.run(["git", "checkout", "-B", branch], check=True)


def open_pr(branch: str, title: str) -> int:
    gh = shutil.which("gh")
    if not gh:
        print("gh CLI not found; skipping PR creation.")
        return 2
    body = "@juanesriosg\n\nSelf-improvement proposal. Review the proposal, eval report, and guardrail output before approval."
    subprocess.run(["git", "push", "-u", "origin", branch], check=True)
    proc = subprocess.run([gh, "pr", "create", "--title", title, "--body", body, "--base", "main", "--head", branch], text=True)
    return proc.returncode


def main() -> int:
    p = argparse.ArgumentParser(description="Run the agent self-improvement loop.")
    sub = p.add_subparsers(dest="cmd", required=True)
    h = sub.add_parser("harvest")
    h.add_argument("--feedback-jsonl", default=str(FEEDBACK_JSONL))
    r = sub.add_parser("run-once")
    r.add_argument("--feedback-jsonl", default=str(FEEDBACK_JSONL))
    r.add_argument("--dry-run", action="store_true")
    r.add_argument("--create-branch", action="store_true")
    r.add_argument("--open-pr", action="store_true")
    r.add_argument("--minimum-feedback-events", type=int, default=3)
    args = p.parse_args()

    events = read_feedback(Path(getattr(args, "feedback_jsonl", FEEDBACK_JSONL)))
    summary = cluster(events)
    write_bundle(events, summary)

    if args.cmd == "harvest":
        print(json.dumps({"summary": summary, "bundle": str(OUT_DIR / "feedback-bundle.json")}, indent=2, sort_keys=True))
        return 0

    pid = proposal_id(summary)
    if args.create_branch:
        create_branch(f"ai/self-improvement/{pid}")

    proposal_dir = OUT_DIR / "proposals"
    proposal_dir.mkdir(parents=True, exist_ok=True)
    proposal_path = proposal_dir / f"{pid}.md"
    proposal_path.write_text(deterministic_proposal(events, summary), encoding="utf-8")
    (OUT_DIR / "changelog.md").write_text(f"# Self-improvement changelog\n\n- {now()}: created proposal `{pid}`.\n", encoding="utf-8")

    if len(events) < args.minimum_feedback_events:
        print(f"Only {len(events)} feedback events found; created proposal scaffold but will not invoke Codex improvement.")
        eval_code = run_evals()
        return 0 if args.dry_run else max(eval_code, 0)

    prompt = codex_prompt(proposal_path)
    codex_code = invoke_codex(prompt, args.dry_run)
    eval_code = run_evals()

    if args.open_pr and not args.dry_run:
        pr_code = open_pr(f"ai/self-improvement/{pid}", f"chore: self-improve agent skills ({pid})")
        return max(codex_code, eval_code, pr_code)
    return max(codex_code, eval_code)


if __name__ == "__main__":
    raise SystemExit(main())
