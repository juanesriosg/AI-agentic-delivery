#!/usr/bin/env python3
"""Generate a test traceability matrix skeleton from a task/spec file."""
from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Dict, List, Tuple


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(errors="replace")


def parse_front_matter(text: str) -> Dict[str, str]:
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}
    data: Dict[str, str] = {}
    for line in text[4:end].splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or ":" not in stripped:
            continue
        key, value = stripped.split(":", 1)
        data[key.strip()] = value.strip().strip('"').strip("'")
    return data


def normalize_ac_id(raw: str, counter: int) -> str:
    token = raw.strip().upper().rstrip(":.)")
    match = re.match(r"AC[-_ ]?(\d+)$", token)
    if match:
        return f"AC-{int(match.group(1)):03d}"
    match = re.match(r"(\d+)$", token)
    if match:
        return f"AC-{int(match.group(1)):03d}"
    return f"AC-{counter:03d}"


def clean_requirement(value: str) -> str:
    return value.strip().lstrip(":.) ").strip() or "<add acceptance criterion>"


def table_requirement(cells: List[str]) -> str:
    """Turn AC table cells into a readable testable requirement."""
    payload = [c for c in cells[1:] if c and not set(c) <= {"-", ":"}]
    if len(payload) >= 3:
        return clean_requirement(f"Given {payload[0]}; When {payload[1]}; Then {payload[2]}")
    return clean_requirement("; ".join(payload))


def acceptance_criteria(text: str) -> List[Tuple[str, str]]:
    """Extract ACs from bullets, numbered lines, and Markdown tables."""
    acs: List[Tuple[str, str]] = []
    in_ac = False
    counter = 1
    for line in text.splitlines():
        stripped = line.strip()
        low = stripped.lower()
        if re.match(r"^#+\s+.*(acceptance criteria|acceptance|done when)", low):
            in_ac = True
            continue
        if in_ac and stripped.startswith("#"):
            in_ac = False
        if not in_ac:
            continue
        if stripped.startswith("|"):
            cells = [c.strip() for c in stripped.strip("|").split("|")]
            if cells and re.match(r"AC[-_ ]?\d+", cells[0], re.I):
                acs.append((normalize_ac_id(cells[0], counter), table_requirement(cells)))
                counter += 1
            continue
        if stripped.startswith("-"):
            raw = stripped.lstrip("- ").strip()
            m = re.match(r"^(AC[-_ ]?\d+|\d+[.)])\s*(.*)$", raw, re.I)
            if m:
                acs.append((normalize_ac_id(m.group(1), counter), clean_requirement(m.group(2))))
            elif raw:
                acs.append((f"AC-{counter:03d}", clean_requirement(raw)))
            counter += 1
            continue
        m = re.match(r"^(AC[-_ ]?\d+|\d+[.)])\s*(.*)$", stripped, re.I)
        if m:
            acs.append((normalize_ac_id(m.group(1), counter), clean_requirement(m.group(2))))
            counter += 1
    if not acs:
        acs.append(("AC-001", "<add acceptance criterion>"))
    seen = set()
    unique: List[Tuple[str, str]] = []
    for ac_id, req in acs:
        key = (ac_id.lower(), req.lower())
        if key not in seen:
            seen.add(key)
            unique.append((ac_id, req))
    return unique


def linked_acceptance_criteria(path: Path, text: str) -> List[Tuple[str, str]]:
    acs = acceptance_criteria(text)
    if acs and acs != [("AC-001", "<add acceptance criterion>")]:
        return acs
    front = parse_front_matter(text)
    for key in ("source_trd", "source_prd"):
        linked = front.get(key, "")
        if not linked:
            continue
        linked_path = (path.parent / linked).resolve() if not Path(linked).is_absolute() else Path(linked)
        if not linked_path.exists():
            linked_path = Path(linked)
        if linked_path.exists():
            linked_acs = acceptance_criteria(read_text(linked_path))
            if linked_acs and linked_acs != [("AC-001", "<add acceptance criterion>")]:
                return linked_acs
    return acs


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("spec_path", nargs="?", help="Spec path. Kept for backward-compatible positional usage.")
    parser.add_argument("--spec", help="Spec path.")
    args = parser.parse_args()
    selected = args.spec or args.spec_path
    if not selected:
        parser.error("one of --spec or spec_path is required")
    selected_path = Path(selected)
    text = read_text(selected_path)
    acs = linked_acceptance_criteria(selected_path, text)
    print("# Spec-to-Test Traceability Matrix")
    print("")
    print("| AC ID | Requirement | Unit | Component | Integration | Contract | E2E | Dev/QA | Evidence | Status |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    for ac_id, req in acs:
        safe = req.replace("|", "\\|")
        print(f"| {ac_id} | {safe} | unmapped | unmapped | unmapped | unmapped | unmapped | unmapped | unmapped | not_started |")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
