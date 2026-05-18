#!/usr/bin/env python3
"""Create optional repo-level docs folders used by agentic evidence and business context."""
from __future__ import annotations
from pathlib import Path
import shutil

ROOT = Path.cwd()
TEMPLATES = ROOT / ".ai" / "docs" / "templates"

FILES = {
    "docs/agentic-feedback/README.md": TEMPLATES / "agentic-feedback.README.md",
    "docs/agentic-self-improvement/README.md": TEMPLATES / "agentic-self-improvement.README.md",
    "docs/business-rules/_TEMPLATE.business-rules.md": TEMPLATES / "business-rules" / "_TEMPLATE.business-rules.md",
}


def main() -> int:
    created = []
    for dest_rel, src in FILES.items():
        dest = ROOT / dest_rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.exists():
            continue
        if src.exists():
            shutil.copyfile(src, dest)
        else:
            dest.write_text("# Agentic documentation\n\nGenerated placeholder.\n", encoding="utf-8")
        created.append(dest_rel)
    if created:
        print("Created optional repo docs:")
        for item in created:
            print(f"- {item}")
    else:
        print("Optional repo docs already exist.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
