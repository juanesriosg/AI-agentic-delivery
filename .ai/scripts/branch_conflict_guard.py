#!/usr/bin/env python3
"""Branch conflict guard for agent-created work.

Purpose:
- Prevent two active non-main branches from touching the same implementation file.
- Let agents switch to another task instead of creating annoying merge conflicts.
- Support early path reservations (leases) and final PR checks.

The script intentionally uses only Python's standard library and Git.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import fnmatch
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

ISO = "%Y-%m-%dT%H:%M:%SZ"
DEFAULT_BASE_CANDIDATES = ("main", "master", "develop")
DEFAULT_ACTIVE_BRANCH_PATTERNS = ("*")
RUNTIME_PREFIXES = (
    ".agent/", ".venv/", "venv/", "node_modules/", "vendor/bundle/",
    "__pycache__/", ".pytest_cache/", ".mypy_cache/", "target/", "dist/", "build/",
)
# These paths are deliberately branch-specific evidence/reservation metadata. They
# should not count as implementation conflicts.
NON_IMPLEMENTATION_PREFIXES = (
    "docs/agentic-evidence/",
    "docs/agentic-path-leases/",
    ".agent/",
)
LEASE_PREFIX = "docs/agentic-path-leases"
PATH_INTENT_SUFFIXES = ("path-intent.json", "path_lease.json", "path-lease.json")


def now_utc() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime(ISO)


def run(cmd: Sequence[str], check: bool = True, cwd: Optional[Path] = None) -> subprocess.CompletedProcess[str]:
    cp = subprocess.run(list(cmd), cwd=str(cwd) if cwd else None, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if check and cp.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(cmd)}\nSTDOUT:\n{cp.stdout}\nSTDERR:\n{cp.stderr}")
    return cp


def git(*args: str, check: bool = True) -> str:
    return run(["git", *args], check=check).stdout.strip()


def ref_exists(ref: str) -> bool:
    return run(["git", "rev-parse", "--verify", "--quiet", ref], check=False).returncode == 0


def repo_root() -> Path:
    cp = run(["git", "rev-parse", "--show-toplevel"], check=False)
    if cp.returncode != 0:
        raise RuntimeError("branch_conflict_guard.py must run inside a Git repository")
    return Path(cp.stdout.strip()).resolve()


def safe_slug(value: str, max_len: int = 120) -> str:
    value = value.strip().replace("\\", "/")
    value = re.sub(r"[^A-Za-z0-9._/-]+", "-", value)
    value = value.replace("/", "__")
    value = re.sub(r"-+", "-", value).strip("-._")
    return (value or "branch")[:max_len]


def normalize_path(path: str) -> str:
    normalized = path.strip().replace("\\", "/")
    while normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized


def is_runtime_or_nonimplementation(path: str) -> bool:
    normalized = normalize_path(path)
    if any(normalized.startswith(prefix) for prefix in RUNTIME_PREFIXES):
        return True
    if "/__pycache__/" in normalized or normalized.endswith(".pyc"):
        return True
    if any(normalized.startswith(prefix) for prefix in NON_IMPLEMENTATION_PREFIXES):
        return True
    return False


def path_matches_any(path: str, patterns: Iterable[str]) -> bool:
    normalized = normalize_path(path)
    for pattern in patterns:
        pat = normalize_path(pattern)
        if not pat:
            continue
        candidates = [pat, pat.replace("**/", "")]
        for candidate in candidates:
            if fnmatch.fnmatch(normalized, candidate):
                return True
            if candidate.endswith("/") and normalized.startswith(candidate):
                return True
    return False


def literal_prefix(pattern: str) -> str:
    pattern = normalize_path(pattern)
    wildcard_positions = [pos for pos in [pattern.find("*"), pattern.find("?"), pattern.find("[")] if pos >= 0]
    if wildcard_positions:
        pattern = pattern[:min(wildcard_positions)]
    if "/" in pattern:
        return pattern.rsplit("/", 1)[0] + "/"
    return pattern


def pattern_matches_path(pattern: str, path: str) -> bool:
    pattern = normalize_path(pattern)
    path = normalize_path(path)
    if not pattern or not path:
        return False
    if pattern == path:
        return True
    if any(token in pattern for token in "*?["):
        return fnmatch.fnmatch(path, pattern) or fnmatch.fnmatch(path, pattern.replace("**/", ""))
    if pattern.endswith("/"):
        return path.startswith(pattern)
    # Treat extensionless paths or paths ending with directory-looking names as directories too.
    if path.startswith(pattern.rstrip("/") + "/"):
        return True
    return False


def is_broad_pattern(value: str) -> bool:
    value = normalize_path(value)
    if any(token in value for token in "*?["):
        return True
    if value.endswith("/"):
        return True
    # Extensionless paths inside directories are usually directory/module intents,
    # for example `src/components` or `infra/terraform`.
    if "/" in value and not Path(value).suffix:
        return True
    return False


def patterns_overlap(a: str, b: str) -> bool:
    a = normalize_path(a)
    b = normalize_path(b)
    if not a or not b:
        return False
    if pattern_matches_path(a, b) or pattern_matches_path(b, a):
        return True
    # Exact file paths in the same directory are not conflicts unless the file is
    # the same. This avoids blocking `src/a.py` vs `src/b.py`.
    if not is_broad_pattern(a) and not is_broad_pattern(b):
        return False
    # Approximate broad pattern overlap by literal prefix. This intentionally errs
    # on the side of blocking only when at least one side is a directory/glob.
    ap = literal_prefix(a)
    bp = literal_prefix(b)
    return bool(ap and bp and (ap.startswith(bp) or bp.startswith(ap)))


def resolve_base_ref(base: str) -> str:
    remote_base = f"origin/{base}"
    run(["git", "fetch", "origin", f"{base}:refs/remotes/origin/{base}", "--depth", "1"], check=False)
    if ref_exists(remote_base):
        return remote_base
    if ref_exists(base):
        return base
    for candidate in DEFAULT_BASE_CANDIDATES:
        if candidate == base:
            continue
        remote_candidate = f"origin/{candidate}"
        if ref_exists(remote_candidate):
            return remote_candidate
        if ref_exists(candidate):
            return candidate
    roots = git("rev-list", "--max-parents=0", "HEAD", check=False).splitlines()
    return roots[0] if roots else "HEAD"


def current_branch() -> str:
    branch = git("rev-parse", "--abbrev-ref", "HEAD", check=False)
    return branch if branch and branch != "HEAD" else "detached-head"


def normalize_branch_from_ref(ref: str) -> str:
    ref = ref.strip()
    if not ref or ref.endswith("/HEAD"):
        return ""
    if ref.startswith("origin/"):
        return ref[len("origin/"):]
    return ref


def fetch_all_branches() -> None:
    run(["git", "fetch", "origin", "+refs/heads/*:refs/remotes/origin/*", "--prune"], check=False)


def list_active_refs(base_branch: str, exclude_branches: Iterable[str], branch_patterns: Iterable[str], include_remote: bool) -> List[Dict[str, str]]:
    refs_args = ["refs/heads"]
    if include_remote:
        refs_args.append("refs/remotes")
    output = git("for-each-ref", "--format=%(refname:short)", *refs_args, check=False)
    excluded = {normalize_branch_from_ref(x) for x in exclude_branches if x}
    excluded.update({base_branch, "main", "master", "develop", ""})
    branch_to_ref: Dict[str, str] = {}
    for line in output.splitlines():
        ref = line.strip()
        branch = normalize_branch_from_ref(ref)
        if not branch or branch in excluded or ref.endswith("/HEAD"):
            continue
        if not path_matches_any(branch, branch_patterns):
            continue
        # Prefer remote refs because they are visible to cloud workers too.
        if branch not in branch_to_ref or ref.startswith("origin/"):
            branch_to_ref[branch] = ref
    return [{"branch": branch, "ref": ref} for branch, ref in sorted(branch_to_ref.items())]


def changed_files_for_ref(base_ref: str, ref: str) -> List[str]:
    if not ref_exists(ref):
        return []
    merge_base = git("merge-base", base_ref, ref, check=False).strip()
    compare = merge_base if merge_base else base_ref
    output = git("diff", "--name-only", compare, ref, check=False)
    files = [normalize_path(x) for x in output.splitlines() if normalize_path(x)]
    return [f for f in files if not is_runtime_or_nonimplementation(f)]


def changed_files_current(diff_base: str) -> List[str]:
    base_ref = diff_base
    if not ref_exists(base_ref):
        if ref_exists(f"origin/{diff_base}"):
            base_ref = f"origin/{diff_base}"
        else:
            base_ref = resolve_base_ref(diff_base)
    output = git("diff", "--name-only", f"{base_ref}...HEAD", check=False)
    files = [normalize_path(x) for x in output.splitlines() if normalize_path(x)]
    # Include staged/unstaged/untracked files for local agent work before commit.
    # Preserve leading spaces in porcelain output. The first two columns are the
    # status code; stripping stdout would corrupt paths that start with a dot,
    # for example `.ai/scripts/foo.py`.
    status = run(["git", "status", "--porcelain"], check=False).stdout
    for line in status.splitlines():
        if not line.strip():
            continue
        raw_path = line[3:].strip() if len(line) > 3 else line.strip()
        if " -> " in raw_path:
            raw_path = raw_path.split(" -> ", 1)[1]
        files.append(normalize_path(raw_path))
    return sorted({f for f in files if f and not is_runtime_or_nonimplementation(f)})


def paths_from_spec_file(path: Optional[str]) -> List[str]:
    if not path:
        return []
    p = Path(path)
    if not p.exists():
        return []
    text = p.read_text(encoding="utf-8", errors="replace")
    candidates: List[str] = []
    in_files_section = False
    section_level = 99
    for raw in text.splitlines():
        line = raw.strip()
        heading = re.match(r"^(#+)\s+(.*)$", line)
        if heading:
            level = len(heading.group(1))
            title = heading.group(2).lower()
            if in_files_section and level <= section_level:
                in_files_section = False
            if any(token in title for token in ("files", "areas to touch", "paths")):
                in_files_section = True
                section_level = level
                continue
        if not in_files_section:
            continue
        candidates.extend(re.findall(r"`([^`]+)`", raw))
        table_cells = [cell.strip() for cell in raw.split("|")]
        for cell in table_cells:
            if re.search(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.*/-]+", cell):
                candidates.append(cell)
    cleaned: List[str] = []
    for item in candidates:
        item = item.strip().strip(".,;:()[]{}")
        if not item or item.lower() in {"path", "path / pattern", "src/...", "tests/..."}:
            continue
        if "<" in item and ">" in item:
            continue
        if item.startswith(("http://", "https://")):
            continue
        cleaned.append(normalize_path(item))
    return sorted(set(cleaned))


def ls_tree_names(ref: str) -> List[str]:
    output = git("ls-tree", "-r", "--name-only", ref, check=False)
    return [normalize_path(x) for x in output.splitlines() if normalize_path(x)]


def read_file_at_ref(ref: str, path: str) -> str:
    return git("show", f"{ref}:{path}", check=False)


def lease_files_for_ref(ref: str) -> List[str]:
    names = ls_tree_names(ref)
    out: List[str] = []
    for name in names:
        if name.startswith(LEASE_PREFIX + "/") and name.endswith(".json"):
            out.append(name)
        elif name.endswith(PATH_INTENT_SUFFIXES):
            out.append(name)
    return out


def read_path_leases(ref: str) -> List[Dict[str, Any]]:
    leases: List[Dict[str, Any]] = []
    for path in lease_files_for_ref(ref):
        raw = read_file_at_ref(ref, path)
        if not raw.strip():
            continue
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            continue
        paths = data.get("reserved_paths") or data.get("paths") or data.get("expected_paths") or []
        if isinstance(paths, str):
            paths = [paths]
        paths = [normalize_path(str(p)) for p in paths if normalize_path(str(p))]
        if paths:
            leases.append({
                "lease_file": path,
                "branch": data.get("branch") or data.get("owner_branch") or "unknown",
                "task_id": data.get("task_id") or data.get("task") or "unknown",
                "story_id": data.get("story_id") or data.get("story") or "unknown",
                "reserved_paths": paths,
                "created_at": data.get("created_at"),
            })
    return leases


def conflict_report(current_paths: List[str], active_refs: List[Dict[str, str]], base_ref: str, ignore_patterns: Iterable[str]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    conflicts: List[Dict[str, Any]] = []
    branches: List[Dict[str, Any]] = []
    current = [p for p in sorted(set(map(normalize_path, current_paths))) if p and not is_runtime_or_nonimplementation(p)]
    current = [p for p in current if not path_matches_any(p, ignore_patterns)]
    for item in active_refs:
        branch = item["branch"]
        ref = item["ref"]
        changed = [p for p in changed_files_for_ref(base_ref, ref) if not path_matches_any(p, ignore_patterns)]
        leases = read_path_leases(ref)
        branches.append({"branch": branch, "ref": ref, "changed_files": changed, "path_leases": leases})
        for path in current:
            for other in changed:
                if patterns_overlap(path, other):
                    conflicts.append({
                        "path": path,
                        "other_path": other,
                        "branch": branch,
                        "ref": ref,
                        "conflict_type": "actual_branch_change",
                        "severity": "blocking",
                        "reason": "Another active branch already changes this implementation path.",
                    })
            for lease in leases:
                for reserved in lease.get("reserved_paths", []):
                    if patterns_overlap(path, reserved):
                        conflicts.append({
                            "path": path,
                            "other_path": reserved,
                            "branch": branch,
                            "ref": ref,
                            "conflict_type": "reserved_path",
                            "severity": "blocking",
                            "lease_file": lease.get("lease_file"),
                            "other_task_id": lease.get("task_id"),
                            "reason": "Another active agent reserved this path before implementation.",
                        })
    # Deduplicate conflicts.
    unique: Dict[Tuple[str, str, str, str], Dict[str, Any]] = {}
    for c in conflicts:
        key = (c["path"], c["other_path"], c["branch"], c["conflict_type"])
        unique[key] = c
    return list(unique.values()), branches


def write_outputs(report: Dict[str, Any], json_output: Optional[str], markdown_output: Optional[str]) -> None:
    if json_output:
        path = Path(json_output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if markdown_output:
        path = Path(markdown_output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(markdown_report(report), encoding="utf-8")


def markdown_report(report: Dict[str, Any]) -> str:
    lines = [
        f"# Branch Conflict Guard: {report.get('status', 'UNKNOWN')}",
        "",
        f"Mode: `{report.get('mode')}`",
        f"Current branch: `{report.get('current_branch')}`",
        f"Base branch: `{report.get('base_branch')}`",
        f"Base ref: `{report.get('base_ref')}`",
        f"Checked at: `{report.get('checked_at')}`",
        "",
        "## Current paths",
        "",
    ]
    current_paths = report.get("current_paths") or []
    if current_paths:
        lines.extend([f"- `{p}`" for p in current_paths])
    else:
        lines.append("No current paths were available. Preflight can only reserve/check paths when the task planner provides expected files.")
    lines += ["", "## Conflicts", ""]
    conflicts = report.get("conflicts") or []
    if conflicts:
        for c in conflicts:
            lines.append(f"- **{c.get('conflict_type')}**: `{c.get('path')}` overlaps `{c.get('other_path')}` in `{c.get('branch')}`. {c.get('reason','')}")
    else:
        lines.append("No path overlap found with active branches or path reservations.")
    lines += ["", "## Active branches scanned", ""]
    branches = report.get("active_branches") or []
    if branches:
        for b in branches:
            changed = b.get("changed_files") or []
            leases = b.get("path_leases") or []
            lines.append(f"- `{b.get('branch')}` via `{b.get('ref')}` — {len(changed)} changed implementation path(s), {len(leases)} path lease(s)")
    else:
        lines.append("No active branches scanned.")
    lines += ["", "## Required action", ""]
    if report.get("status") == "BLOCKED":
        lines.append("This task must not continue. The dev agent should switch to another task, split the task, or ask the manager to approve a specific overlap exception.")
    elif report.get("status") == "WARN":
        lines.append("Continue only with low-risk discovery. Add expected paths before implementation when possible.")
    else:
        lines.append("The task can continue under the one-responsibility PR policy.")
    return "\n".join(lines) + "\n"


def write_lease(current_paths: List[str], args: argparse.Namespace) -> Optional[Path]:
    if not args.write_lease:
        return None
    paths = [p for p in sorted(set(map(normalize_path, current_paths))) if p]
    if not paths and not args.allow_empty_intent:
        return None
    branch = current_branch()
    lease_dir = Path(LEASE_PREFIX)
    lease_dir.mkdir(parents=True, exist_ok=True)
    lease_path = lease_dir / f"{safe_slug(branch)}.json"
    payload = {
        "schema": "agentic.path-lease.v1",
        "branch": branch,
        "story_id": args.story_id or "unknown",
        "task_id": args.task_id or "unknown",
        "mode": args.mode,
        "reserved_paths": paths,
        "created_at": now_utc(),
        "expires_policy": "Lease is valid while this branch or PR is active.",
        "rules": [
            "No other active agent branch should modify these paths.",
            "If overlap is detected, switch tasks or request manager approval.",
        ],
    }
    lease_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.commit_lease:
        run(["git", "add", str(lease_path)], check=True)
        # Avoid empty commit if unchanged.
        diff = run(["git", "diff", "--cached", "--quiet"], check=False)
        if diff.returncode != 0:
            run(["git", "commit", "-m", f"chore(agent): reserve paths for {args.task_id or branch}"], check=True)
    if args.push_lease:
        run(["git", "push", "-u", "origin", branch], check=False)
    return lease_path


def build_current_paths(args: argparse.Namespace) -> List[str]:
    paths = [normalize_path(p) for p in args.path if normalize_path(p)]
    paths.extend(paths_from_spec_file(args.spec_file))
    if args.current_diff or not paths:
        paths.extend(changed_files_current(args.current_diff_base or args.base))
    paths = [p for p in paths if p and not is_runtime_or_nonimplementation(p)]
    return sorted(set(paths))


def do_guard(args: argparse.Namespace) -> int:
    if args.fetch:
        fetch_all_branches()
    base_ref = resolve_base_ref(args.base)
    current = current_branch()
    exclude = set(args.exclude_branch or [])
    exclude.add(current)
    active_refs = list_active_refs(args.base, exclude, args.branch_pattern, include_remote=args.include_remote)
    current_paths = build_current_paths(args)
    ignore_patterns = list(args.ignore_pattern or [])
    conflicts, active_branches = conflict_report(current_paths, active_refs, base_ref, ignore_patterns)
    status = "PASS"
    if conflicts and not args.allow_overlap:
        status = "BLOCKED"
    elif not current_paths:
        status = "WARN"
    lease_path = None
    if status != "BLOCKED" or args.allow_overlap:
        lease_path = write_lease(current_paths, args)
    report = {
        "schema": "agentic.branch-conflict-report.v1",
        "status": status,
        "mode": args.mode,
        "checked_at": now_utc(),
        "current_branch": current,
        "base_branch": args.base,
        "base_ref": base_ref,
        "current_diff_base": args.current_diff_base or args.base,
        "current_paths": current_paths,
        "conflicts": conflicts,
        "active_branches": active_branches,
        "lease_file": str(lease_path) if lease_path else None,
        "allow_overlap": bool(args.allow_overlap),
    }
    write_outputs(report, args.json_output, args.markdown_output)
    print(json.dumps(report, indent=2, sort_keys=True))
    if status == "BLOCKED" and not args.allow_overlap:
        return 2
    return 0


def do_changed(args: argparse.Namespace) -> int:
    paths = changed_files_current(args.current_diff_base or args.base)
    print("\n".join(paths))
    return 0


def do_scan(args: argparse.Namespace) -> int:
    if args.fetch:
        fetch_all_branches()
    base_ref = resolve_base_ref(args.base)
    active_refs = list_active_refs(args.base, args.exclude_branch or [], args.branch_pattern, include_remote=args.include_remote)
    branches = []
    for item in active_refs:
        branches.append({
            "branch": item["branch"],
            "ref": item["ref"],
            "changed_files": changed_files_for_ref(base_ref, item["ref"]),
            "path_leases": read_path_leases(item["ref"]),
        })
    report = {
        "schema": "agentic.branch-conflict-scan.v1",
        "status": "PASS",
        "mode": "scan",
        "checked_at": now_utc(),
        "base_branch": args.base,
        "base_ref": base_ref,
        "active_branches": branches,
    }
    write_outputs(report, args.json_output, args.markdown_output)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Prevent active agent branches from touching the same implementation files.")
    parser.add_argument("command", nargs="?", default="guard", choices=["guard", "scan", "changed"])
    parser.add_argument("--mode", default="preflight", choices=["preflight", "postflight", "pr", "manual"])
    parser.add_argument("--base", default=os.environ.get("AGENTIC_DEFAULT_BASE_BRANCH", "main"))
    parser.add_argument("--current-diff-base", default=None, help="Base used to determine current branch changed paths. For PRs use github.base_ref/source spec branch.")
    parser.add_argument("--path", action="append", default=[], help="Expected path/pattern this task needs to touch. Can be repeated.")
    parser.add_argument("--spec-file", default=None, help="Optional spec file to extract files-to-touch paths from.")
    parser.add_argument("--exclude-branch", action="append", default=[], help="Branch to ignore when scanning active branch changes. Can be repeated.")
    parser.add_argument("--branch-pattern", action="append", default=["*"], help="Active branch glob to scan. Defaults to all non-main branches.")
    parser.add_argument("--ignore-pattern", action="append", default=[], help="Path glob to ignore for conflict purposes. Can be repeated.")
    parser.add_argument("--include-remote", action="store_true", default=True)
    parser.add_argument("--no-remote", action="store_false", dest="include_remote")
    parser.add_argument("--fetch", action="store_true", default=True)
    parser.add_argument("--no-fetch", action="store_false", dest="fetch")
    parser.add_argument("--current-diff", action="store_true", default=False, help="Include current branch diff. Auto-enabled when no --path is given.")
    parser.add_argument("--write-lease", action="store_true", help="Write docs/agentic-path-leases/<branch>.json when the check passes.")
    parser.add_argument("--commit-lease", action="store_true", help="Commit the lease file to the current branch.")
    parser.add_argument("--push-lease", action="store_true", help="Push current branch after committing the lease.")
    parser.add_argument("--allow-empty-intent", action="store_true")
    parser.add_argument("--allow-overlap", action="store_true", default=os.environ.get("AGENT_ALLOW_FILE_OVERLAP", "false").lower() in {"1", "true", "yes"})
    parser.add_argument("--task-id", default="")
    parser.add_argument("--story-id", default="")
    parser.add_argument("--json-output", default=None)
    parser.add_argument("--markdown-output", default=None)
    args = parser.parse_args(argv)

    repo_root()  # fail early if not inside repo
    if args.command == "changed":
        return do_changed(args)
    if args.command == "scan":
        return do_scan(args)
    return do_guard(args)


if __name__ == "__main__":
    raise SystemExit(main())
