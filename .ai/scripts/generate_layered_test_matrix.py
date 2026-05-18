#!/usr/bin/env python3
"""Generate a DB → API → frontend test matrix from a spec."""
from __future__ import annotations

import argparse
import re
from pathlib import Path


def strip_front_matter(text: str) -> str:
    if text.startswith("---\n"):
        end = text.find("\n---\n", 4)
        if end != -1:
            return text[end + 5:]
    return text


def acceptance(text: str):
    body = strip_front_matter(text)
    lines = body.splitlines()
    capture = False
    out = []
    level = 999
    for line in lines:
        m = re.match(r"^(#{1,6})\s+(.*)$", line.strip())
        if m:
            if capture and len(m.group(1)) <= level:
                break
            if "acceptance" in m.group(2).lower() or "definition of done" in m.group(2).lower():
                capture = True
                level = len(m.group(1))
                continue
        if capture and re.match(r"^\s*[-*]\s+", line):
            out.append(re.sub(r"^\s*[-*]\s+", "", line).strip())
    return out or ["Primary spec behavior works as designed"]


def infer_layers(text: str):
    low = text.lower()
    layers = []
    if any(k in low for k in ["database", "schema", "data model", "migration", "sql", "dynamodb", "rds"]):
        layers.append("database")
    if any(k in low for k in ["api", "endpoint", "backend", "lambda", "rest", "graphql", "controller", "route"]):
        layers.append("api")
    if any(k in low for k in ["frontend", "ui", "form", "screen", "page", "component", "button", "input"]):
        layers.append("frontend")
    return layers or ["crosscutting"]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--spec", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    text = args.spec.read_text(encoding="utf-8", errors="replace")
    acs = acceptance(text)
    layers = infer_layers(text)
    lines = ["# Layered Test Matrix", "", f"Spec: `{args.spec}`", "", "Order: database → API → frontend", "", "| Acceptance criterion | Database tests | API/contract tests | Frontend/component tests | Integration/E2E | Evidence |", "|---|---|---|---|---|---|"]
    for ac in acs:
        db = "required" if "database" in layers else "not applicable"
        api = "required after DB pass" if "api" in layers else "not applicable"
        front = "required after API pass" if "frontend" in layers else "not applicable"
        e2e = "required for user flow" if "frontend" in layers and "api" in layers else "as applicable"
        lines.append(f"| {ac} | {db} | {api} | {front} | {e2e} | docs/agentic-evidence/... |")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(lines)+"\n", encoding="utf-8")
    print(args.output)

if __name__ == "__main__":
    main()
