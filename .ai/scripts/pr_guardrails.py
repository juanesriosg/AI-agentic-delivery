#!/usr/bin/env python3
"""PR guardrails for agent-created branches.

Stops false-positive "done" PRs: one responsibility, meaningful changes,
real QA/PM/test evidence, required tests, and no protected deletions.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Iterable, List, Tuple

PROTECTED_DELETIONS = [
    ".github/", ".ai/", "infra/", "terraform/", "migrations/", "database/",
    "CODEOWNERS", "LICENSE", "AGENTS.md", "package-lock.json", "pnpm-lock.yaml",
    "yarn.lock", "poetry.lock", "Pipfile.lock", "go.sum", "Cargo.lock",
]
RUNTIME_PREFIXES = (
    ".agent/", ".venv/", "venv/", "node_modules/", "vendor/bundle/",
    "__pycache__/", ".pytest_cache/", ".mypy_cache/", "target/", "dist/", "build/",
)
EVIDENCE_PREFIXES = ("docs/agentic-evidence/", ".agent/")
UI_EXTENSIONS = {".tsx", ".jsx", ".vue", ".svelte", ".css", ".scss", ".html"}
CODE_EXTENSIONS = {".py", ".ts", ".tsx", ".js", ".jsx", ".go", ".rs", ".java", ".kt", ".cs", ".rb", ".php"}
API_HINTS = ["api/", "routes/", "controllers/", "handlers/", "lambda", "server", "backend"]
TEST_HINTS = ["test", "spec", "__tests__", "e2e", "integration", "cypress", "playwright", "vitest", "jest", "pytest"]
PASS_WORDS = ("pass", "passed", "approved", "ok", "accepted", "completed")
BAD_STATUS_WORDS = ("pending_agent_verification", "pending", "blocked", "fail", "failed")


def run(cmd: List[str], check: bool = True) -> str:
    cp = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if check and cp.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(cmd)}\n{cp.stderr}")
    return cp.stdout


def path_within_scopes(path: str, scopes: Iterable[str]) -> bool:
    normalized = path.replace("\\", "/").strip("/")
    for scope in scopes:
        normalized_scope = str(scope).replace("\\", "/").strip("/")
        if not normalized_scope:
            continue
        if normalized == normalized_scope or normalized.startswith(normalized_scope.rstrip("/") + "/"):
            return True
    return False


def scope_paths_from_env(name: str = "AGENTIC_SCOPE_PATHS_JSON") -> list[str]:
    raw = os.environ.get(name, "").strip()
    if not raw:
        return []
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return []
    if not isinstance(parsed, list):
        return []
    return [str(item).replace("\\", "/").strip("/") for item in parsed if str(item).strip()]


def ref_exists(ref: str) -> bool:
    cp = subprocess.run(["git", "rev-parse", "--verify", "--quiet", ref], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return cp.returncode == 0


def resolve_base_ref(base: str) -> str:
    # Fetch when origin exists; continue gracefully in local/offline repos.
    run(["git", "fetch", "origin", f"{base}:refs/remotes/origin/{base}", "--depth", "1"], check=False)
    remote_base = f"origin/{base}"
    if ref_exists(remote_base):
        return remote_base
    if ref_exists(base):
        return base
    roots = run(["git", "rev-list", "--max-parents=0", "HEAD"], check=False).splitlines()
    return roots[0] if roots else "HEAD"


def expand_status_path(path: str) -> list[str]:
    # Porcelain rename lines can look like "old -> new"; validate the final path.
    if " -> " in path:
        path = path.split(" -> ", 1)[1]
    path = path.strip().replace("\\", "/")
    if not path:
        return []
    p = Path(path)
    if p.is_dir():
        out: list[str] = []
        for child in p.rglob("*"):
            if child.is_file() and ".git" not in child.parts:
                out.append(child.as_posix())
        return out
    return [path]


def changed_files(base: str) -> List[Tuple[str, str]]:
    base_ref = resolve_base_ref(base)
    out = run(["git", "diff", "--name-status", f"{base_ref}...HEAD"], check=False)
    rows: List[Tuple[str, str]] = []
    for line in out.splitlines():
        parts = line.split("\t")
        if len(parts) >= 2:
            for path in expand_status_path(parts[-1]):
                rows.append((parts[0], path))
    # Include unstaged/staged/untracked files when run during local orchestration before commit.
    status = run(["git", "status", "--porcelain"], check=False)
    for line in status.splitlines():
        if not line.strip():
            continue
        status_code = line[:2].strip() or "M"
        raw_path = line[3:].strip() if len(line) > 3 else line.strip()
        for path in expand_status_path(raw_path):
            rows.append((status_code, path))
    dedup: dict[str, str] = {}
    for status_code, path in rows:
        dedup[path] = status_code
    return [(status_code, path) for path, status_code in sorted(dedup.items())]


def numstat_from_output(output: str) -> Tuple[int, int]:
    added = deleted = 0
    for line in output.splitlines():
        parts = line.split("\t")
        if len(parts) < 2:
            continue
        a, d = parts[0], parts[1]
        if a.isdigit():
            added += int(a)
        if d.isdigit():
            deleted += int(d)
    return added, deleted


def text_file_line_count(path: str) -> int:
    p = Path(path)
    try:
        data = p.read_bytes()
    except Exception:
        return 0
    if b"\0" in data:
        return 0
    try:
        return len(data.decode("utf-8", errors="replace").splitlines())
    except Exception:
        return 0


def diff_stat(base: str) -> Tuple[int, int]:
    base_ref = resolve_base_ref(base)
    added = deleted = 0
    for cmd in [
        ["git", "diff", "--numstat", f"{base_ref}...HEAD"],
        ["git", "diff", "--cached", "--numstat"],
        ["git", "diff", "--numstat"],
    ]:
        a, d = numstat_from_output(run(cmd, check=False))
        added += a
        deleted += d
    untracked = run(["git", "ls-files", "--others", "--exclude-standard"], check=False).splitlines()
    added += sum(text_file_line_count(path) for path in untracked)
    return added, deleted


def diff_stat_for_files(base: str, files: Iterable[str]) -> Tuple[int, int]:
    """Return line counts for selected paths only.

    Guardrails should judge PR size by implementation changes, not by runtime
    artifacts or generated agent evidence. This keeps evidence-rich PRs from
    failing only because agents wrote QA/PM/test reports.
    """
    selected = sorted({f.replace("\\", "/") for f in files if f})
    if not selected:
        return 0, 0
    base_ref = resolve_base_ref(base)
    added = deleted = 0
    for path in selected:
        for cmd in [
            ["git", "diff", "--numstat", f"{base_ref}...HEAD", "--", path],
            ["git", "diff", "--cached", "--numstat", "--", path],
            ["git", "diff", "--numstat", "--", path],
        ]:
            a, d = numstat_from_output(run(cmd, check=False))
            added += a
            deleted += d
    untracked = set(run(["git", "ls-files", "--others", "--exclude-standard"], check=False).splitlines())
    added += sum(text_file_line_count(path) for path in selected if path in untracked)
    return added, deleted


def has_test_change(files: Iterable[str]) -> bool:
    return any(any(h in f.lower() for h in TEST_HINTS) for f in files)


def has_ui_change(files: Iterable[str]) -> bool:
    return any(Path(f).suffix.lower() in UI_EXTENSIONS for f in files)


def has_api_change(files: Iterable[str]) -> bool:
    lower = [f.lower() for f in files]
    return any(any(h in f for h in API_HINTS) for f in lower)


def is_runtime_file(path: str) -> bool:
    normalized = path.replace("\\", "/")
    return any(normalized.startswith(prefix) for prefix in RUNTIME_PREFIXES) or "/__pycache__/" in normalized or normalized.endswith(".pyc")


def is_evidence_only(files: list[str]) -> bool:
    reviewable = [f for f in files if not is_runtime_file(f)]
    normalized = [f.replace("\\", "/") for f in reviewable]
    return bool(normalized) and all(f.startswith(EVIDENCE_PREFIXES) for f in normalized)


def is_evidence_or_support_only(files: list[str]) -> bool:
    reviewable = [f for f in files if not is_runtime_file(f)]
    normalized = [f.replace("\\", "/") for f in reviewable]
    return bool(normalized) and all(
        f.startswith(EVIDENCE_PREFIXES) or classify_domain(f) == "support"
        for f in normalized
    )


def classify_domain(path: str) -> str:
    normalized = path.replace("\\", "/").lower()
    suffix = Path(normalized).suffix.lower()
    if normalized.startswith(EVIDENCE_PREFIXES) or is_runtime_file(normalized) or any(h in normalized for h in TEST_HINTS):
        return "support"
    if normalized.startswith(("infra/", "terraform/", "cdk/", "cloudformation/", "k8s/", "helm/")) or suffix == ".tf" or "/terraform/" in normalized:
        return "cloud"
    if normalized.startswith((".github/workflows/", "scripts/deploy/")):
        return "deployment"
    if any(token in normalized for token in ("auth", "permission", "iam", "policy", "secret", "security")):
        return "security"
    if any(token in normalized for token in ("migration", "database", "prisma", "schema.sql", "/db/", "sql/")):
        return "database"
    if any(h in normalized for h in API_HINTS):
        return "backend"
    if suffix in UI_EXTENSIONS or any(token in normalized for token in ("components/", "pages/", "app/", "frontend/", "ui/", "styles/", "public/")):
        return "frontend"
    return "unknown"


def responsibility_domains(files: Iterable[str]) -> set[str]:
    domains = {classify_domain(f) for f in files}
    return {d for d in domains if d not in {"support", "unknown"}}


def evidence_dir_for(task_id: str) -> List[Path]:
    base = Path("docs/agentic-evidence")
    if not base.exists():
        return []
    return [p for p in base.glob(f"**/{task_id}") if p.is_dir()]


def discover_task_evidence_dirs() -> list[Path]:
    base = Path("docs/agentic-evidence")
    if not base.exists():
        return []
    required = {"agents.log.md", "qa-checklist.md", "pm-checklist.md", "test-evidence.md"}
    out: list[Path] = []
    for path in base.rglob("*"):
        if path.is_dir() and required.issubset({child.name for child in path.iterdir() if child.is_file()}):
            out.append(path)
    return sorted(out)


def file_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""


def gate_status_failures(path: Path, gate_name: str) -> list[str]:
    failures: list[str] = []
    text = file_text(path)
    lower = text.lower()
    if "pending_agent_verification" in lower:
        failures.append(f"{gate_name} evidence is still pending: {path}")
    status_lines = [
        line.strip().lower()
        for line in text.splitlines()
        if re.search(r"^(status|qa status|pm status|qa decision|pm decision|decision|qa result|pm result|result)\s*:", line.strip(), re.I)
    ]
    if not status_lines:
        failures.append(f"{gate_name} evidence has no Status/Decision line: {path}")
        return failures
    joined = "\n".join(status_lines)
    if any(word in joined for word in BAD_STATUS_WORDS):
        failures.append(f"{gate_name} status is not passing: {path}")
    if not any(word in joined for word in PASS_WORDS):
        failures.append(f"{gate_name} status/decision does not clearly say pass/approved: {path}")
    return failures


def validate_evidence(evidence_dirs: list[Path], ui_required: bool) -> list[str]:
    failures: list[str] = []
    required = ["agents.log.md", "qa-checklist.md", "pm-checklist.md", "test-evidence.md", "scale-security-architecture-review.md", "pr-notification.md"]
    for ev in evidence_dirs:
        for name in required:
            path = ev / name
            if not path.exists() or not file_text(path).strip():
                failures.append(f"Missing required evidence file: {path}")
        if (ev / "qa-checklist.md").exists():
            failures.extend(gate_status_failures(ev / "qa-checklist.md", "QA"))
        if (ev / "pm-checklist.md").exists():
            failures.extend(gate_status_failures(ev / "pm-checklist.md", "PM"))
        for evidence_file in ev.glob("*.md"):
            evidence_text = file_text(evidence_file).lower()
            if "pending_agent_verification" in evidence_text:
                failures.append(f"Evidence still pending agent verification: {evidence_file}")
            if "generated by automation. agents should replace" in evidence_text:
                failures.append(f"Evidence placeholder was not replaced: {evidence_file}")
        test_text = file_text(ev / "test-evidence.md").lower()
        if ui_required:
            visual = ev / "visual-evidence.md"
            if not visual.exists():
                failures.append("UI change detected but visual-evidence.md is missing.")
            elif "pending_agent_verification" in file_text(visual).lower():
                failures.append(f"Visual evidence is still pending: {visual}")
    return failures



def required_layer_for_domains(domains: set[str]) -> str:
    if "database" in domains:
        return "database"
    if "backend" in domains:
        return "api"
    if "frontend" in domains:
        return "frontend"
    if "cloud" in domains:
        return "cloud"
    return ""


def validate_layer_gate(evidence_dirs: list[Path], layer: str) -> list[str]:
    if not layer:
        return []
    failures: list[str] = []
    for ev in evidence_dirs:
        # Expected shape: docs/agentic-evidence/<spec-id>/<task-id>
        parts = ev.parts
        try:
            idx = parts.index("agentic-evidence")
            spec_id = parts[idx + 1]
        except Exception:
            failures.append(f"Cannot infer spec id from evidence directory: {ev}")
            continue
        gate = Path("docs/agentic-evidence") / spec_id / "layer-gates" / f"{layer}.passed.md"
        text = file_text(gate)
        if not gate.exists() or "status: pass" not in text.lower():
            failures.append(f"Missing or non-passing {layer} layer gate evidence: {gate}")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", required=True)
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--ui-change", action="store_true")
    parser.add_argument("--aws-change", action="store_true")
    parser.add_argument("--skip-branch-conflict-check", action="store_true")
    parser.add_argument("--max-files", type=int, default=int(os.environ.get("AGENT_MAX_FILES_CHANGED", "35")))
    parser.add_argument("--good-lines", type=int, default=int(os.environ.get("AGENT_GOOD_LINES_CHANGED", "1200")))
    parser.add_argument("--max-lines", type=int, default=int(os.environ.get("AGENT_MAX_LINES_CHANGED", "5000")))
    parser.add_argument(
        "--advisory",
        action="store_true",
        default=os.environ.get("AGENT_PR_GUARDRAILS_ADVISORY", "false").lower() in {"1", "true", "yes"},
        help="Report guardrail findings without returning a failing exit code.",
    )
    args = parser.parse_args()

    failures: list[str] = []
    warnings: list[str] = []
    rows = changed_files(args.base)
    scope_paths = scope_paths_from_env()
    conflict_scope_paths = scope_paths_from_env("AGENTIC_CONFLICT_SCOPE_PATHS_JSON") or scope_paths
    if scope_paths:
        rows = [(status, path) for status, path in rows if path_within_scopes(path, scope_paths)]
    files = [p for _, p in rows]

    # Size guardrails are based on implementation files only. Runtime artifacts
    # and agent evidence can be large but should not force agents to throw away
    # useful QA/PM/test traces. Evidence still has its own quality checks below.
    runtime_files = [f for f in files if is_runtime_file(f)]
    reviewable_files = [f for f in files if not is_runtime_file(f)]
    evidence_files = [f for f in reviewable_files if f.startswith(EVIDENCE_PREFIXES)]
    implementation_files = [f for f in reviewable_files if not f.startswith(EVIDENCE_PREFIXES)]

    added, deleted = diff_stat_for_files(args.base, implementation_files)
    evidence_added, evidence_deleted = diff_stat_for_files(args.base, evidence_files)
    total_lines = added + deleted
    evidence_total_lines = evidence_added + evidence_deleted

    if len(implementation_files) > args.max_files:
        failures.append(f"Too many implementation files changed: {len(implementation_files)} > {args.max_files}. Split the PR.")
    if total_lines >= args.max_lines:
        failures.append(f"Too many implementation lines changed: {total_lines} >= {args.max_lines}. Split the PR.")
    elif total_lines > args.good_lines:
        warnings.append(
            f"Implementation diff is above the reviewability target: {total_lines} > {args.good_lines}. "
            f"This is allowed below the hard {args.max_lines} line limit, but should be split when practical."
        )

    allow_evidence_only = os.environ.get("AGENT_ALLOW_EVIDENCE_ONLY", "false").lower() in {"1", "true", "yes"}
    if is_evidence_only(files) and not allow_evidence_only:
        failures.append("PR only changes agent evidence/runtime files. Suppress this PR or add the actual one-responsibility implementation.")

    domains = responsibility_domains(implementation_files)
    allow_multi = os.environ.get("AGENT_ALLOW_MULTI_DOMAIN_PR", "false").lower() in {"1", "true", "yes"}
    if len(domains) > 1 and not allow_multi:
        failures.append(f"Multiple implementation domains changed in one PR: {sorted(domains)}. Split into one-responsibility PRs or explicitly approve override.")

    for status, path in rows:
        if status.startswith("D"):
            for protected in PROTECTED_DELETIONS:
                if path == protected or path.startswith(protected):
                    failures.append(f"Protected deletion blocked: {path}")

    evidence_dirs = evidence_dir_for(args.task_id)
    if not evidence_dirs:
        failures.append(f"Missing evidence directory for task {args.task_id}: docs/agentic-evidence/**/{args.task_id}")
    else:
        failures.extend(validate_evidence(evidence_dirs, ui_required=(args.ui_change or has_ui_change(files))))
        layer = required_layer_for_domains(domains)
        failures.extend(validate_layer_gate(evidence_dirs, layer))

    if has_api_change(files) and not has_test_change(files):
        failures.append("API/backend change detected but no test/integration/e2e file changed.")

    if not args.skip_branch_conflict_check and Path(".ai/scripts/branch_conflict_guard.py").exists():
        default_base = os.environ.get("AGENTIC_DEFAULT_BASE_BRANCH", "main")
        current_branch = run(["git", "rev-parse", "--abbrev-ref", "HEAD"], check=False).strip() or "HEAD"
        head_ref = os.environ.get("GITHUB_HEAD_REF") or current_branch
        conflict_cmd = [
            sys.executable,
            ".ai/scripts/branch_conflict_guard.py",
            "guard",
            "--mode", "pr",
            "--base", default_base,
            "--current-diff-base", args.base,
            "--exclude-branch", head_ref,
            "--exclude-branch", current_branch,
            "--exclude-branch", args.base,
            "--json-output", ".agent/branch-conflict/pr-guard.json",
            "--markdown-output", ".agent/branch-conflict/pr-guard.md",
        ]
        for path in conflict_scope_paths:
            conflict_cmd.extend(["--path", path])
        cp = subprocess.run(conflict_cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if cp.returncode != 0:
            failures.append("Branch conflict guard failed. This PR overlaps files changed or reserved by another active branch. See .agent/branch-conflict/pr-guard.md if available.")

    if not has_test_change(files):
        code_files = [f for f in files if Path(f).suffix.lower() in CODE_EXTENSIONS and not f.startswith(EVIDENCE_PREFIXES)]
        if code_files:
            failures.append("Code changed but no test file changed. Add tests or evidence explaining why not applicable.")

    report = {
        "files_changed": len(files),
        "implementation_files_changed": len(implementation_files),
        "evidence_files_changed": len(evidence_files),
        "runtime_files_changed": len(runtime_files),
        "implementation_lines_added": added,
        "implementation_lines_deleted": deleted,
        "evidence_lines_added": evidence_added,
        "evidence_lines_deleted": evidence_deleted,
        "lines_added": added,
        "lines_deleted": deleted,
        "domains": sorted(responsibility_domains(implementation_files)),
        "failures": failures,
        "warnings": warnings,
        "advisory": args.advisory,
        "files": files,
        "implementation_files": implementation_files,
        "evidence_files": evidence_files,
        "runtime_files": runtime_files,
    }
    print(json.dumps(report, indent=2))
    if args.advisory:
        return 0
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
