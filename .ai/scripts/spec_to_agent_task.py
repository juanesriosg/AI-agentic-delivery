#!/usr/bin/env python3
"""Render an implementation task for an agent from a spec file."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Tuple


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(errors="replace")


def slugify(value: str, max_len: int = 48) -> str:
    value = re.sub(r"[^A-Za-z0-9]+", "-", value).strip("-").lower()
    return (value[:max_len].strip("-") or "spec")


def clean_value(value: str) -> str:
    cleaned = value.strip().strip("`").strip().strip('"\'').strip()
    # Handles markdown labels such as **Owner:** @name where split leaves leading ** in value.
    return cleaned.strip("* ").strip()


def parse_front_matter(text: str) -> Dict[str, str]:
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}
    raw = text[4:end]
    data: Dict[str, str] = {}
    for line in raw.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or ":" not in stripped:
            continue
        key, value = stripped.split(":", 1)
        value = value.strip()
        if " #" in value:
            value = value.split(" #", 1)[0].strip()
        data[key.strip()] = clean_value(value)
    return data


def is_template_spec_path(path: Path | str) -> bool:
    normalized = str(path).replace("\\", "/").lower()
    name = Path(normalized).name
    return name.startswith("_template") or ".template." in name or name.startswith("template.") or "/examples/" in normalized


def normalize_key(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.lower())


def extract_yaml_scalar(text: str, key: str) -> str:
    front = parse_front_matter(text)
    for k, v in front.items():
        if normalize_key(k) == normalize_key(key):
            return clean_value(v)
    pattern = re.compile(rf"^\s*{re.escape(key)}\s*:\s*(.+?)\s*$", re.I | re.M)
    match = pattern.search(text)
    return clean_value(match.group(1)) if match else ""


def extract_title(text: str, spec_path: str) -> str:
    front_title = extract_yaml_scalar(text, "title")
    if front_title:
        return front_title
    for line in text.splitlines():
        if line.strip().startswith("#"):
            title = line.lstrip("#").strip()
            if title:
                return title
    return Path(spec_path).stem.replace("-", " ").replace("_", " ").title()


def extract_field(text: str, field: str) -> str:
    wanted = normalize_key(field)
    aliases = {wanted}
    if wanted == "specid":
        aliases.update({"spec", "id", "spec_id"})
    if wanted == "risk":
        aliases.update({"risklevel", "risk_level"})
    if wanted == "autonomy":
        aliases.update({"autonomylevel", "autonomy_level"})
    if wanted == "owner":
        aliases.update({"productowner", "aipm", "productowneraipm", "managergithubuser", "manager_github_user"})

    front = parse_front_matter(text)
    for k, v in front.items():
        if normalize_key(k) in aliases:
            return clean_value(v)

    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("---"):
            continue
        cleaned = line.strip("* ")
        m = re.match(r"^([A-Za-z0-9_ /.-]+?)\s*:\s*(.+?)\s*$", cleaned)
        if m and normalize_key(m.group(1)) in aliases:
            return clean_value(m.group(2))
        if line.startswith("|") and line.endswith("|"):
            cells = [c.strip().strip("*") for c in line.strip("|").split("|")]
            if len(cells) >= 2 and normalize_key(cells[0]) in aliases and not set(cells[1]) <= {"-"}:
                return clean_value(cells[1])
    return ""


def format_table_acceptance(cells: List[str]) -> str:
    payload = [c for c in cells[1:] if c and not set(c) <= {"-", ":"}]
    if len(payload) >= 3:
        return f"Given {payload[0]}; When {payload[1]}; Then {payload[2]}"
    return "; ".join(payload).strip()


def extract_acceptance_criteria(text: str) -> List[str]:
    acs: List[str] = []
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
        if in_ac and stripped.startswith("|") and "|" in stripped[1:]:
            cells = [c.strip() for c in stripped.strip("|").split("|")]
            if cells and re.match(r"AC[-_ ]?\d+", cells[0], re.I):
                ac_id = cells[0].replace(" ", "-").replace("_", "-").upper()
                criterion = format_table_acceptance(cells)
                acs.append(f"{ac_id}: {criterion}".strip())
                counter += 1
            continue
        if in_ac and stripped.startswith("-"):
            raw = stripped.lstrip("- ").strip()
            if raw:
                if not re.match(r"AC[-_ ]?\d+", raw, re.I):
                    raw = f"AC-{counter:03d}: {raw}"
                acs.append(raw)
                counter += 1
        else:
            match = re.match(r"^(AC[-_ ]?\d+[:.)]?\s+.+)$", stripped, re.I)
            if match:
                acs.append(match.group(1))
    return acs


def spec_id_from(text: str, spec_path: str) -> str:
    explicit = extract_field(text, "Spec ID") or extract_field(text, "spec_id") or extract_yaml_scalar(text, "id")
    if explicit and not explicit.lower().startswith("<"):
        return slugify(explicit, 60).upper()
    digest = hashlib.sha1((spec_path + text[:512]).encode("utf-8")).hexdigest()[:8]
    return f"SPEC-{digest}"


def render_payload(spec_path: Path, branch: str, sha: str, repo: str) -> Dict[str, Any]:
    text = read_text(spec_path)
    front = parse_front_matter(text)
    title = front.get("title") or extract_title(text, str(spec_path))
    spec_id = front.get("spec_id") or spec_id_from(text, str(spec_path))
    status = front.get("status", "")
    slug = slugify(title)
    implementation_branch = f"ai/{slugify(spec_id, 24)}-{slug}"
    return {
        "event_type": "ai_spec_ready",
        "repository": repo,
        "source_spec_branch": branch,
        "source_commit_sha": sha,
        "spec_path": str(spec_path),
        "title": title,
        "spec_id": spec_id,
        "spec_status": status,
        "implementation_branch": implementation_branch,
        "pr_target_branch": branch,
        "autonomy": extract_field(text, "Autonomy level") or extract_field(text, "Autonomy") or "L3",
        "risk": extract_field(text, "Risk level") or extract_field(text, "Risk") or "unknown",
        "owner": extract_field(text, "Product owner / AI PM") or extract_field(text, "Owner") or "manager/repo-owner",
        "acceptance_criteria": extract_acceptance_criteria(text),
        "required_agent": "mid-software-engineer",
    }


def render_markdown(payload: Dict[str, Any]) -> str:
    acs = payload.get("acceptance_criteria") or []
    ac_block = "\n".join(f"- {ac}" for ac in acs) if acs else "- No acceptance criteria detected; ask clarification before risky implementation."
    return f"""
# AI Implementation Task from Spec: {payload['title']}

Status: `ai:ready`
Source spec branch: `{payload['source_spec_branch']}`
Source commit SHA: `{payload['source_commit_sha']}`
Spec path: `{payload['spec_path']}`
Implementation branch: `{payload['implementation_branch']}`
PR target branch: `{payload['pr_target_branch']}`
Autonomy: `{payload['autonomy']}`
Risk: `{payload['risk']}`
Owner: `{payload['owner']}`

## Mission

Implement the spec pushed to the source branch. Work like a mid-level software engineer: read the spec deeply, test first or near-first, implement safely, self-review, open a PR, notify the manager, and continue to the next ready task when possible.

## Required files to read first

- `AGENTS.md`
- `.ai/specs/branch-spec-ingestion.yml`
- `.ai/specs/spec-file-convention.md`
- `.ai/specs/spec-implementation-pipeline.md`
- `.ai/specs/testing-lifecycle.yml`
- `.ai/specs/quality-rubric.yml`
- `.ai/specs/deployment-gates.yml`
- `{payload['spec_path']}`

## Acceptance criteria detected

{ac_block}

## Required execution

```bash
git fetch --all --prune
git checkout {payload['source_spec_branch']}
.codex/bootstrap.sh || .ai/scripts/bootstrap-task-env.sh
.ai/scripts/spec-quality-check.py --spec {payload['spec_path']} --format markdown
.ai/scripts/generate-test-matrix.py --spec {payload['spec_path']}
git checkout -b {payload['implementation_branch']}
```

Then follow the repo SDLC: requirements review, task split, implementation, unit/component/integration/E2E/visual/accessibility tests as applicable, QA gate, PM gate, dev-manager PR gate, concise PR notification, and next-task continuation.

## Deployment restriction

Do not deploy to production. Non-production deployment is allowed only if the repo explicitly opts in and `.ai/specs/deployment-gates.yml` passes.
""".strip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--spec", required=True)
    parser.add_argument("--branch", default=os.environ.get("GITHUB_REF_NAME", "unknown"))
    parser.add_argument("--sha", default=os.environ.get("GITHUB_SHA", "unknown"))
    parser.add_argument("--repo", default=os.environ.get("GITHUB_REPOSITORY", "local"))
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown")
    parser.add_argument("--out")
    parser.add_argument("--require-ready-status", action="store_true", help="Require frontmatter status: ready_for_agents before dispatch.")
    args = parser.parse_args()

    spec_path = Path(args.spec)
    if is_template_spec_path(spec_path):
        raise SystemExit(f"Refusing to render implementation task for template/example file: {spec_path}")
    payload = render_payload(spec_path, args.branch, args.sha, args.repo)
    if args.require_ready_status and payload.get("spec_status") != "ready_for_agents":
        raise SystemExit(f"Spec status must be ready_for_agents before task dispatch; got {payload.get('spec_status') or 'missing'}")
    output = json.dumps(payload, indent=2) if args.format == "json" else render_markdown(payload)
    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(output, encoding="utf-8")
    else:
        print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
