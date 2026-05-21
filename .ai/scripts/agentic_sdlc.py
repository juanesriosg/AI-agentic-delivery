#!/usr/bin/env python3
"""
Agentic SDLC Orchestrator v17

Repo-level automation for detecting ChatGPT-created specs in local or remote branches,
asking Codex local-mode agents to implement one-responsibility tasks, running
design-first architecture gates, DB → API → frontend layer gates, QA/PM gates, collecting evidence, avoiding cross-branch file conflicts, pushing validated implementation to the source spec branch, and opening concise final PRs for human review.

The script intentionally uses only the Python standard library. It shells out to
`git`, `gh`, and `codex` when those tools are available. Cloud mode is blocked unless explicitly requested.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import fnmatch
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import textwrap
import time
import threading
import queue
from dataclasses import dataclass, field
from pathlib import Path, PurePath
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

ROOT_MARKERS = [".git"]
DEFAULT_CONFIG_PATH = ".ai/automation/agentic.config.json"
DEFAULT_IGNORE_SPEC_PATTERNS = [
    "**/_TEMPLATE.*",
    "**/_TEMPLATE*",
    "**/template.*",
    "**/*.template.*",
    "**/.archived/**",
    "**/drafts/**",
    "**/README.md",
]
RUNTIME_EXCLUDE_ROOTS = {
    ".agent",
    ".venv",
    "venv",
    "node_modules",
    "vendor/bundle",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    "target",
    "dist",
    "build",
}
SHELL_SCRIPT_GLOBS = (
    ".ai/scripts/*.sh",
    ".ai/scripts/**/*.sh",
)
ISO = "%Y-%m-%dT%H:%M:%SZ"
DEFAULT_AGENT_TIMEOUT_SECONDS = 2 * 60 * 60
DEFAULT_ANALYSIS_AGENT_TIMEOUT_SECONDS = 60 * 60
DEFAULT_WRITE_AGENT_TIMEOUT_SECONDS = DEFAULT_AGENT_TIMEOUT_SECONDS
DEFAULT_MAX_TASKS_PER_SPEC = 50

LOG_LEVEL_BY_STATUS = {
    "completed": "SUCCESS",
    "done": "SUCCESS",
    "passed": "SUCCESS",
    "success": "SUCCESS",
    "warning": "WARNING",
    "warn": "WARNING",
    "skipped": "WARNING",
    "blocked": "ERROR",
    "failed": "ERROR",
    "failure": "ERROR",
    "error": "ERROR",
    "started": "INFO",
    "running": "INFO",
}


class OrchestratorError(RuntimeError):
    pass


class BranchConflictBlocked(OrchestratorError):
    """Raised when another active non-main branch already owns a needed file."""
    pass


class LayerDependencyBlocked(OrchestratorError):
    """Raised when a task cannot start because DB/API/frontend layer order is not satisfied."""
    pass


class TaskDependencyBlocked(OrchestratorError):
    """Raised when a task cannot start because its declared task dependencies are incomplete."""
    pass


class CodexAgentTimeout(OrchestratorError):
    """Raised when a nested Codex agent exceeds its stage timeout."""
    pass


def now_utc() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime(ISO)


def status_log_level(status: str) -> str:
    return LOG_LEVEL_BY_STATUS.get(str(status).strip().lower(), "INFO")


def stream_log_level(kind: str, summary: str) -> str:
    text = summary.lower()
    if kind == "stderr":
        if any(token in text for token in ("error", "traceback", "failed", "failure", "exception", "timed out")):
            return "ERROR"
        return "WARNING"
    if any(token in text for token in ("error", "traceback", "failed", "failure", "exception", "timed out")):
        return "ERROR"
    if any(token in text for token in ("warning", "warn", "blocked", "skipped")):
        return "WARNING"
    return "INFO"


def run(
    cmd: Sequence[str],
    cwd: Optional[Path] = None,
    check: bool = True,
    capture: bool = True,
    input_text: Optional[str] = None,
    env: Optional[Dict[str, str]] = None,
) -> subprocess.CompletedProcess[str]:
    merged_env = os.environ.copy()
    if env:
        merged_env.update(env)
    try:
        return subprocess.run(
            list(cmd),
            cwd=str(cwd) if cwd else None,
            check=check,
            text=True,
            encoding="utf-8",
            errors="replace",
            input=input_text,
            stdout=subprocess.PIPE if capture else None,
            stderr=subprocess.PIPE if capture else None,
            env=merged_env,
        )
    except subprocess.CalledProcessError as exc:
        msg = [f"Command failed: {' '.join(cmd)}"]
        if exc.stdout:
            msg.append("STDOUT:\n" + exc.stdout)
        if exc.stderr:
            msg.append("STDERR:\n" + exc.stderr)
        raise OrchestratorError("\n".join(msg)) from exc
    except FileNotFoundError as exc:
        raise OrchestratorError(
            "Executable not found while running command: "
            + " ".join(str(part) for part in cmd)
            + (f"\ncwd: {cwd}" if cwd else "")
        ) from exc
    except OSError as exc:
        raise OrchestratorError(
            "Could not start command: "
            + " ".join(str(part) for part in cmd)
            + (f"\ncwd: {cwd}" if cwd else "")
            + f"\n{exc}"
        ) from exc

def which(binary: str) -> Optional[str]:
    return shutil.which(binary)

def resolve_executable(binary: str, *, prefer_cmd_on_windows: bool = False) -> Optional[str]:
    """Resolve a command to a CreateProcess-safe executable path.

    npm installs both PowerShell and cmd shims on Windows. PowerShell can run
    `codex.ps1` interactively, but Python subprocess with shell=False needs a
    directly executable file, so prefer `codex.cmd` for Windows agent runs.
    """
    if os.name == "nt" and prefer_cmd_on_windows:
        path = PurePath(binary)
        if path.suffix.lower() == ".ps1":
            cmd_path = str(path.with_suffix(".cmd"))
            if os.path.exists(cmd_path):
                return cmd_path
            cmd_path = re.sub(r"(?i)\.ps1$", ".cmd", binary)
            if os.path.exists(cmd_path):
                return cmd_path
        if not path.suffix:
            for candidate in (f"{binary}.cmd", f"{binary}.exe", f"{binary}.bat"):
                found = shutil.which(candidate)
                if found:
                    return found
    found = shutil.which(binary)
    if os.name == "nt" and prefer_cmd_on_windows and found:
        found_path = PurePath(found)
        if found_path.suffix.lower() == ".ps1":
            cmd_path = str(found_path.with_suffix(".cmd"))
            if os.path.exists(cmd_path):
                return cmd_path
            cmd_path = re.sub(r"(?i)\.ps1$", ".cmd", found)
            if os.path.exists(cmd_path):
                return cmd_path
    return found


def repo_root(start: Optional[Path] = None) -> Path:
    current = (start or Path.cwd()).resolve()
    for candidate in [current, *current.parents]:
        if (candidate / ".git").exists():
            return candidate
    raise OrchestratorError("This command must run inside a Git repository.")


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8")


def append_jsonl(path: Path, value: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(value, sort_keys=True) + "\n")


def safe_slug(value: str, max_len: int = 64) -> str:
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9._/-]+", "-", value)
    value = value.replace("/", "-")
    value = re.sub(r"-+", "-", value).strip("-._")
    return (value or "task")[:max_len]


def compact_slug(value: str, *, prefix: str, slug_len: int = 24, hash_len: int = 8) -> str:
    """Return a short stable filesystem-safe id.

    Windows still fails in many repos when nested automation paths exceed the
    classic MAX_PATH boundary. Internal run/task folders must therefore be
    compact even when spec and task titles are long. Keep the human-readable
    slug small and preserve uniqueness with a hash.
    """
    slug = safe_slug(value, slug_len)
    digest = hashlib.sha256(value.encode("utf-8")).hexdigest()[:hash_len]
    return f"{prefix}-{digest}-{slug}"


def branch_matches(branch: str, patterns: Iterable[str]) -> bool:
    return any(fnmatch.fnmatch(branch, pat) for pat in patterns)


def path_matches(path: str, patterns: Iterable[str]) -> bool:
    normalized = path.replace("\\", "/")
    for pat in patterns:
        candidates = [pat]
        # Python fnmatch treats ** as ordinary globs; make repo-root files match
        # patterns such as specs/**/*.md as well as specs/foo/bar.md.
        candidates.append(pat.replace("**/", ""))
        if any(fnmatch.fnmatch(normalized, candidate) for candidate in candidates):
            return True
    return False


def parse_front_matter_simple(text: str) -> Tuple[Dict[str, str], str]:
    """Parse simple YAML-like front matter without requiring PyYAML."""
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}, text
    raw = text[4:end]
    body = text[end + 5:]
    data: Dict[str, str] = {}
    for line in raw.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or ":" not in stripped:
            continue
        key, value = stripped.split(":", 1)
        value = value.strip().strip('"').strip("'")
        if " #" in value:
            value = value.split(" #", 1)[0].strip()
        data[key.strip()] = value
    return data, body


def extract_spec_status(text: str, path: str = "") -> str:
    """Extract a simple readiness status from Markdown front matter or YAML specs.

    The parser intentionally avoids non-standard dependencies. It supports:
    - Markdown front matter: `status: ready_for_agents`
    - YAML-ish specs: `status: ready_for_agents`, including nested `spec.status`
    - Markdown body fallback: `**Status:** ready_for_agents`
    """
    front_matter, body = parse_front_matter_simple(text)
    candidates: List[str] = []
    for key in ("status", "spec_status", "agent_status", "implementation_status"):
        if front_matter.get(key):
            candidates.append(front_matter[key])
    search_text = text if path.lower().endswith((".yml", ".yaml")) else body
    for line in search_text.splitlines():
        m = re.match(r"^\s*(?:[-*]\s*)?(?:\*\*)?(?:status|spec_status|agent_status|implementation_status)(?:\*\*)?\s*[:=]\s*`?([^`#]+)`?", line, re.I)
        if m:
            candidates.append(m.group(1))
    if not candidates:
        m = re.search(r"\bstatus\b\s*[:=]\s*`?([A-Za-z0-9_.-]+)`?", text, re.I)
        if m:
            candidates.append(m.group(1))
    for value in candidates:
        cleaned = re.split(r"\s|,|;", value.strip().strip('\"\''), maxsplit=1)[0].strip().lower()
        if cleaned:
            return cleaned
    return ""


def normalize_spec_status(value: str) -> str:
    return value.strip().lower().replace("-", "_")


def extract_spec_title(text: str, path: str) -> str:
    """Prefer front-matter title; otherwise first markdown heading after front matter."""
    front, body = parse_front_matter_simple(text)
    for key in ("title", "name", "summary"):
        value = front.get(key) or front.get(key.replace("_", "-"))
        if value and "{{" not in value and "<" not in value:
            return value.strip()[:120]
    for line in body.splitlines():
        stripped = line.strip()
        if re.match(r"^#+\s+", stripped):
            candidate = stripped.lstrip("#").strip()
            if candidate and "{{" not in candidate and "<" not in candidate:
                return candidate[:120]
    return clean_spec_stem(path).replace("-", " ").replace("_", " ").title()


def strip_front_matter(text: str) -> str:
    return parse_front_matter_simple(text)[1]


def section_text(text: str, heading_keywords: Iterable[str]) -> str:
    """Extract markdown section text for simple heading keywords."""
    body = strip_front_matter(text)
    lines = body.splitlines()
    capture = False
    captured: List[str] = []
    start_level = 999
    keys = [k.lower() for k in heading_keywords]
    for line in lines:
        m = re.match(r"^(#+)\s+(.*)$", line.strip())
        if m:
            level = len(m.group(1))
            title = m.group(2).lower()
            if capture and level <= start_level:
                break
            if any(k in title for k in keys):
                capture = True
                start_level = level
                continue
        if capture:
            captured.append(line)
    return "\n".join(captured)



def section_is_explicitly_not_applicable(section: str) -> bool:
    """Return True when a spec section clearly says this layer is not in scope.

    This prevents fallback routing from creating database/API/cloud tasks merely
    because the spec template mentions those words while saying they are N/A.
    """
    low = re.sub(r"\s+", " ", section.lower()).strip()
    if not low:
        return False
    explicit_no_phrases = [
        "not applicable", "n/a", "no persistent", "no persistence",
        "does not persist", "does not create", "not in scope",
        "out of scope", "no database", "no db", "no new database",
        "no database schema", "no new database schema", "no schema change",
        "no schema changes", "no database changes", "database changes are not applicable",
        "no api", "no new api", "no api change", "no api changes",
        "api changes are not applicable", "no backend", "no backend change",
        "no backend changes", "no endpoint", "no aws", "no cloud",
        "no infrastructure", "no terraform", "no new aws",
        "no aws components", "no cloud components",
    ]
    return any(phrase in low for phrase in explicit_no_phrases)


def section_has_positive_signal(section: str, keywords: Iterable[str]) -> bool:
    low = section.lower()
    if section_is_explicitly_not_applicable(section):
        # If a section says N/A but also describes a future shape, do not treat
        # that future shape as current implementation scope.
        return False
    return any(keyword in low for keyword in keywords)


def cleaned_requirement_text(text: str) -> str:
    """Remove template placeholders/examples so fallback routing does not over-detect domains."""
    body = strip_front_matter(text)
    lines: List[str] = []
    skip_example = False
    for raw in body.splitlines():
        line = raw.strip()
        low = line.lower()
        if low.startswith("**example") or low.startswith("example:"):
            skip_example = True
            continue
        if skip_example and not line:
            skip_example = False
            continue
        if skip_example:
            continue
        if "{{" in line or "}}" in line:
            continue
        if "<" in line and ">" in line:
            continue
        lines.append(raw)
    return "\n".join(lines)


def is_template_spec_path(path: str) -> bool:
    """Return True for package templates/examples that must not trigger agents."""
    normalized = path.replace("\\", "/")
    lowered = normalized.lower()
    name = Path(normalized).name.lower()
    return (
        name.startswith("_template")
        or name.startswith("template.")
        or ".template." in name
        or "/examples/" in lowered
    )


def clean_spec_stem(path: str) -> str:
    name = Path(path).name
    lowered = name.lower()
    for suffix in [".agentic-spec.md", ".agentic-spec.yml", ".agentic-spec.yaml", ".spec.md", ".spec.yml", ".spec.yaml", ".md", ".yml", ".yaml", ".json"]:
        if lowered.endswith(suffix):
            return name[:-len(suffix)] or Path(path).stem
    return Path(path).stem


def is_runtime_or_generated_path(path: str) -> bool:
    normalized = path.replace("\\", "/")
    parts = [part for part in normalized.split("/") if part]
    return bool(parts) and (
        parts[0] in RUNTIME_EXCLUDE_ROOTS
        or "__pycache__" in parts
        or normalized.endswith(".pyc")
    )


def is_evidence_path(path: str, evidence_dir: str = "docs/agentic-evidence") -> bool:
    normalized = path.replace("\\", "/")
    return normalized.startswith(evidence_dir.strip("/") + "/")


def git(repo: Path, *args: str, check: bool = True) -> str:
    cp = run(["git", *args], cwd=repo, check=check, capture=True)
    return (cp.stdout or "").strip()


def split_nul_paths(value: str) -> List[str]:
    return [path for path in value.split("\0") if path]


def path_within_scopes(path: str, scopes: Iterable[str]) -> bool:
    normalized = path.replace("\\", "/").strip("/")
    for scope in scopes:
        normalized_scope = str(scope).replace("\\", "/").strip("/")
        if not normalized_scope:
            continue
        if normalized == normalized_scope or normalized.startswith(normalized_scope.rstrip("/") + "/"):
            return True
    return False


def git_changed_paths(repo: Path) -> List[str]:
    """Return tracked and untracked changed paths without ignored runtime files."""
    tracked = split_nul_paths(git(repo, "diff", "--name-only", "-z", "HEAD"))
    untracked = split_nul_paths(git(repo, "ls-files", "--others", "--exclude-standard", "-z"))
    paths = sorted(set(tracked + untracked))
    return [path for path in paths if not is_runtime_or_generated_path(path)]


def git_add_changed_paths(
    repo: Path,
    scopes: Optional[Iterable[str]] = None,
    exclude_paths: Optional[Iterable[str]] = None,
) -> List[str]:
    """Stage filtered changed paths without using ignored pathspec excludes.

    `git add -A -- . :(exclude).agent/**` still fails on some Git/Windows
    combinations when `.agent` is ignored, because Git validates the ignored
    pathspec before applying the exclusion. Build the add list explicitly so
    runtime artifacts are never passed to `git add`.
    """
    paths = git_changed_paths(repo)
    if scopes:
        paths = [path for path in paths if path_within_scopes(path, scopes)]
    if exclude_paths:
        excluded = {str(path).replace("\\", "/").strip("/") for path in exclude_paths if str(path).strip()}
        paths = [path for path in paths if path.replace("\\", "/").strip("/") not in excluded]
    if not paths:
        return []
    chunk_size = 100
    for start in range(0, len(paths), chunk_size):
        git(repo, "add", "-A", "--", *paths[start:start + chunk_size])
    return paths


def normalize_shell_script_line_endings(repo: Path) -> List[str]:
    """Ensure bash scripts can run from Windows-created git worktrees."""
    changed: List[str] = []
    candidates = set()
    for pattern in SHELL_SCRIPT_GLOBS:
        candidates.update(repo.glob(pattern))
    for path in sorted(candidates):
        if not path.is_file():
            continue
        data = path.read_bytes()
        if b"\r" not in data:
            continue
        path.write_bytes(data.replace(b"\r\n", b"\n").replace(b"\r", b"\n"))
        changed.append(path.relative_to(repo).as_posix())
    return changed


def gh(repo: Path, *args: str, check: bool = True) -> str:
    cp = run(["gh", *args], cwd=repo, check=check, capture=True)
    return (cp.stdout or "").strip()


def git_output_or_empty(repo: Path, *args: str) -> str:
    try:
        return git(repo, *args, check=True)
    except OrchestratorError:
        return ""


def short_sha(text: str, n: int = 12) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:n]


@dataclass
class SpecCandidate:
    branch: str
    path: str
    sha: str
    content: str
    status: str = ""

    @property
    def id(self) -> str:
        base = clean_spec_stem(self.path)
        # Evidence and task-completion markers must survive normal progress
        # updates to the spec file. The registry key still includes content SHA,
        # but the public spec id is stable for a branch/path pair.
        return f"spec-{short_sha(self.branch + ':' + self.path, 10)}-{safe_slug(base, 40)}"

    @property
    def title(self) -> str:
        return extract_spec_title(self.content, self.path)


@dataclass
class AgentTask:
    task_id: str
    title: str
    responsibility: str
    domain: str
    acceptance_criteria: List[str]
    risk: str = "medium"
    requires_local: bool = False
    requires_cloud: bool = False
    requires_terraform: bool = False
    requires_screenshots: bool = False
    requires_e2e: bool = False
    expected_paths: List[str] = field(default_factory=list)
    layer: str = "auto"
    depends_on: List[str] = field(default_factory=list)


class AgenticSDLC:
    def __init__(self, repo: Path, config_path: Optional[Path] = None, dry_run: bool = False, verbose: bool = False):
        self.repo = repo
        self.config_path = config_path or (repo / DEFAULT_CONFIG_PATH)
        self.config = self.load_config()
        self.dry_run = dry_run
        self.verbose = verbose
        self.state_dir = repo / self.config["repository"]["state_dir"]
        self.run_dir = repo / self.config["repository"]["run_dir"]
        self.worktree_dir = repo / self.config["repository"]["worktree_dir"]
        self.evidence_dir = repo / self.config["repository"].get("evidence_dir", "docs/agentic-evidence")
        self.registry_path = self.state_dir / "spec_registry.json"
        self.registry = read_json(self.registry_path, {"seen": {}, "runs": []})
        self.task_preexisting_changed_paths: Dict[Tuple[str, str], set[str]] = {}

    def load_config(self) -> Dict[str, Any]:
        default = {
            "manager": {"github_user": "", "timezone": "America/Bogota"},
            "repository": {
                "remote": "origin",
                "default_base_branch": "main",
                "allow_default_branch_fallback": True,
                "state_dir": ".agent/state",
                "run_dir": ".agent/runs",
                "worktree_dir": ".agent/worktrees",
                "evidence_dir": "docs/agentic-evidence",
                "commit_evidence": True,
                "retry_failed_specs": True,
                "skip_specs_with_existing_agent_branch": True,
                "short_internal_paths": True,
                "max_internal_slug_len": 24,
            },
            "spec_detection": {
                "watched_branches": ["dev/*", "spec/*", "chatgpt/*", "ai-spec/*", "feature/spec/*", "develop"],
                "spec_file_patterns": ["specs/**/*.md", ".ai/inbox/specs/**/*.md", ".codex/specs/**/*.md"],
                "ignore_file_patterns": DEFAULT_IGNORE_SPEC_PATTERNS,
                "ready_statuses": ["ready_for_agents", "ready", "approved", "implementation_ready"],
                "process_specs_without_status": True,
            },
            "branching": {
                "implementation_branch_prefix": "ai",
                "base_pr_to_source_spec_branch": True,
                "push_tasks_to_source_spec_branch": False,
                "run_tasks_in_current_worktree": False,
                "create_task_prs": True,
                "create_final_pr_from_spec_branch": False,
                "final_pr_base_branch": "main",
                "qa_user_branch_prefix": "qa-user",
                "prod_ready_branch_prefix": "prod-ready",
            },
            "branch_conflict": {
                "enabled": True,
                "default_base_branch": "main",
                "write_path_leases": True,
                "commit_path_leases": True,
                "push_path_leases": True,
                "block_on_overlap": True,
                "continue_with_next_task_when_blocked": True,
                "ignore_patterns": [
                    "docs/agentic-evidence/**",
                    "docs/agentic-path-leases/**",
                    ".agent/**"
                ]
            },
            "design_first": {
                "enabled": True,
                "block_implementation_without_design": True,
                "required_sections": [
                    "business need", "requirements", "design", "architecture",
                    "data model", "api contract", "cloud", "testing strategy",
                    "layer order", "paradigm", "acceptance criteria"
                ],
                "allow_explicit_not_applicable": True,
                "design_report_dir": ".agent/design-gates"
            },
            "layer_gates": {
                "enabled": True,
                "strict_db_api_front_order": True,
                "database_before_api": True,
                "api_before_frontend": True,
                "block_frontend_if_api_missing": True,
                "block_api_if_database_missing": True,
                "pass_file_dir": "docs/agentic-evidence/{spec_id}/layer-gates",
                "order": ["design", "cloud", "database", "api", "backend", "frontend", "qa", "pm", "release"],
                "merge_required_for_next_layer": True,
                "allow_contract_only_parallelism": False
            },
            "codex": {
                "binary": "codex",
                "sandbox": "danger-full-access",
                "approval_policy": "never",
                "json_events": True,
                "model": "gpt-5.5",
                "reasoning_effort": "xhigh",
                "reasoning_summary": "concise",
                "verbosity": "high",
                "cloud_requires_explicit_request": True,
                "default_runtime_mode": "local",
                "allow_missing_codex_for_dry_run": True,
            },
            "execution": {
                "max_specs_per_run": 1,
                "max_tasks_per_spec": DEFAULT_MAX_TASKS_PER_SPEC,
                "retry_failed_specs": True,
                "agent_timeout_max_seconds": DEFAULT_AGENT_TIMEOUT_SECONDS,
                "analysis_agent_timeout_seconds": DEFAULT_ANALYSIS_AGENT_TIMEOUT_SECONDS,
                "write_agent_timeout_seconds": DEFAULT_WRITE_AGENT_TIMEOUT_SECONDS,
                "analysis_stage_failures_block_task": False,
                "readonly_agents_in_isolated_worktree": True,
            },
            "pr_policy": {
                "open_as_draft": True,
                "block_placeholder_evidence": True,
                "block_evidence_only_pr": True,
            },
            "agents": {},
        }
        if self.config_path.exists():
            user_config = json.loads(self.config_path.read_text(encoding="utf-8"))
            return deep_merge(default, user_config)
        return default

    def log(self, message: str) -> None:
        print(message, flush=True)

    def log_status(self, level: str, message: str) -> None:
        self.log(f"[{level.upper()}] {message}")

    def log_info(self, message: str) -> None:
        self.log_status("INFO", message)

    def log_success(self, message: str) -> None:
        self.log_status("SUCCESS", message)

    def log_warning(self, message: str) -> None:
        self.log_status("WARNING", message)

    def log_error(self, message: str) -> None:
        self.log_status("ERROR", message)

    def debug(self, message: str) -> None:
        if self.verbose:
            print(f"[debug] {message}", flush=True)

    def doctor(self) -> int:
        checks = []
        checks.append(("git", which("git") is not None))
        checks.append(("gh", which("gh") is not None))
        checks.append(("codex", resolve_executable(str(self.config["codex"].get("binary", "codex")), prefer_cmd_on_windows=True) is not None))
        checks.append(("repo", (self.repo / ".git").exists()))
        checks.append(("config", self.config_path.exists()))
        try:
            branch = git(self.repo, "rev-parse", "--abbrev-ref", "HEAD")
            clean = git(self.repo, "status", "--porcelain") == ""
        except OrchestratorError:
            branch, clean = "unknown", False
        print("Agentic SDLC doctor")
        print(f"repo: {self.repo}")
        print(f"branch: {branch}")
        print(f"working tree clean: {clean}")
        for name, ok in checks:
            print(f"{'OK' if ok else 'MISSING'}  {name}")
        print("\nNext commands:")
        print("  python .ai/scripts/agentic_sdlc.py scan")
        print("  python .ai/scripts/agentic_sdlc.py --dry-run run-once --max-specs 1")
        print("  python .ai/scripts/agentic_sdlc.py watch --mode local")
        return 0 if all(ok for _, ok in checks if _ != "codex") else 1

    def remote_name(self) -> str:
        return str(self.config["repository"].get("remote", "origin"))

    def remote_available(self) -> bool:
        return bool(git_output_or_empty(self.repo, "remote", "get-url", self.remote_name()))

    def fetch(self) -> None:
        remote = self.remote_name()
        if not self.remote_available():
            self.log(f"Remote {remote!r} is not configured. Using local branches only.")
            return
        self.log(f"Fetching remote branches from {remote}...")
        git(self.repo, "fetch", remote, "--prune")

    def list_remote_branches(self) -> List[str]:
        remote = self.remote_name()
        if not self.remote_available():
            return []
        output = git_output_or_empty(self.repo, "ls-remote", "--heads", remote)
        branches: List[str] = []
        for line in output.splitlines():
            if not line.strip():
                continue
            ref = line.split()[-1]
            if ref.startswith("refs/heads/"):
                branches.append(ref[len("refs/heads/"):])
        patterns = self.config["spec_detection"]["watched_branches"]
        return sorted([b for b in branches if branch_matches(b, patterns)])

    def list_local_branches(self) -> List[str]:
        output = git_output_or_empty(self.repo, "for-each-ref", "--format=%(refname:short)", "refs/heads")
        patterns = self.config["spec_detection"]["watched_branches"]
        branches = [line.strip() for line in output.splitlines() if line.strip()]
        return sorted([b for b in branches if branch_matches(b, patterns)])

    def list_candidate_branches(self) -> List[str]:
        remote_branches = self.list_remote_branches()
        return remote_branches if remote_branches else self.list_local_branches()

    def ref_for_branch(self, branch: str) -> str:
        remote = self.remote_name()
        remote_ref = f"{remote}/{branch}"
        if git_output_or_empty(self.repo, "rev-parse", "--verify", "--quiet", remote_ref):
            return remote_ref
        if self.remote_available() and git_output_or_empty(self.repo, "ls-remote", "--heads", remote, branch):
            return remote_ref
        return branch

    def spec_ignore_patterns(self) -> List[str]:
        return list(DEFAULT_IGNORE_SPEC_PATTERNS) + list(self.config["spec_detection"].get("ignore_file_patterns", [])) + [
            "**/_TEMPLATE*",
            "**/*_TEMPLATE*",
            "**/*.template.*",
            "**/*.example.*",
            "**/example-*",
            ".ai/examples/**",
        ]

    def list_specs_in_branch(self, branch: str) -> List[SpecCandidate]:
        ref = self.ref_for_branch(branch)
        names = git_output_or_empty(self.repo, "ls-tree", "-r", "--name-only", ref).splitlines()
        spec_patterns = self.config["spec_detection"]["spec_file_patterns"]
        ignore_patterns = self.spec_ignore_patterns()
        specs: List[SpecCandidate] = []
        for name in names:
            if not path_matches(name, spec_patterns):
                continue
            if is_template_spec_path(name) or path_matches(name, ignore_patterns):
                self.debug(f"Ignoring non-implementation spec file: {branch}:{name}")
                continue
            content = git_output_or_empty(self.repo, "show", f"{ref}:{name}")
            if not content.strip():
                continue
            sha = short_sha(content, 40)
            specs.append(SpecCandidate(branch=branch, path=name, sha=sha, content=content, status=extract_spec_status(content, name)))
        return specs

    def get_spec_candidate(self, branch: str, spec_path: str, fetch: bool = True) -> SpecCandidate:
        if fetch:
            self.fetch()
        spec_path = spec_path.replace("\\", "/")
        spec_patterns = self.config["spec_detection"]["spec_file_patterns"]
        ignore_patterns = self.spec_ignore_patterns()
        if not path_matches(spec_path, spec_patterns):
            raise OrchestratorError(f"Spec path is not watched by config: {spec_path}")
        if is_template_spec_path(spec_path) or path_matches(spec_path, ignore_patterns):
            raise OrchestratorError(f"Spec path is intentionally ignored: {spec_path}")
        ref = self.ref_for_branch(branch)
        content = git_output_or_empty(self.repo, "show", f"{ref}:{spec_path}")
        if not content.strip() and (self.repo / spec_path).exists():
            content = (self.repo / spec_path).read_text(encoding="utf-8", errors="replace")
        if not content.strip():
            raise OrchestratorError(f"Could not read spec {spec_path} from {ref} or working tree")
        sha = short_sha(content, 40)
        return SpecCandidate(branch=branch, path=spec_path, sha=sha, content=content, status=extract_spec_status(content, spec_path))

    def scan(self, fetch: bool = True) -> List[SpecCandidate]:
        if fetch:
            self.fetch()
        found: List[SpecCandidate] = []
        branches = self.list_candidate_branches()
        if not branches:
            self.log("No watched branches found. Create/push a branch such as dev/<feature> with specs/<feature>.spec.md.")
        for branch in branches:
            found.extend(self.list_specs_in_branch(branch))
        print(f"Found {len(found)} spec candidate(s).")
        for spec in found:
            seen_key = self.registry_key(spec)
            registry_status = "new" if seen_key not in self.registry.get("seen", {}) else "seen"
            normalized_status = normalize_spec_status(spec.status or "")
            if normalized_status == "completed":
                readiness = "completed"
            elif self.is_spec_ready(spec):
                readiness = "ready" if self.validate_spec_candidate(spec) else "not-ready:validation-failed"
            else:
                readiness = f"not-ready:{spec.status or 'no-status'}"
            print(f"- [{registry_status}/{readiness}] {spec.branch}:{spec.path} ({spec.id})")
        return found

    def is_spec_ready(self, spec: SpecCandidate) -> bool:
        """Return whether a spec should be implemented automatically.

        Draft/on-hold specs are intentionally ignored. By default a spec must
        explicitly declare an implementation-ready status such as
        `ready_for_agents`. Requiring this status prevents copied templates,
        experiments, and partially written specs from triggering autonomous work.
        """
        cfg = self.config.get("spec_detection", {})
        status = normalize_spec_status(spec.status or "")
        if not status:
            return bool(cfg.get("process_specs_without_status", False))
        blocked = {"template", "draft", "completed", "done", "blocked", "on_hold", "hold", "paused", "clarification_needed", "needs_clarification", "cancelled", "canceled", "archived"}
        if status in blocked:
            return False
        ready_statuses = {normalize_spec_status(str(x)) for x in cfg.get("ready_statuses", ["ready_for_agents", "ready", "approved"])}
        return status in ready_statuses

    def validate_spec_candidate(self, spec: SpecCandidate) -> bool:
        """Run the repo spec validator against branch content before coding.

        This blocks copied templates, unresolved placeholders, missing files-to-touch,
        or weak acceptance criteria even when the file path and status look valid.
        Validation artifacts are stored under .agent/state and ignored by git.
        """
        if not bool(self.config.get("spec_detection", {}).get("validate_before_implementation", True)):
            return True
        validator = self.repo / ".ai/scripts/validate_agentic_spec.py"
        if not validator.exists():
            self.debug("Spec validator not found; skipping structural validation.")
            return True
        suffixes = ''.join(Path(spec.path).suffixes) or ".md"
        validation_dir = self.state_dir / "spec-validation"
        validation_dir.mkdir(parents=True, exist_ok=True)
        temp_spec = validation_dir / f"{safe_slug(spec.id, 80)}{suffixes}"
        write_text(temp_spec, spec.content)
        allowed = [str(x) for x in self.config.get("spec_detection", {}).get("ready_statuses", ["ready_for_agents"])]
        cmd = [sys.executable, str(validator), str(temp_spec), "--format", "json"]
        for status in allowed:
            cmd.extend(["--allow-status", status])
        cp = run(cmd, cwd=self.repo, check=False, capture=True)
        report_path = validation_dir / f"{safe_slug(spec.id, 80)}.validation.json"
        write_text(report_path, cp.stdout or "[]")
        if cp.returncode != 0:
            message = cp.stdout.strip() or cp.stderr.strip() or "validation failed"
            self.log(f"Spec validation failed for {spec.branch}:{spec.path}; skipping autonomous implementation. Report: {report_path.relative_to(self.repo)}")
            if self.verbose:
                self.log(message)
            return False
        try:
            data = json.loads(cp.stdout or "[]")
            if data and not data[0].get("passed", False):
                self.log(f"Spec validation did not pass for {spec.branch}:{spec.path}; skipping autonomous implementation. Report: {report_path.relative_to(self.repo)}")
                return False
        except json.JSONDecodeError:
            self.log(f"Spec validation output was not JSON for {spec.branch}:{spec.path}; skipping autonomous implementation. Report: {report_path.relative_to(self.repo)}")
            return False
        return True

    def registry_key(self, spec: SpecCandidate) -> str:
        return f"{spec.branch}:{spec.path}:{spec.sha}"

    def new_specs(self, specs: List[SpecCandidate]) -> List[SpecCandidate]:
        seen = self.registry.get("seen", {})
        retry_failed = bool(self.config.get("execution", {}).get("retry_failed_specs", self.config["repository"].get("retry_failed_specs", True)))
        skip_existing_agent_branch = bool(self.config["repository"].get("skip_specs_with_existing_agent_branch", True))
        fresh: List[SpecCandidate] = []
        for spec in specs:
            if not self.is_spec_ready(spec):
                normalized_status = normalize_spec_status(spec.status or "")
                if normalized_status == "completed":
                    self.debug(f"Skipping {spec.id}: spec is already completed")
                else:
                    self.debug(f"Skipping {spec.id}: spec status is not ready ({spec.status or 'no-status'})")
                continue
            if not self.validate_spec_candidate(spec):
                continue
            key = self.registry_key(spec)
            item = seen.get(key)
            if item and not (retry_failed and item.get("status") in {"failed", "blocked"}):
                continue
            if skip_existing_agent_branch and self.existing_agent_branch_for_spec(spec):
                self.debug(f"Skipping {spec.id}: existing agent branch found")
                continue
            fresh.append(spec)
        return fresh

    def existing_agent_branch_for_spec(self, spec: SpecCandidate) -> bool:
        remote = self.config["repository"].get("remote", "origin")
        branch_prefix = self.config.get("branching", {}).get("implementation_branch_prefix", "ai")
        title_slug = safe_slug(spec.title, 32)
        local_pattern = f"{branch_prefix}/{title_slug}/"
        local = git_output_or_empty(self.repo, "for-each-ref", "--format=%(refname:short)", "refs/heads")
        if any(line.startswith(local_pattern) for line in local.splitlines()):
            return True
        if not self.remote_available():
            return False
        pattern = f"refs/heads/{branch_prefix}/{title_slug}/*"
        out = git_output_or_empty(self.repo, "ls-remote", "--heads", remote, pattern)
        return bool(out.strip())

    def mark_spec_seen(self, spec: SpecCandidate, status: str, run_id: str) -> None:
        key = self.registry_key(spec)
        self.registry.setdefault("seen", {})[key] = {
            "branch": spec.branch,
            "path": spec.path,
            "sha": spec.sha,
            "spec_id": spec.id,
            "status": status,
            "run_id": run_id,
            "updated_at": now_utc(),
        }
        self.registry.setdefault("runs", []).append({
            "run_id": run_id,
            "spec_id": spec.id,
            "branch": spec.branch,
            "path": spec.path,
            "status": status,
            "updated_at": now_utc(),
        })
        write_json(self.registry_path, self.registry)

    def run_once(self, mode: str, max_specs: Optional[int] = None, fetch: bool = True) -> int:
        self.ensure_cloud_explicit(mode)
        candidates = self.scan(fetch=fetch)
        new = self.new_specs(candidates)
        if not new:
            self.log_info("No new specs to implement.")
            return 0
        limit = max_specs or int(self.config["execution"].get("max_specs_per_run", 1))
        failures = 0
        for spec in new[:limit]:
            try:
                if not self.implement_spec(spec, mode=mode):
                    failures += 1
            except Exception as exc:
                failures += 1
                run_id = self.make_run_id(spec, prefix="fail")
                if not self.dry_run:
                    self.mark_spec_seen(spec, status="failed", run_id=run_id)
                print(f"[ERROR] processing {spec.id}: {exc}", file=sys.stderr)
                if self.verbose:
                    raise
        return 1 if failures else 0

    def push_tasks_to_source_spec_branch(self) -> bool:
        """When enabled, each validated task commit is pushed directly to the source spec branch.

        This supports the desired POC workflow:
        GPT-created spec branch -> Codex implements -> same branch receives code -> final PR to base.
        The default remains task-branch PRs for teams that want one PR per task.
        """
        return bool(self.config.get("branching", {}).get("push_tasks_to_source_spec_branch", False))

    def run_tasks_in_current_worktree(self) -> bool:
        """Run task agents in the visible checkout instead of hidden detached worktrees.

        This is useful for local Windows development where the manager expects
        generated code/evidence to appear immediately in the IDE. The explicit
        environment override lets one-off runs opt in without editing config.
        """
        env_value = os.environ.get("AGENTIC_RUN_IN_CURRENT_WORKTREE", "").strip().lower()
        if env_value:
            return env_value in {"1", "true", "yes", "on"}
        return bool(self.config.get("branching", {}).get("run_tasks_in_current_worktree", False))

    def create_final_pr_from_spec_branch_enabled(self) -> bool:
        return bool(self.config.get("branching", {}).get("create_final_pr_from_spec_branch", False))

    def final_pr_base_branch(self) -> str:
        return str(self.config.get("branching", {}).get("final_pr_base_branch") or self.config.get("repository", {}).get("default_base_branch", "main"))

    def refresh_source_branch_ref(self, branch: str) -> None:
        remote = self.remote_name()
        if self.remote_available():
            git(self.repo, "fetch", remote, f"{branch}:refs/remotes/{remote}/{branch}", "--force", check=False)

    def compact_paths_enabled(self) -> bool:
        return bool(self.config.get("repository", {}).get("short_internal_paths", True))

    def make_run_id(self, spec: SpecCandidate, prefix: str = "run") -> str:
        if not self.compact_paths_enabled():
            return f"{spec.id}-{int(time.time())}"
        seed = f"{spec.branch}:{spec.path}:{spec.sha}:{int(time.time())}"
        return compact_slug(seed, prefix=prefix, slug_len=10, hash_len=10)

    def make_task_run_id(self, spec: SpecCandidate, task: AgentTask) -> str:
        if not self.compact_paths_enabled():
            return f"{spec.id}-{task.task_id}-{int(time.time())}"
        seed = f"{spec.branch}:{spec.path}:{spec.sha}:{task.task_id}:{int(time.time())}"
        return compact_slug(seed, prefix="tsk", slug_len=10, hash_len=10)

    def task_dir_name(self, task: AgentTask) -> str:
        if not self.compact_paths_enabled():
            return task.task_id
        return compact_slug(task.task_id, prefix="t", slug_len=int(self.config.get("repository", {}).get("max_internal_slug_len", 24)), hash_len=8)

    def implement_spec(self, spec: SpecCandidate, mode: str, mark_seen: bool = True) -> bool:
        run_id = self.make_run_id(spec)
        story_dir = self.run_dir / run_id
        story_dir.mkdir(parents=True, exist_ok=True)
        write_text(story_dir / "spec.md", spec.content)
        write_json(story_dir / "metadata.json", {
            "run_id": run_id,
            "spec_id": spec.id,
            "title": spec.title,
            "source_branch": spec.branch,
            "spec_path": spec.path,
            "mode": mode,
            "started_at": now_utc(),
        })
        self.write_agent_log(story_dir, "orchestrator", "spec_detected", "started", f"Detected spec {spec.path} in {spec.branch}")
        self.log_info(f"Implementing spec {spec.id}: {spec.title}")
        self.run_design_gate_for_spec(spec, story_dir, mode=mode)
        tasks = self.plan_tasks(spec, story_dir, mode=mode)
        if not tasks:
            raise OrchestratorError(f"Planning produced no tasks for {spec.id}")
        tasks = self.order_tasks_by_layer(tasks)
        max_tasks = int(self.config["execution"].get("max_tasks_per_spec", DEFAULT_MAX_TASKS_PER_SPEC))
        selected_tasks = tasks[:max_tasks]
        if len(tasks) > len(selected_tasks):
            self.log_warning(
                f"Task run limited to {len(selected_tasks)}/{len(tasks)} tasks by execution.max_tasks_per_spec={max_tasks}."
            )
        else:
            self.log_info(f"Task run will process all {len(selected_tasks)} planned task(s).")
        blocked = 0
        completed = 0
        completed_task_ids = {
            task.task_id
            for task in tasks
            if self.push_tasks_to_source_spec_branch() and self.task_completed_in_source_branch(spec, task)
        }
        for task in selected_tasks:
            result = self.run_task_pipeline(spec, task, story_dir, mode=mode, completed_task_ids=completed_task_ids)
            if result == "blocked":
                blocked += 1
            else:
                completed += 1
                completed_task_ids.add(task.task_id)
            if self.push_tasks_to_source_spec_branch():
                self.refresh_source_branch_ref(spec.branch)
        if self.push_tasks_to_source_spec_branch() and completed > 0 and blocked == 0:
            self.create_final_pr_from_spec_branch(spec, story_dir, mode=mode)
        if mark_seen and not self.dry_run:
            self.mark_spec_seen(spec, status=("blocked" if blocked else "processed"), run_id=run_id)
        summary = f"Processed {completed} task(s); blocked {blocked} task(s) waiting for layer gates"
        self.write_agent_log(story_dir, "orchestrator", "spec_processed", "completed" if blocked == 0 else "blocked", summary)
        if blocked:
            self.log_error(f"Spec incomplete: {summary}. Run artifacts: {story_dir}")
            return False
        self.log_success(f"Spec complete: {summary}. Run artifacts: {story_dir}")
        return True

    def plan_tasks(self, spec: SpecCandidate, story_dir: Path, mode: str) -> List[AgentTask]:
        plan_path = story_dir / "plan.json"
        deterministic = self.plan_tasks_from_task_list(spec)
        if deterministic:
            write_json(plan_path, {"tasks": [task.__dict__ for task in deterministic], "source": "task_list_progress"})
            self.write_agent_log(story_dir, "spec-task-splitter", "local_plan_created", "completed", f"Created {len(deterministic)} tasks from task-list progress")
            return deterministic
        prompt = self.render_prompt(
            agent_file=self.config["agents"].get("planning", "spec-task-splitter.agent.md"),
            title="Split this spec into one-responsibility agent tasks",
            body=f"""
            You are planning implementation for a repo-level agentic SDLC.

            Runtime mode: {mode}
            Source branch: {spec.branch}
            Spec path: {spec.path}
            Spec id: {spec.id}

            Create a task breakdown with one responsibility per PR. Prefer separate tasks for architecture/design, data model/database, API/backend, frontend, cloud/Terraform, security, QA, PM acceptance, and release only when they are actually needed.

            Mandatory planning rule:
            - Design and architecture must be clear before implementation.
            - Database/data model tasks must complete and pass DB integration gates before API tasks.
            - API/backend tasks must complete and pass API integration/contract gates before frontend tasks.
            - Frontend may use mocks for early component tests only, but it cannot be marked integrated or done until real API integration/E2E evidence exists.
            - Use data-driven, object-oriented, or event-driven programming only after explaining why that paradigm fits this task.

            Write the machine-readable plan to:
            {plan_path.relative_to(self.repo)}

            Required JSON shape:
            {{
              "tasks": [
                {{
                  "task_id": "short-kebab-id",
                  "title": "concise task title",
                  "responsibility": "one sentence responsibility",
                  "domain": "frontend|backend|database|cloud|security|design|qa|pm|release|fullstack",
                  "acceptance_criteria": ["..."],
                  "risk": "low|medium|high",
                  "requires_local": false,
                  "requires_cloud": false,
                  "requires_terraform": false,
                  "requires_screenshots": false,
                  "requires_e2e": false,
                  "expected_paths": ["src/path-or-directory-needed-by-this-task"],
                  "layer": "design|database|api|frontend|cloud|qa|pm|release|crosscutting",
                  "depends_on": ["task-id-that-must-be-merged-or-gated-first"]
                }}
              ]
            }}

            Do not implement yet. Only analyze and plan.
            Every task must include expected_paths when possible. These paths are used to prevent two active branches from touching the same file.

            SPEC:
            {spec.content}
            """,
        )
        write_text(story_dir / "prompts" / "planning.md", prompt)
        self.call_codex(prompt, cwd=self.repo, run_dir=story_dir, agent="spec-task-splitter", mode=mode, allow_write=True)
        if plan_path.exists():
            data = read_json(plan_path, {})
            parsed = self.parse_tasks(data)
            if parsed:
                self.write_agent_log(story_dir, "spec-task-splitter", "plan_created", "completed", f"Created {len(parsed)} tasks")
                return parsed
        fallback = self.fallback_plan(spec)
        write_json(plan_path, {"tasks": [task.__dict__ for task in fallback], "fallback": True})
        self.write_agent_log(story_dir, "spec-task-splitter", "fallback_plan_created", "completed", "Created fallback plan because no valid plan.json was produced")
        return fallback

    def split_task_progress_items(self, spec: SpecCandidate) -> List[Tuple[bool, str, str]]:
        progress = section_text(spec.content, ["agentic split task progress", "split task progress"])
        if not progress.strip():
            return []
        items: List[Tuple[bool, str, str]] = []
        for raw_line in progress.splitlines():
            match = re.match(r"^\s*[-*]\s+\[([ xX])\]\s+(.+?)\s*$", raw_line)
            if not match:
                continue
            checked = match.group(1).lower() == "x"
            text = match.group(2).strip()
            code = re.search(r"`([^`]+)`", text)
            if code:
                task_id = safe_slug(code.group(1), 48)
                title = text[code.end():].strip(" -:\t") or task_id.replace("-", " ").title()
            else:
                task_id = safe_slug(text, 48)
                title = text
            items.append((checked, task_id, title))
        return items

    def completed_split_task_ids_from_text(self, text: str) -> set[str]:
        ids: set[str] = set()
        for pattern in (
            r"Completed task id:\s*`([^`]+)`",
            r"Task id:\s*`([^`]+)`",
        ):
            for match in re.finditer(pattern, text, re.I):
                ids.add(safe_slug(match.group(1), 48))
        progress = section_text(text, ["agentic split task progress", "split task progress"])
        for raw_line in progress.splitlines():
            match = re.match(r"^\s*[-*]\s+\[([ xX])\]\s+(.+?)\s*$", raw_line)
            if not match or match.group(1).lower() != "x":
                continue
            code = re.search(r"`([^`]+)`", match.group(2))
            ids.add(safe_slug(code.group(1) if code else match.group(2), 48))
        return ids

    def is_worker_wrapper_task_list(self, spec: SpecCandidate) -> bool:
        front_matter, _ = parse_front_matter_simple(spec.content)
        if normalize_spec_status(front_matter.get("doc_type", "")) != "task_list":
            return False
        markers = " ".join(
            [
                spec.path,
                front_matter.get("title", ""),
                front_matter.get("source_trd", ""),
                spec.title,
            ]
        ).lower()
        return (
            "worker-wrapper-artifacts" in markers
            or "worker wrapper and artifact contract" in markers
        )

    def canonical_worker_wrapper_split_items(self, spec: SpecCandidate) -> List[Tuple[bool, str, str]]:
        if not self.is_worker_wrapper_task_list(spec):
            return []
        checked_ids = self.completed_split_task_ids_from_text(spec.content)
        canonical = [
            ("worker-wrapper-design-gate", "Clarify worker wrapper design"),
            ("artifact-manifest-contract", "Add artifact manifest contract"),
            ("worker-wrapper-cli", "Add wrapper CLI"),
            ("cdp-security-runtime-guard", "Guard CDP exposure"),
            ("local-fixture-worker-mode", "Add local fixture worker mode"),
            ("container-entrypoint-alignment", "Align container entrypoint"),
            ("worker-wrapper-qa-evidence", "Validate wrapper evidence"),
            ("worker-wrapper-pm-pr-notice", "Prepare PM PR notice"),
        ]
        return [(task_id in checked_ids, task_id, title) for task_id, title in canonical]

    def plan_tasks_from_task_list(self, spec: SpecCandidate) -> List[AgentTask]:
        """Create a deterministic plan when a task-list can be split locally."""
        items = self.canonical_worker_wrapper_split_items(spec) or self.split_task_progress_items(spec)
        if not items:
            return []
        tasks: List[AgentTask] = []
        previous_id: Optional[str] = None
        for checked, task_id, title in items:
            depends = [previous_id] if previous_id else []
            previous_id = task_id
            task = self.agent_task_from_split_item(spec, task_id, title, depends)
            if checked and not self.checked_split_task_needs_replay(spec, task):
                continue
            tasks.append(task)
        return tasks

    def checked_split_task_needs_replay(self, spec: SpecCandidate, task: AgentTask) -> bool:
        """Return true for a checked task whose source-branch evidence is incomplete.

        A task-list checkbox is usually enough to skip completed work. In
        source-spec mode, however, a failed rerun can leave a checkbox and task
        marker on the branch without the layer-gate PASS artifact. In that case
        the task must be planned again so it can commit the missing scoped
        artifacts and unblock downstream DB/API/frontend layers.
        """
        if not self.push_tasks_to_source_spec_branch():
            return False
        if not self.task_completed_in_source_branch_by_id(spec, task.task_id):
            return False
        return not self.task_completed_in_source_branch(spec, task)

    def agent_task_from_split_item(self, spec: SpecCandidate, task_id: str, title: str, depends_on: List[str]) -> AgentTask:
        blueprint = self.worker_wrapper_task_blueprint(task_id)
        if blueprint:
            return AgentTask(
                task_id=task_id,
                title=blueprint["title"],
                responsibility=blueprint["responsibility"],
                domain=blueprint["domain"],
                layer=blueprint["layer"],
                depends_on=depends_on,
                acceptance_criteria=list(blueprint["acceptance_criteria"]),
                risk=blueprint.get("risk", "medium"),
                requires_local=bool(blueprint.get("requires_local", True)),
                requires_cloud=bool(blueprint.get("requires_cloud", False)),
                requires_terraform=bool(blueprint.get("requires_terraform", False)),
                requires_screenshots=bool(blueprint.get("requires_screenshots", False)),
                requires_e2e=bool(blueprint.get("requires_e2e", False)),
                expected_paths=list(blueprint.get("expected_paths", [])),
            )

        lowered = f"{task_id} {title}".lower()
        domain = "fullstack"
        layer = "crosscutting"
        requires_screenshots = False
        requires_e2e = False
        requires_terraform = False
        if any(word in lowered for word in ["database", "db", "data model", "manifest", "artifact"]):
            domain, layer = "database", "database"
        if any(word in lowered for word in ["api", "backend", "python", "wrapper", "cli"]):
            domain, layer = "backend", "api"
        if (
            any(word in lowered for word in ["frontend", "react", "page", "screen"])
            or re.search(r"\b(ui|front-end)\b", lowered)
        ):
            domain, layer = "frontend", "frontend"
            requires_screenshots = True
            requires_e2e = True
        if any(word in lowered for word in ["cloud", "container", "docker", "terraform", "aws", "entrypoint"]):
            domain, layer = "cloud", "cloud"
            requires_terraform = "terraform" in lowered
        if any(word in lowered for word in ["security", "cdp"]):
            domain, layer = "security", "crosscutting"
        if "qa" in lowered:
            domain, layer = "qa", "qa"
        if any(word in lowered for word in ["pm", "product", "notice", "pr-notice"]):
            domain, layer = "pm", "pm"

        return AgentTask(
            task_id=task_id,
            title=title,
            responsibility=f"Complete the split task `{task_id}` with one responsibility and repo-native tests/evidence.",
            domain=domain,
            layer=layer,
            depends_on=depends_on,
            acceptance_criteria=[
                f"`{task_id}` satisfies its mapped requirements in the task list.",
                "Relevant tests or explicit blocker evidence are recorded.",
                "QA and PM evidence accurately reflect pass, blocked, or not-applicable status.",
            ],
            risk="medium",
            requires_local=True,
            requires_terraform=requires_terraform,
            requires_screenshots=requires_screenshots,
            requires_e2e=requires_e2e,
            expected_paths=self.extract_expected_paths_from_spec(spec),
        )

    def worker_wrapper_task_blueprint(self, task_id: str) -> Dict[str, Any]:
        blueprints: Dict[str, Dict[str, Any]] = {
            "artifact-manifest-contract": {
                "title": "Add artifact manifest contract",
                "responsibility": "Define and test the local artifact manifest data shape and attempt-specific output path rules without adding persistent database schema.",
                "domain": "backend",
                "layer": "database",
                "acceptance_criteria": [
                    "Manifest builder records batch_id, target_id, attempt, run_id, local_run_dir, output_s3_prefix, status, metrics_path, quality_report_path, clean_records_path, rejected_records_path, diagnostics_paths, and required result artifact paths.",
                    "Manifest path construction preserves attempt identity and cannot overwrite prior attempts for the same batch_id and target_id.",
                    "Artifact discovery covers config.json, status.txt, metrics.json, quality_report.md, properties_master_clean.jsonl, rejected_records.jsonl, quality_flags.csv, domain_diagnostics.csv, image_diagnostics.csv, and results/** when present.",
                    "Unit or contract tests validate manifest generation, required and missing artifact handling, and output prefix construction using local fixtures only.",
                    "Layer-gate evidence states that no migration, DynamoDB table, S3 bucket, AWS resource, or Terraform change is created by this task.",
                ],
                "expected_paths": [
                    "city_pipelines/cloud/__init__.py",
                    "city_pipelines/cloud/artifacts.py",
                    "city_pipelines/cloud/tests/test_artifact_manifest_contract.py",
                    "city_pipelines/cloud/tests/fixtures/artifact_run/",
                    "docs/agentic-evidence/SPEC-20260519-city-pipeline-aws-cost-mvp/P0-F1-T1/layer-gates/database.md",
                ],
            },
            "worker-wrapper-cli": {
                "title": "Add wrapper CLI",
                "responsibility": "Implement the cloud-safe worker CLI and environment parsing that invokes city_pipelines/run_city.py without changing local pipeline semantics.",
                "domain": "backend",
                "layer": "api",
                "acceptance_criteria": [
                    "Wrapper reads BATCH_ID, TARGET_ID, CONFIG_S3_URI, OUTPUT_S3_PREFIX, ATTEMPT, AWS_REGION, egress mode, and dry-run/local options from environment variables or explicit CLI flags with deterministic precedence.",
                    "Wrapper invokes the existing city_pipelines/run_city.py path with --mode headless and --stop-chrome for real worker execution while keeping direct local run_city.py usage available.",
                    "Wrapper emits structured JSON logs containing batch_id, target_id, attempt, region, egress_mode, run_id, local_run_dir, artifact manifest path, and artifact paths.",
                    "Wrapper maps unrecoverable worker failures to a non-zero exit code and machine-readable failure reason without hiding subprocess errors.",
                    "Unit tests cover environment parsing, CLI flag overrides, run_city command construction, structured log fields, and failure reason mapping without requiring AWS credentials.",
                ],
                "expected_paths": [
                    "city_pipelines/cloud/config.py",
                    "city_pipelines/cloud/logging.py",
                    "city_pipelines/cloud/worker.py",
                    "city_pipelines/cloud/tests/test_worker_wrapper_cli.py",
                    "docs/agentic-evidence/SPEC-20260519-city-pipeline-aws-cost-mvp/P0-F1-T1/layer-gates/api.md",
                ],
            },
            "cdp-security-runtime-guard": {
                "title": "Guard CDP exposure",
                "responsibility": "Verify and, if needed, harden the worker runtime so Chrome/CDP is not publicly exposed in the cloud wrapper path.",
                "domain": "security",
                "layer": "crosscutting",
                "acceptance_criteria": [
                    "Security evidence inspects city_pipelines/common/pipeline.py, city_pipelines/common/scripts/**, the wrapper command path, and Dockerfile.city-pipeline for CDP binding or exposed-port behavior.",
                    "If implementation changes are needed, the cloud wrapper path binds CDP to a non-public interface or documents why container networking keeps it non-public without changing existing local run semantics.",
                    "Tests or static assertions cover the effective Chrome/CDP command or wrapper guard for the cloud execution path.",
                    "Evidence confirms Dockerfile.city-pipeline does not expose a public CDP port and no new public port mapping is introduced.",
                    "Rollback guidance is recorded for any security hardening changes and compatibility with --mode headless --stop-chrome is preserved.",
                ],
                "expected_paths": [
                    "city_pipelines/cloud/security.py",
                    "city_pipelines/cloud/tests/test_cdp_security_runtime_guard.py",
                    "city_pipelines/common/pipeline.py",
                    "city_pipelines/common/scripts/",
                    "Dockerfile.city-pipeline",
                    "docs/agentic-evidence/SPEC-20260519-city-pipeline-aws-cost-mvp/P0-F1-T1/security-review.md",
                ],
            },
            "local-fixture-worker-mode": {
                "title": "Add local fixture worker mode",
                "responsibility": "Add the local fixture or dry-run-compatible worker mode and tests that produce a manifest without AWS credentials or real S3 calls.",
                "domain": "backend",
                "layer": "api",
                "requires_e2e": True,
                "acceptance_criteria": [
                    "Local fixture mode can run from CLI flags or environment variables without AWS credentials and without network calls to S3.",
                    "Fixture execution stages or reuses a local config, creates an attempt-specific local output identity, and writes an artifact manifest using the manifest contract.",
                    "Tests verify local fixture behavior, missing fixture/config failures, manifest content, structured logs, and no-AWS adapter behavior.",
                    "Evidence includes at least one generated artifact manifest example under the P0-F1-T1 evidence path.",
                    "Any gap in full Docker smoke feasibility is documented with the exact command a later QA task should run.",
                ],
                "expected_paths": [
                    "city_pipelines/cloud/local_adapter.py",
                    "city_pipelines/cloud/tests/test_local_fixture_worker_mode.py",
                    "city_pipelines/cloud/tests/fixtures/worker_config/",
                    "docs/agentic-evidence/SPEC-20260519-city-pipeline-aws-cost-mvp/P0-F1-T1/artifact-manifest-example.json",
                ],
            },
            "container-entrypoint-alignment": {
                "title": "Align container entrypoint",
                "responsibility": "Update or document the container entrypoint path only as needed so AWS Batch can call the wrapper while direct local worker behavior remains available.",
                "domain": "cloud",
                "layer": "cloud",
                "requires_e2e": True,
                "acceptance_criteria": [
                    "Dockerfile.city-pipeline is inspected after the wrapper exists and either updated to expose the wrapper command or evidence records the exact Batch command override that should be used instead.",
                    "Any Dockerfile or dependency change is limited to worker entrypoint/runtime needs and does not introduce Terraform, AWS resources, production deployment, or broad package churn.",
                    "Container-level validation evidence includes a local Docker smoke command when feasible, or a documented blocker/gap with a manual verification command.",
                    "The task confirms no public CDP port is exposed by the container image and no P0 NAT/proxy/external-provider behavior is introduced.",
                    "Rollback notes explain how to return to the previous direct run_city.py entrypoint or command override.",
                ],
                "expected_paths": [
                    "Dockerfile.city-pipeline",
                    "requirements-city-pipeline.txt",
                    "docs/agentic-evidence/SPEC-20260519-city-pipeline-aws-cost-mvp/P0-F1-T1/docker-smoke.md",
                ],
            },
            "worker-wrapper-qa-evidence": {
                "title": "Validate wrapper evidence",
                "responsibility": "Run layered validation and collect QA evidence showing each FR, NFR, and AC is satisfied or explicitly documented as a gap.",
                "domain": "qa",
                "layer": "qa",
                "risk": "low",
                "requires_e2e": True,
                "acceptance_criteria": [
                    "test-evidence.md records spec-quality, test-matrix, targeted unit tests, local fixture or dry-run smoke, and Docker smoke results when feasible.",
                    "qa-checklist.md maps FR-001 through FR-005, NFR-REL-001, NFR-SEC-001, AC-001, AC-002, and AC-003 to concrete validation evidence or an explicit gap.",
                    "QA evidence confirms frontend visual and accessibility testing are non-applicable because this task has no UI.",
                    "QA evidence confirms Terraform plan/apply, real AWS S3, DynamoDB, Batch, and production deployment are non-applicable or blocked for this task.",
                    "Self-review and scale/security architecture review outputs are captured and any in-scope findings are routed back to the responsible implementation task before QA passes.",
                ],
                "expected_paths": [
                    "docs/agentic-evidence/SPEC-20260519-city-pipeline-aws-cost-mvp/P0-F1-T1/agents.log.md",
                    "docs/agentic-evidence/SPEC-20260519-city-pipeline-aws-cost-mvp/P0-F1-T1/qa-checklist.md",
                    "docs/agentic-evidence/SPEC-20260519-city-pipeline-aws-cost-mvp/P0-F1-T1/scale-security-architecture-review.md",
                    "docs/agentic-evidence/SPEC-20260519-city-pipeline-aws-cost-mvp/P0-F1-T1/test-evidence.md",
                ],
            },
            "worker-wrapper-pm-pr-notice": {
                "title": "Prepare PM PR notice",
                "responsibility": "Prepare the PM acceptance checklist and PR notification for the worker wrapper/artifact contract without requesting approval before the Codex review gate.",
                "domain": "pm",
                "layer": "pm",
                "risk": "low",
                "acceptance_criteria": [
                    "pm-checklist.md verifies the business outcome: the worker can be tested locally, has a cloud-style CLI/environment contract, produces complete attempt-specific artifact evidence, and preserves local pipeline behavior.",
                    "pr-notification.md includes scope, why it changed, validation, risk, rollback plan, assumptions, follow-ups, quality score, files worth review, and links to P0-F1-T1 evidence.",
                    "PR notification explicitly states that no AWS infrastructure, Terraform, production deploy, persistent database schema, HTTP API, or frontend UI was changed.",
                    "PR notification records that human manager approval must wait for the required Agentic Codex PR Review / codex_review_gate status check.",
                    "PM evidence records any unresolved gaps from local Docker smoke or real AWS validation as follow-up items rather than marking cloud integration complete.",
                ],
                "expected_paths": [
                    "docs/agentic-evidence/SPEC-20260519-city-pipeline-aws-cost-mvp/P0-F1-T1/pm-checklist.md",
                    "docs/agentic-evidence/SPEC-20260519-city-pipeline-aws-cost-mvp/P0-F1-T1/pr-notification.md",
                ],
            },
        }
        return blueprints.get(task_id, {})

    def parse_tasks(self, data: Dict[str, Any]) -> List[AgentTask]:
        raw_tasks = data.get("tasks", []) if isinstance(data, dict) else []
        tasks: List[AgentTask] = []
        for index, item in enumerate(raw_tasks):
            if not isinstance(item, dict):
                continue
            task_id = safe_slug(str(item.get("task_id") or item.get("id") or f"task-{index+1}"), 48)
            title = str(item.get("title") or task_id.replace("-", " ").title())
            responsibility = str(item.get("responsibility") or title)
            domain = safe_slug(str(item.get("domain") or "fullstack"), 24)
            ac = item.get("acceptance_criteria") or item.get("acceptanceCriteria") or []
            if isinstance(ac, str):
                ac = [ac]
            raw_paths = item.get("expected_paths") or item.get("files_to_touch") or item.get("paths") or []
            if isinstance(raw_paths, str):
                raw_paths = [raw_paths]
            raw_depends = item.get("depends_on") or item.get("dependsOn") or []
            if isinstance(raw_depends, str):
                raw_depends = [raw_depends]
            tasks.append(AgentTask(
                task_id=task_id,
                title=title,
                responsibility=responsibility,
                domain=domain,
                acceptance_criteria=[str(x) for x in ac],
                risk=str(item.get("risk") or "medium"),
                requires_local=bool(item.get("requires_local", False)),
                requires_cloud=bool(item.get("requires_cloud", False)),
                requires_terraform=bool(item.get("requires_terraform", False)),
                requires_screenshots=bool(item.get("requires_screenshots", False)),
                requires_e2e=bool(item.get("requires_e2e", False)),
                expected_paths=[str(x).strip() for x in raw_paths if str(x).strip()],
                layer=safe_slug(str(item.get("layer") or item.get("domain") or "auto"), 24),
                depends_on=[safe_slug(str(x), 48) for x in raw_depends if str(x).strip()],
            ))
        return tasks


    def extract_expected_paths_from_spec(self, spec: SpecCandidate) -> List[str]:
        """Extract likely implementation paths from a spec's files-to-touch section."""
        files_section = section_text(spec.content, ["files", "areas to touch", "expected files", "paths"])
        candidates: List[str] = []
        for raw in files_section.splitlines():
            candidates.extend(re.findall(r"`([^`]+)`", raw))
            if "|" in raw:
                for cell in raw.split("|"):
                    cell = cell.strip()
                    if re.search(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.*/-]+", cell):
                        candidates.append(cell)
        cleaned: List[str] = []
        for item in candidates:
            item = item.strip().strip("`\"\'.,;:()[]{}")
            if not item or item.lower() in {"path", "path / pattern", "src/...", "tests/..."}:
                continue
            if "<" in item and ">" in item:
                continue
            if item.startswith(("http://", "https://")):
                continue
            if any(ch.isspace() for ch in item):
                continue
            if not any(token in item for token in ["/", "*", "."]):
                continue
            cleaned.append(item.replace("\\", "/"))
        return sorted(set(cleaned))

    def task_layer(self, task: AgentTask) -> str:
        explicit = (task.layer or "auto").lower()
        if explicit and explicit != "auto":
            if explicit == "backend":
                return "api"
            if explicit == "db":
                return "database"
            return explicit
        domain = task.domain.lower()
        if domain in {"db", "database"}:
            return "database"
        if domain in {"api", "backend"}:
            return "api"
        if domain in {"front", "frontend", "ui", "design"}:
            return "frontend"
        if domain in {"cloud", "infra"} or task.requires_terraform:
            return "cloud"
        if domain in {"qa", "test"}:
            return "qa"
        if domain == "pm":
            return "pm"
        if domain == "release":
            return "release"
        return "crosscutting"

    def order_tasks_by_layer(self, tasks: List[AgentTask]) -> List[AgentTask]:
        configured = self.config.get("layer_gates", {}).get("order", [])
        order = {name: idx for idx, name in enumerate(configured)}
        original_index = {task.task_id: index for index, task in enumerate(tasks)}

        def rank(task: AgentTask) -> Tuple[int, int, str]:
            return (order.get(self.task_layer(task), 50), original_index.get(task.task_id, 9999), task.task_id)

        # Explicit task dependencies are stronger than broad layer ordering.
        # Use layer order only as a tie-breaker among currently ready tasks.
        remaining = list(tasks)
        ordered: List[AgentTask] = []
        remaining_ids = {task.task_id for task in remaining}
        while remaining:
            ready = [
                task for task in remaining
                if all(dep not in remaining_ids for dep in task.depends_on)
            ]
            if not ready:
                # Cycles or unknown dependency ids should not make planning
                # nondeterministic. Keep the remaining layer order; the runtime
                # dependency preflight will block unsafe tasks before agents run.
                ordered.extend(sorted(remaining, key=rank))
                break
            ready.sort(key=rank)
            for task in ready:
                ordered.append(task)
                remaining.remove(task)
                remaining_ids.remove(task.task_id)
        return ordered

    def spec_mentions_layer(self, spec: SpecCandidate, layer: str) -> bool:
        """Infer whether the spec requires a real implementation layer.

        The inference intentionally prefers explicit design sections and files-to-touch
        over generic text, because a good spec often says "API: Not applicable"
        or "Database: Not applicable" while still mentioning those words.
        """
        content = cleaned_requirement_text(spec.content)
        lower = content.lower()
        files_section = section_text(content, ["files and areas to touch", "files", "expected files", "paths"])

        if layer == "database":
            data_section = section_text(content, ["data model design", "data model", "database design", "database", "db"])
            if section_is_explicitly_not_applicable(data_section):
                return any(k in files_section.lower() for k in ["migration", "database/", "db/", "schema", "repository", ".sql", "prisma", "sequelize", "typeorm"])
            return section_has_positive_signal(data_section, ["schema", "table", "migration", "repository", "sql", "dynamodb", "rds", "persistent", "entity", "model"]) or any(k in files_section.lower() for k in ["migration", "database/", "db/", "schema", ".sql", "prisma", "sequelize", "typeorm"])

        if layer == "api":
            api_section = section_text(content, ["api contract", "api", "backend", "endpoint", "contract requirements"])
            if section_is_explicitly_not_applicable(api_section):
                return any(k in files_section.lower() for k in ["api/", "backend/", "controller", "lambda", "handler"])
            api_file_signals = ["api/", "backend/", "controller", "lambda", "handler", "routes/api", "api-route", "api_route"]
            return section_has_positive_signal(api_section, ["endpoint", "api route", "request", "response", "controller", "handler", "graphql", "rest", "lambda", "backend service"]) or any(k in files_section.lower() for k in api_file_signals)

        if layer == "frontend":
            ui_section = section_text(content, ["design / ux", "ux", "ui", "frontend", "screen", "user scenarios"])
            if section_is_explicitly_not_applicable(ui_section):
                return any(k in files_section.lower() for k in ["frontend", "component", "page", "app/", "src/", "screen", "ui/"])
            return section_has_positive_signal(ui_section, ["form", "screen", "page", "component", "button", "input", "visual", "accessibility", "layout", "user-facing"]) or any(k in files_section.lower() for k in ["frontend", "component", "page", "app/", "src/", "screen", "ui/"])

        return False

    def source_branch_has_layer_pass(self, spec: SpecCandidate, layer: str) -> bool:
        pass_dir_template = self.config.get("layer_gates", {}).get("pass_file_dir", "docs/agentic-evidence/{spec_id}/layer-gates")
        pass_dir = pass_dir_template.format(spec_id=spec.id)
        ref = self.ref_for_branch(spec.branch)
        candidates = [
            f"{pass_dir}/{layer}.passed.json",
            f"{pass_dir}/{layer}.passed.md",
            f"{pass_dir}/{layer}-passed.json",
            f"{pass_dir}/{layer}-passed.md",
        ]
        for candidate in candidates:
            if git_output_or_empty(self.repo, "cat-file", "-e", f"{ref}:{candidate}") == "":
                # git cat-file returns no stdout both for success and failure; verify with show.
                shown = git_output_or_empty(self.repo, "show", f"{ref}:{candidate}")
                if shown.strip() and "PASS" in shown.upper():
                    return True
        # Fallback: if no generated pass files exist yet, accept explicit source-branch evidence only.
        evidence = git_output_or_empty(self.repo, "show", f"{ref}:docs/agentic-evidence/{spec.id}/layer-gates/{layer}.passed.md")
        return bool(evidence.strip() and "PASS" in evidence.upper())

    def task_completion_path_for_id(self, spec: SpecCandidate, task_id: str) -> Path:
        return Path(self.config["repository"].get("evidence_dir", "docs/agentic-evidence")) / spec.id / safe_slug(task_id, 48) / "task-completed.md"

    def task_completed_in_source_branch_by_id(self, spec: SpecCandidate, task_id: str) -> bool:
        """Return true when the source branch already contains a completion marker for a task id."""
        ref = self.ref_for_branch(spec.branch)
        rel = str(self.task_completion_path_for_id(spec, task_id)).replace("\\", "/")
        out = git_output_or_empty(self.repo, "show", f"{ref}:{rel}")
        return bool(out.strip())

    def task_marked_completed_in_spec(self, spec: SpecCandidate, task_id: str) -> bool:
        """Return true when the task document marks a split task as completed.

        This is a compatibility bridge for older runs that changed spec content
        before task-completion markers used stable spec ids.
        """
        wanted = safe_slug(task_id, 48)
        if wanted in self.completed_split_task_ids_from_text(spec.content):
            return True
        for raw_line in spec.content.splitlines():
            line = raw_line.strip()
            if not re.match(r"^[-*]\s+\[x\]\s+", line, flags=re.I):
                continue
            code_ids = [safe_slug(value, 48) for value in re.findall(r"`([^`]+)`", line)]
            if wanted in code_ids:
                return True
            checkbox_text = re.sub(r"^[-*]\s+\[x\]\s+", "", line, flags=re.I)
            if wanted in safe_slug(checkbox_text, 160).split("-"):
                return True
            if wanted in safe_slug(checkbox_text, 160):
                return True
        return False

    def ensure_task_dependencies_satisfied(
        self,
        spec: SpecCandidate,
        task: AgentTask,
        story_dir: Path,
        task_dir: Path,
        completed_task_ids: Optional[Iterable[str]] = None,
    ) -> None:
        completed = {safe_slug(task_id, 48) for task_id in (completed_task_ids or [])}
        missing: List[str] = []
        for dependency in task.depends_on:
            dep = safe_slug(dependency, 48)
            if dep in completed:
                continue
            if self.task_completed_in_source_branch_by_id(spec, dep):
                continue
            if self.task_marked_completed_in_spec(spec, dep):
                continue
            missing.append(dep)
        if not missing:
            if task.depends_on:
                self.write_agent_log(story_dir, "layer-sequencing-orchestrator", "task_dependency_preflight", "completed", f"{task.task_id} dependencies satisfied: {', '.join(task.depends_on)}")
            return
        msg = (
            f"Task {task.task_id} is blocked because declared task dependencies are not complete on `{spec.branch}`: "
            + ", ".join(missing)
            + ". Complete those earlier split tasks first; dependent tasks must not start agent implementation or evidence collection."
        )
        write_text(task_dir / "task-dependency-blocked.md", msg + "\n")
        raise TaskDependencyBlocked(msg)

    def required_previous_layers(self, spec: SpecCandidate, task: AgentTask) -> List[str]:
        cfg = self.config.get("layer_gates", {})
        if not bool(cfg.get("enabled", True)):
            return []
        layer = self.task_layer(task)
        required: List[str] = []
        if layer == "api" and bool(cfg.get("database_before_api", True)) and self.spec_mentions_layer(spec, "database"):
            required.append("database")
        if layer == "frontend" and bool(cfg.get("api_before_frontend", True)) and self.spec_mentions_layer(spec, "api"):
            required.append("api")
            if self.spec_mentions_layer(spec, "database"):
                required.append("database")
        return required

    def ensure_layer_dependencies_satisfied(self, spec: SpecCandidate, task: AgentTask, story_dir: Path, task_dir: Path) -> None:
        cfg = self.config.get("layer_gates", {})
        if not bool(cfg.get("enabled", True)):
            return
        layer = self.task_layer(task)
        required = self.required_previous_layers(spec, task)
        missing = [prev for prev in required if not self.source_branch_has_layer_pass(spec, prev)]
        if not missing:
            self.write_agent_log(story_dir, "layer-sequencing-orchestrator", "layer_dependency_preflight", "completed", f"{task.task_id} layer={layer}; dependencies satisfied")
            return
        msg = (
            f"Task {task.task_id} layer={layer} is blocked because the source branch `{spec.branch}` does not yet contain passed layer gate evidence for: "
            + ", ".join(missing)
            + ". Complete and push/pass the previous layer gate on the source spec branch first, then the watcher can continue this task."
        )
        write_text(task_dir / "layer-dependency-blocked.md", msg + "\n")
        raise LayerDependencyBlocked(msg)

    def run_design_gate_for_spec(self, spec: SpecCandidate, story_dir: Path, mode: str) -> None:
        cfg = self.config.get("design_first", {})
        if not bool(cfg.get("enabled", True)):
            return
        script = self.repo / ".ai/scripts/design_gate.py"
        if not script.exists():
            self.debug("design_gate.py not found; skipping design-first gate")
            return
        report_dir = story_dir / "design-gate"
        report_dir.mkdir(parents=True, exist_ok=True)
        temp_spec = report_dir / Path(spec.path).name
        write_text(temp_spec, spec.content)
        cmd = [sys.executable, str(script), "--spec", str(temp_spec), "--format", "json", "--markdown-output", str(report_dir / "design-gate.md")]
        if bool(cfg.get("allow_explicit_not_applicable", True)):
            cmd.append("--allow-not-applicable")
        cp = run(cmd, cwd=self.repo, check=False, capture=True)
        write_text(report_dir / "design-gate.json", cp.stdout or "{}")
        if cp.returncode != 0 and bool(cfg.get("block_implementation_without_design", True)):
            self.write_agent_log(story_dir, "architecture-design-lead", "design_gate_failed", "blocked", f"Spec design is not implementation-ready. See {report_dir.relative_to(self.repo)}")
            raise OrchestratorError(f"Design-first gate failed for {spec.branch}:{spec.path}. See {report_dir / 'design-gate.md'}")
        self.write_agent_log(story_dir, "architecture-design-lead", "design_gate_passed", "completed", f"Design-first gate passed for {spec.path}")

    def run_layer_gate(self, worktree: Path, spec: SpecCandidate, task: AgentTask, story_dir: Path, task_dir: Path) -> None:
        cfg = self.config.get("layer_gates", {})
        if not bool(cfg.get("enabled", True)):
            return
        script = worktree / ".ai/scripts/layer_gate.py"
        if not script.exists():
            self.debug("layer_gate.py not found; skipping layer gate")
            return
        layer = self.task_layer(task)
        evidence_rel = Path(self.config["repository"].get("evidence_dir", "docs/agentic-evidence")) / spec.id / task.task_id
        out_dir = Path(self.config.get("layer_gates", {}).get("pass_file_dir", "docs/agentic-evidence/{spec_id}/layer-gates").format(spec_id=spec.id))
        cmd = [
            sys.executable, str(script),
            "--layer", layer,
            "--spec-id", spec.id,
            "--task-id", task.task_id,
            "--evidence-dir", str(evidence_rel),
            "--pass-dir", str(out_dir),
            "--write-pass-file",
            "--format", "json",
            "--markdown-output", str(task_dir / "layer-gate.md"),
        ]
        if task.requires_screenshots:
            cmd.append("--ui-change")
        if task.requires_terraform or task.domain in {"cloud", "infra"}:
            cmd.append("--cloud-change")
        if self.dry_run:
            self.log(f"    DRY-RUN would run {' '.join(cmd)}")
            return
        cp = run(cmd, cwd=worktree, check=False, capture=True)
        write_text(task_dir / "layer-gate.json", cp.stdout or "{}")
        if cp.returncode != 0:
            raise OrchestratorError(f"Layer gate failed for {task.task_id} ({layer}). See {task_dir / 'layer-gate.md'}")
        self.write_agent_log(story_dir, "dependency-gate-qa", "layer_gate_passed", "completed", f"{layer} gate passed for {task.task_id}")

    def fallback_plan(self, spec: SpecCandidate) -> List[AgentTask]:
        active = cleaned_requirement_text(spec.content)
        lower = active.lower()
        files_section = section_text(spec.content, ["files", "areas to touch", "expected files"]).lower()
        cloud_section = section_text(spec.content, ["aws", "cloud", "infrastructure"]).lower()
        expected_paths = self.extract_expected_paths_from_spec(spec)
        requires_front = self.spec_mentions_layer(spec, "frontend")
        requires_api = self.spec_mentions_layer(spec, "api")
        requires_db = self.spec_mentions_layer(spec, "database")
        requires_screenshots = any(k in lower for k in ["ui", "form", "screen", "page", "frontend", "button", "input", "visual", "accessibility"])
        explicit_no_cloud = any(k in cloud_section or k in lower for k in [
            "does this require new aws components? | no", "must infrastructure be changed? | no",
            "touches_cloud_or_aws: false", "new_aws_components: false", "terraform_required: false",
            "terraform required? | no", "no new aws", "no aws", "no cloud", "no new cloud",
            "no new infrastructure", "no infrastructure expected", "must infrastructure be changed? no"
        ])
        explicit_yes_cloud = any(k in cloud_section or k in lower for k in [
            "does this require new aws components? | yes", "must infrastructure be changed? | yes",
            "touches_cloud_or_aws: true", "new_aws_components: true", "terraform_required: true", "terraform required? | yes"
        ])
        cloud_keywords = ["lambda", "dynamodb", "ec2", "rds", "api gateway", "cloudwatch", "s3 bucket", "aws component", "aws resource", ".tf", "terraform/"]
        path_cloud = any(k in files_section for k in ["infra/", "terraform/", ".tf", "cloudformation", "cdk/"])
        requires_terraform = explicit_yes_cloud or ((not explicit_no_cloud) and (path_cloud or any(k in cloud_section for k in cloud_keywords)))
        tasks: List[AgentTask] = []
        if requires_terraform:
            tasks.append(AgentTask(
                task_id=f"{safe_slug(clean_spec_stem(spec.path), 32)}-cloud",
                title=f"{spec.title} - cloud/Terraform foundation",
                responsibility="Create or update cloud infrastructure using Terraform only.",
                domain="cloud",
                layer="cloud",
                acceptance_criteria=["Terraform changes are scoped", "terraform fmt/validate/plan evidence exists", "No raw AWS mutating CLI is used"],
                requires_terraform=True,
                expected_paths=[p for p in expected_paths if any(x in p.lower() for x in ["infra", "terraform", ".tf", "cloudformation", "cdk"])] or expected_paths,
            ))
        if requires_db:
            tasks.append(AgentTask(
                task_id=f"{safe_slug(clean_spec_stem(spec.path), 32)}-database",
                title=f"{spec.title} - data model/database",
                responsibility="Implement the data model, schema/repository behavior, and database tests first.",
                domain="database",
                layer="database",
                acceptance_criteria=["Data model is explicit", "DB unit and integration tests pass", "Migration/rollback is documented when applicable"],
                expected_paths=[p for p in expected_paths if any(x in p.lower() for x in ["database", "migration", "model", "repository", "schema", "db"])] or expected_paths,
            ))
        if requires_api:
            depends = [tasks[-1].task_id] if requires_db and tasks else []
            tasks.append(AgentTask(
                task_id=f"{safe_slug(clean_spec_stem(spec.path), 32)}-api",
                title=f"{spec.title} - API/backend contract",
                responsibility="Implement the API/backend behavior after the database layer is validated.",
                domain="backend",
                layer="api",
                depends_on=depends,
                acceptance_criteria=["API contract is documented", "API unit tests pass", "DB-backed integration/API contract tests pass"],
                expected_paths=[p for p in expected_paths if any(x in p.lower() for x in ["api", "backend", "controller", "route", "service", "lambda"])] or expected_paths,
            ))
        if requires_front:
            depends = []
            if requires_api:
                depends.append(f"{safe_slug(clean_spec_stem(spec.path), 32)}-api")
            if requires_db:
                depends.append(f"{safe_slug(clean_spec_stem(spec.path), 32)}-database")
            tasks.append(AgentTask(
                task_id=f"{safe_slug(clean_spec_stem(spec.path), 32)}-frontend",
                title=f"{spec.title} - frontend/UI",
                responsibility="Implement the frontend only after real API integration is available on the source branch.",
                domain="frontend",
                layer="frontend",
                depends_on=depends,
                acceptance_criteria=["Component tests pass", "Visual/accessibility evidence exists", "E2E validates the real API flow"],
                requires_screenshots=requires_screenshots,
                requires_e2e=True,
                expected_paths=[p for p in expected_paths if any(x in p.lower() for x in ["frontend", "src", "component", "page", "app", "ui"])] or expected_paths,
            ))
        if not tasks:
            tasks.append(AgentTask(
                task_id=safe_slug(clean_spec_stem(spec.path), 48),
                title=spec.title,
                responsibility="Implement the spec with the smallest coherent one-responsibility PR possible.",
                domain="fullstack",
                layer="crosscutting",
                acceptance_criteria=["Spec acceptance criteria are satisfied", "Relevant tests pass", "QA and PM gates are documented"],
                requires_screenshots=requires_screenshots,
                requires_terraform=requires_terraform,
                requires_e2e=requires_screenshots,
                expected_paths=expected_paths,
            ))
        return tasks

    def run_task_pipeline(
        self,
        spec: SpecCandidate,
        task: AgentTask,
        story_dir: Path,
        mode: str,
        completed_task_ids: Optional[Iterable[str]] = None,
    ) -> str:
        self.log_info(f"Task {task.task_id}: {task.title} [{task.domain}/{self.task_layer(task)}]")
        task_run_id = self.make_task_run_id(spec, task)
        task_dir = story_dir / "tasks" / self.task_dir_name(task)
        task_dir.mkdir(parents=True, exist_ok=True)
        write_json(task_dir / "task.json", task.__dict__)
        if self.push_tasks_to_source_spec_branch() and self.task_completed_in_source_branch(spec, task):
            self.write_agent_log(story_dir, "orchestrator", "task_already_completed", "skipped", f"{task.task_id} already has a completion marker on {spec.branch}")
            self.log_success(f"Task already completed; skipping {task.task_id}")
            return "completed"
        try:
            self.ensure_task_dependencies_satisfied(spec, task, story_dir, task_dir, completed_task_ids=completed_task_ids)
            self.ensure_layer_dependencies_satisfied(spec, task, story_dir, task_dir)
        except TaskDependencyBlocked as exc:
            self.write_agent_log(story_dir, "layer-sequencing-orchestrator", "task_blocked_dependency", "blocked", str(exc))
            self.log_error(f"Task dependency blocked {task.task_id}; earlier split tasks must complete first. Reason: {exc}")
            return "blocked"
        except LayerDependencyBlocked as exc:
            self.write_agent_log(story_dir, "layer-sequencing-orchestrator", "task_blocked_layer_dependency", "blocked", str(exc))
            self.log_error(f"Layer dependency blocked task {task.task_id}; watcher will retry after previous layer PR is merged/passed. Reason: {exc}")
            return "blocked"
        worktree: Optional[Path] = None
        try:
            worktree = self.prepare_worktree(spec, task, task_run_id)
            if self.run_tasks_in_current_worktree() and not self.dry_run:
                self.task_preexisting_changed_paths[(spec.id, task.task_id)] = set(git_changed_paths(worktree))
            self.write_agent_log(story_dir, "orchestrator", "task_started", "started", f"{task.task_id} in {worktree}")
            if self.run_branch_conflict_check(worktree, spec, task, story_dir, task_dir, phase="preflight"):
                self.write_agent_log(story_dir, "branch-conflict-coordinator", "preflight_passed", "completed", task.task_id)
            self.run_agent_sequence(spec, task, worktree, story_dir, task_dir, mode)
            self.collect_evidence(spec, task, story_dir, task_dir, worktree)
            if not self.dry_run:
                self.validate_evidence_ready(worktree, spec, task)
            self.run_branch_conflict_check(worktree, spec, task, story_dir, task_dir, phase="postflight")
            self.run_layer_gate(worktree, spec, task, story_dir, task_dir)
            self.run_guardrails(worktree, spec, task, story_dir, task_dir, mode)
            if not self.dry_run:
                self.write_task_completion_marker(worktree, spec, task, mode)
                self.mark_task_spec_completed(worktree, spec, task, mode)
            self.create_pr_if_changed(worktree, spec, task, story_dir, task_dir, mode)
            self.write_agent_log(story_dir, "orchestrator", "task_completed", "completed", task.task_id)
            self.log_success(f"Task completed {task.task_id}")
            return "completed"
        except BranchConflictBlocked as exc:
            self.write_agent_log(story_dir, "branch-conflict-coordinator", "task_blocked_file_overlap", "blocked", str(exc))
            write_text(task_dir / "branch-conflict-blocked.md", str(exc) + "\n")
            self.log_error(f"Branch conflict blocked task {task.task_id}; continuing with another task when available. Reason: {exc}")
            return "blocked"
        except OrchestratorError as exc:
            message = str(exc)
            self.write_agent_log(story_dir, "orchestrator", "task_blocked_failure", "blocked", message[:800])
            report = self.build_task_failure_report(spec, task, task_dir, worktree, message)
            write_text(task_dir / "task-blocked.md", report)
            self.log_error(f"Task blocked by failure in {task.task_id}; continuing with another task when available. See {task_dir / 'task-blocked.md'}")
            return "blocked"
        finally:
            # Keep worktree by default for debugging. Cleanup is manual to preserve context.
            pass

    def build_task_failure_report(
        self,
        spec: SpecCandidate,
        task: AgentTask,
        task_dir: Path,
        worktree: Optional[Path],
        message: str,
    ) -> str:
        lines = [
            "# Task Blocked",
            "",
            "Status: ERROR",
            f"Time: {now_utc()}",
            f"Spec: {spec.id}",
            f"Source branch: {spec.branch}",
            f"Spec path: {spec.path}",
            f"Task: {task.task_id}",
            f"Title: {task.title}",
            f"Layer: {self.task_layer(task)}",
            f"Domain: {task.domain}",
            f"Task artifacts: {task_dir}",
            f"Worktree: {worktree if worktree else 'not prepared'}",
            "",
            "## Failure Reason",
            "",
            message.strip() or "No failure message was provided.",
            "",
            "## Expected Paths",
            "",
        ]
        if task.expected_paths:
            lines.extend(f"- {path}" for path in task.expected_paths)
        else:
            lines.append("- No expected paths declared by the task plan.")
        lines.extend(["", "## Changed Paths Since Task Start", ""])
        changed: List[str] = []
        if worktree is not None and worktree.exists():
            try:
                preexisting = self.task_preexisting_changed_paths.get((spec.id, task.task_id), set())
                changed = sorted(set(git_changed_paths(worktree)) - preexisting)
            except Exception as exc:
                lines.append(f"- Could not inspect changed paths: {exc}")
        if changed:
            lines.extend(f"- {path}" for path in changed)
        elif worktree is not None:
            lines.append("- No new changed paths detected after subtracting preexisting worktree changes.")
        codex_dir = task_dir / "codex"
        lines.extend(["", "## Codex Logs", ""])
        if codex_dir.exists():
            logs = sorted(codex_dir.glob("*"), key=lambda path: path.stat().st_mtime if path.exists() else 0, reverse=True)
            for path in logs[:20]:
                lines.append(f"- {path}")
        else:
            lines.append("- No Codex log directory exists for this task.")
        lines.extend(["", "## Next Action", "", "Inspect the Codex logs above, fix the failing stage, then rerun the same `run-spec` command."])
        return "\n".join(lines).rstrip() + "\n"

    def prepare_worktree(self, spec: SpecCandidate, task: AgentTask, run_id: str) -> Path:
        base_ref = self.ref_for_branch(spec.branch)
        base_commit = git_output_or_empty(self.repo, "rev-parse", base_ref) or base_ref
        branch_prefix = self.config.get("branching", {}).get("implementation_branch_prefix", "ai")
        branch = f"{branch_prefix}/{safe_slug(spec.title, 32)}/{safe_slug(task.task_id, 48)}"
        worktree = self.worktree_dir / safe_slug(run_id, 90)
        if self.run_tasks_in_current_worktree():
            if self.dry_run:
                self.log(f"    DRY-RUN would use current worktree {self.repo} for task {task.task_id}")
                return self.repo
            current_branch = git_output_or_empty(self.repo, "rev-parse", "--abbrev-ref", "HEAD")
            if self.push_tasks_to_source_spec_branch() and current_branch != spec.branch:
                raise OrchestratorError(
                    "Current-worktree source-spec mode requires the checkout branch to match "
                    f"the spec branch. Current branch is {current_branch!r}; spec branch is {spec.branch!r}."
                )
            self.normalize_runtime_shell_scripts(self.repo)
            self.ensure_runtime_excludes(self.repo)
            self.log(f"    Using current worktree {self.repo}")
            return self.repo
        if self.push_tasks_to_source_spec_branch():
            if self.dry_run:
                self.log(f"    DRY-RUN would create detached worktree from {base_ref} and push task commit back to source branch {spec.branch}")
                return self.repo
            if worktree.exists():
                git(self.repo, "worktree", "remove", "--force", str(worktree), check=False)
                if worktree.exists():
                    shutil.rmtree(worktree)
            worktree.parent.mkdir(parents=True, exist_ok=True)
            git(self.repo, "worktree", "add", "--detach", "--force", str(worktree), base_commit)
            self.normalize_runtime_shell_scripts(worktree)
            self.ensure_runtime_excludes(worktree)
            return worktree
        if self.dry_run:
            self.log(f"    DRY-RUN would create branch {branch} from {base_ref}")
            return self.repo
        if worktree.exists():
            git(self.repo, "worktree", "remove", "--force", str(worktree), check=False)
            if worktree.exists():
                shutil.rmtree(worktree)
        worktree.parent.mkdir(parents=True, exist_ok=True)
        # Add the worktree at a commit SHA instead of checking out the source
        # branch directly. This avoids Git failures when the source spec branch
        # is already checked out in the developer's main working tree.
        git(self.repo, "worktree", "add", "--detach", "--force", str(worktree), base_commit)
        # Use a unique branch when a local or remote agent branch already exists.
        remote = self.remote_name()
        existing_local = git_output_or_empty(self.repo, "branch", "--list", branch)
        existing_remote = git_output_or_empty(self.repo, "ls-remote", "--heads", remote, branch) if self.remote_available() else ""
        if existing_local or existing_remote:
            branch = f"{branch}-{short_sha(run_id, 6)}"
        git(worktree, "switch", "-c", branch)
        self.normalize_runtime_shell_scripts(worktree)
        self.ensure_runtime_excludes(worktree)
        return worktree

    def readonly_agents_in_isolated_worktree(self) -> bool:
        return bool(self.config.get("execution", {}).get("readonly_agents_in_isolated_worktree", True))

    def analysis_stage_failures_block_task(self) -> bool:
        return bool(self.config.get("execution", {}).get("analysis_stage_failures_block_task", False))

    def prepare_readonly_agent_worktree(self, spec: SpecCandidate, task: AgentTask, agent_name: str, task_dir: Path) -> Path:
        """Create an isolated detached worktree for advisory/read-only agents.

        Read-only agents get full local command access for inspection, but their
        prompt-level no-write policy is not a filesystem boundary. Running them
        in a throwaway detached worktree prevents accidental analysis-stage edits
        from polluting the task commit or blocking later implementation stages.
        """
        base_ref = self.ref_for_branch(spec.branch)
        base_commit = git_output_or_empty(self.repo, "rev-parse", base_ref) or base_ref
        slug = compact_slug(
            f"ro-{task.task_id}-{agent_name}-{short_sha(str(task_dir), 8)}",
            prefix="ro",
            slug_len=int(self.config.get("repository", {}).get("max_internal_slug_len", 24)),
            hash_len=8,
        )
        worktree = self.worktree_dir / slug
        if worktree.exists():
            git(self.repo, "worktree", "remove", "--force", str(worktree), check=False)
            if worktree.exists():
                shutil.rmtree(worktree)
        worktree.parent.mkdir(parents=True, exist_ok=True)
        git(self.repo, "worktree", "add", "--detach", "--force", str(worktree), base_commit)
        self.normalize_runtime_shell_scripts(worktree)
        self.ensure_runtime_excludes(worktree)
        return worktree

    def cleanup_readonly_agent_worktree(self, worktree: Path) -> None:
        try:
            if worktree.exists():
                git(self.repo, "worktree", "remove", "--force", str(worktree), check=False)
            if worktree.exists():
                shutil.rmtree(worktree)
        except Exception as exc:
            self.debug(f"Could not remove read-only agent worktree {worktree}: {exc}")

    def normalize_runtime_shell_scripts(self, worktree: Path) -> None:
        normalized = normalize_shell_script_line_endings(worktree)
        if normalized:
            git(worktree, "update-index", "--refresh", "--", *normalized, check=False)
            shown = ", ".join(normalized[:5])
            if len(normalized) > 5:
                shown += f", +{len(normalized) - 5} more"
            self.log(f"    Normalized LF line endings for shell scripts: {shown}")

    def ensure_runtime_excludes(self, worktree: Path) -> None:
        """Keep agent runtime artifacts out of Git even when the repo has no .gitignore."""
        try:
            exclude_rel = git(worktree, "rev-parse", "--git-path", "info/exclude")
            exclude = worktree / exclude_rel
            existing = exclude.read_text(encoding="utf-8") if exclude.exists() else ""
            additions = [
                ".agent/", ".venv/", "venv/", "node_modules/", "vendor/bundle/",
                "__pycache__/", ".pytest_cache/", ".mypy_cache/", "target/", "dist/", "build/"
            ]
            missing = [item for item in additions if item not in existing]
            if missing:
                exclude.parent.mkdir(parents=True, exist_ok=True)
                with exclude.open("a", encoding="utf-8") as fh:
                    fh.write("\n# Agentic runtime artifacts - do not commit\n")
                    for item in missing:
                        fh.write(item + "\n")
        except Exception:
            return

    def changed_files_against_base(self, worktree: Path, base_branch: str) -> List[str]:
        remote = self.config["repository"].get("remote", "origin")
        base_ref = base_branch
        if git_output_or_empty(worktree, "remote", "get-url", remote):
            git(worktree, "fetch", remote, f"{base_branch}:refs/remotes/{remote}/{base_branch}", "--depth", "1", check=False)
            if git_output_or_empty(worktree, "rev-parse", "--verify", "--quiet", f"{remote}/{base_branch}"):
                base_ref = f"{remote}/{base_branch}"
        if not git_output_or_empty(worktree, "rev-parse", "--verify", "--quiet", base_ref):
            roots = git_output_or_empty(worktree, "rev-list", "--max-parents=0", "HEAD").splitlines()
            base_ref = roots[0] if roots else "HEAD"
        output = git_output_or_empty(worktree, "diff", "--name-only", f"{base_ref}...HEAD")
        return [line.strip() for line in output.splitlines() if line.strip()]

    def non_evidence_changes(self, worktree: Path, spec: SpecCandidate) -> List[str]:
        evidence_dir = self.config["repository"].get("evidence_dir", "docs/agentic-evidence")
        return [
            f for f in self.changed_files_against_base(worktree, spec.branch)
            if not is_runtime_or_generated_path(f) and not is_evidence_path(f, evidence_dir=evidence_dir)
        ]

    def run_agent_sequence(self, spec: SpecCandidate, task: AgentTask, worktree: Path, story_dir: Path, task_dir: Path, mode: str) -> None:
        domain_agent = self.resolve_domain_agent(task.domain)
        layer = self.task_layer(task)
        sequence = [
            ("product-requirements-agent.agent.md", "requirements clarification and acceptance criteria mapping", False),
            ("architecture-design-lead.agent.md", "verify design blueprint, architecture, data/API/cloud contracts, and test strategy", False),
            ("paradigm-selection-agent.agent.md", "choose data-driven, object-oriented, or event-driven implementation style for this task", False),
            ("agentic-sdlc-orchestrator.agent.md", "route task and define implementation plan", False),
            (domain_agent, "implement the task with one responsibility", True),
            ("test-strategy-architect.agent.md", "confirm the layer-specific test strategy before QA", True),
            ("test-engineer.agent.md", "create and run unit/component tests first", True),
            ("integration-e2e-engineer.agent.md", "create integration and E2E validation when applicable", True),
            ("dependency-gate-qa.agent.md", f"verify {layer} layer gate and DB → API → frontend ordering", True),
            ("qa-evidence-collector.agent.md", "run QA checklist and collect evidence", True),
            ("product-manager-acceptance.agent.md", "run PM acceptance checklist", True),
            ("dev-manager-pr-governor.agent.md", "enforce one-responsibility PR and engineering standards", True),
            ("pr-documentation-agent.agent.md", "write concise PR notification and review summary", True),
        ]
        if task.requires_terraform or task.domain == "cloud":
            sequence.insert(3, ("terraform-platform-engineer.agent.md", "ensure all AWS/cloud changes are Terraform-backed", True))
        if task.domain in {"frontend", "design"} or task.requires_screenshots:
            sequence.insert(5, ("visual-qa-engineer.agent.md", "capture screenshots and annotate visual issues", True))
            sequence.insert(6, ("accessibility-qa-engineer.agent.md", "check accessibility and usability", True))
        if mode == "cloud":
            sequence.insert(2, ("cloud-night-worker.agent.md", "avoid local-only assumptions and continue cloud-safe work", False))

        total = len(sequence)
        self.log_info(f"Agent sequence: {total} agent step(s) for task {task.task_id}")
        for index, (agent_file, objective, allow_write) in enumerate(sequence, start=1):
            agent_name = agent_file.replace(".agent.md", "")
            prompt = self.render_task_prompt(agent_file, objective, spec, task, story_dir, task_dir, mode, allow_write=allow_write)
            prompt_path = task_dir / "prompts" / f"{safe_slug(agent_name)}.md"
            write_text(prompt_path, prompt)
            self.log_info(f"[{index}/{total}] START {agent_name}: {objective}")
            self.log_info(f"prompt: {prompt_path}")
            self.write_agent_log(story_dir, agent_name, objective, "started", f"Task {task.task_id}; step {index}/{total}; prompt={prompt_path}")
            started = time.monotonic()
            stage_status = "completed"
            stage_worktree = worktree
            readonly_worktree: Optional[Path] = None
            if (
                not allow_write
                and not self.dry_run
                and self.readonly_agents_in_isolated_worktree()
            ):
                readonly_worktree = self.prepare_readonly_agent_worktree(spec, task, agent_name, task_dir)
                stage_worktree = readonly_worktree
                self.log_info(f"read-only stage cwd: {stage_worktree}")
            try:
                self.call_codex(prompt, cwd=stage_worktree, run_dir=task_dir, agent=agent_name, mode=mode, allow_write=allow_write)
            except OrchestratorError as exc:
                if allow_write or self.analysis_stage_failures_block_task():
                    raise
                warning = (
                    f"Analysis stage `{agent_name}` did not complete cleanly but is advisory; "
                    f"continuing to implementation. Error: {str(exc).strip()}"
                )
                self.log_warning(f"Codex advisory warning: {agent_name}: {warning}")
                self.write_agent_log(story_dir, agent_name, objective, "warning", warning[:800])
                with (task_dir / "analysis-stage-warnings.md").open("a", encoding="utf-8") as fh:
                    fh.write(f"- `{now_utc()}` {warning}\n")
                stage_status = "warning"
            finally:
                if readonly_worktree is not None:
                    self.cleanup_readonly_agent_worktree(readonly_worktree)
            elapsed = time.monotonic() - started
            self.write_agent_log(story_dir, agent_name, objective, stage_status, f"Task {task.task_id}; step {index}/{total}; elapsed={elapsed:.1f}s")
            if stage_status == "completed":
                self.log_success(f"[{index}/{total}] DONE {agent_name} elapsed={elapsed:.1f}s")
            else:
                self.log_warning(f"[{index}/{total}] WARN {agent_name} elapsed={elapsed:.1f}s")

    def resolve_domain_agent(self, domain: str) -> str:
        domain = domain.lower()
        mapping = {
            "frontend": "frontend-engineer.agent.md",
            "ui": "frontend-engineer.agent.md",
            "backend": "backend-engineer.agent.md",
            "api": "backend-engineer.agent.md",
            "database": "database-engineer.agent.md",
            "db": "database-engineer.agent.md",
            "cloud": "terraform-platform-engineer.agent.md",
            "infra": "terraform-platform-engineer.agent.md",
            "security": "security-engineer.agent.md",
            "design": "ui-designer.agent.md",
            "qa": "qa-evidence-collector.agent.md",
            "pm": "product-manager-acceptance.agent.md",
            "release": "release-train-engineer.agent.md",
            "fullstack": "mid-software-engineer.agent.md",
        }
        return mapping.get(domain, "mid-software-engineer.agent.md")

    def stage_write_policy(self, allow_write: bool) -> str:
        if allow_write:
            return textwrap.dedent(
                """
                This is an implementation/evidence stage.
                - You may edit files only within the task expected paths, task evidence paths, and narrowly required tests.
                - Do not edit unrelated files, broad-format the repo, or rewrite prior user changes.
                - Do not run `git add`, `git commit`, `git push`, `git rebase`, or PR creation commands; the orchestrator handles staging, commits, pushes, and PRs after gates pass.
                """
            ).strip()
        return textwrap.dedent(
            """
            This is an analysis-only stage.
            - You have full local command access for inspection, but you must not create, edit, delete, move, format, or stage files.
            - Do not use `apply_patch` or shell redirection to write files.
            - Do not run mutating git commands, package installs, formatters, generators, bootstrap scripts, or tests that write fixtures/caches unless this prompt explicitly says to do so.
            - Finish with concise findings, acceptance-criteria mapping, blockers/gaps, and the next implementation action. Do not implement the task in this stage.
            """
        ).strip()

    def render_task_prompt(self, agent_file: str, objective: str, spec: SpecCandidate, task: AgentTask, story_dir: Path, task_dir: Path, mode: str, allow_write: bool = True) -> str:
        stage_policy = self.stage_write_policy(allow_write)
        return self.render_prompt(
            agent_file=agent_file,
            title=objective,
            body=f"""
            You are part of an automated agile AI engineering team.

            Runtime mode: {mode}
            Source spec branch: {spec.branch}
            Spec path: {spec.path}
            Spec id: {spec.id}
            Task id: {task.task_id}
            Task title: {task.title}
            Domain: {task.domain}
            Layer: {self.task_layer(task)}
            Stage write policy:
            {stage_policy}

            Declared dependencies: {json.dumps(task.depends_on, indent=2)}
            Responsibility: {task.responsibility}
            Risk: {task.risk}

            Acceptance criteria:
            {json.dumps(task.acceptance_criteria, indent=2)}

            Expected paths / path intent:
            {json.dumps(task.expected_paths or [], indent=2)}

            Required behavior:
            - Read AGENTS.md and the specialized agent file carefully.
            - Runtime portability is part of the task. Detect the current OS before running shell commands.
            - On Windows, do not assume WSL/Bash exists. Prefer PowerShell-compatible commands, Python scripts, and `python -m ...` invocations. If Bash/WSL is unavailable, record that as an environment gap and continue with Windows-native validation.
            - If `rg` is unavailable, use `git grep`, `findstr`, PowerShell `Get-ChildItem`/`Select-String`, or a short Python read-only search instead of failing the task.
            - If `pytest` is unavailable, use `python -m unittest` for Python tests unless this repo explicitly requires pytest.
            - If an import dependency such as `requests` is missing, run the repo bootstrap or install the repo requirements into the task-scoped environment before classifying the code as broken.
            - Docker daemon, credentials, WSL, or local package-manager failures are environment blockers unless the acceptance criteria require changing repo code to fix them.
            - This repo may run in source-spec-branch mode. When enabled, the validated task is committed to the same branch that contains the spec, and a final PR is created from that branch to the base branch.
            - Continue progress when clarification is needed by doing safe discovery, tests, fixtures, and documentation.
            - Do not guess on high-risk decisions: auth, security, billing, payments, migrations, production config, destructive data operations, public API contracts, cross-repo contracts.
            - Keep this branch to exactly one responsibility.
            - Follow the design-first blueprint. Do not implement before understanding architecture, data model, API contract, cloud components, user flows, and test strategy.
            - Respect strict layer sequencing: database/data model first, API/backend second, frontend third. Unit tests are insufficient for completion; the layer integration gate must pass.
            - If this task is API/backend work and the spec requires a database, do not claim completion without database integration evidence.
            - If this task is frontend work and the spec requires an API, do not claim completion without real API integration or E2E evidence. Mocks are allowed only for early component tests.
            - Select the appropriate programming paradigm deliberately: data-driven for transformations/analytics/rules, object-oriented for domain entities and behavior boundaries, event-driven for asynchronous workflows/integration/retries.
            - Prefer clean architecture boundaries: domain/application/infrastructure/presentation or equivalent repo-native structure.
            - Before editing a file, respect the branch conflict guard and path lease. If another active non-main branch changed or reserved the same file, stop this task and move to another task.
            - Follow SOLID, single responsibility, clean architecture, and avoid god files. If a conflict appears, prefer extracting a new component/service/adapter over touching a shared file.
            - Create or update tests before claiming completion.
            - For UI changes, create screenshot evidence and visual QA notes.
            - For database changes, include schema/model validation, test data strategy, migration/rollback evidence, and DB integration tests.
            - For API/backend changes, include unit, contract, and DB-backed integration validation.
            - For frontend changes, include unit/component tests, visual/accessibility evidence, and real API/E2E validation when the flow depends on the API.
            - For user flows, include E2E validation or a clear reason it cannot run in this environment; missing dependency is a blocker, not a pass.
            - For AWS/cloud resources, use Terraform only.
            - Write concise evidence files under `.agent/stories/{spec.id}/{task.task_id}/` and reviewable evidence under `docs/agentic-evidence/{spec.id}/{task.task_id}/`.
            - Update agents.log using `.ai/scripts/agent_log.py` if available, or append markdown to evidence.
            - If you find bugs, fix in-scope bugs with regression tests; record out-of-scope bugs as follow-up tasks.

            Paths to use:
            - Runtime evidence: .agent/stories/{spec.id}/{task.task_id}/
            - Reviewable evidence: docs/agentic-evidence/{spec.id}/{task.task_id}/
            - QA checklist: docs/agentic-evidence/{spec.id}/{task.task_id}/qa-checklist.md
            - PM checklist: docs/agentic-evidence/{spec.id}/{task.task_id}/pm-checklist.md
            - Test strategy matrix: docs/agentic-evidence/{spec.id}/{task.task_id}/layered-test-matrix.md
            - Layer gate evidence: docs/agentic-evidence/{spec.id}/layer-gates/{self.task_layer(task)}.passed.md
            - PR notification: docs/agentic-evidence/{spec.id}/{task.task_id}/pr-notification.md
            - Agent log: docs/agentic-evidence/{spec.id}/{task.task_id}/agents.log.md

            SPEC:
            {spec.content}
            """,
        )

    def render_prompt(self, agent_file: str, title: str, body: str) -> str:
        agent_path = self.repo / ".ai" / "agents" / agent_file
        agent_text = agent_path.read_text(encoding="utf-8") if agent_path.exists() else f"# {agent_file}\nNo agent file found. Follow AGENTS.md and general senior engineering standards."
        global_instructions = (self.repo / "AGENTS.md").read_text(encoding="utf-8") if (self.repo / "AGENTS.md").exists() else ""
        return textwrap.dedent(f"""
        # Agentic SDLC Task: {title}

        ## Repository AGENTS.md
        {global_instructions}

        ## Specialized agent instructions: {agent_file}
        {agent_text}

        ## Task
        {body}
        """).strip() + "\n"


    def codex_model_args(self) -> List[str]:
        """Return Codex CLI model/reasoning arguments for local agent runs.

        The manager policy is local-first with GPT-5.5 and extra-high reasoning
        via Codex config override `model_reasoning_effort=xhigh`.
        """
        args: List[str] = []
        codex_cfg = self.config.get("codex", {})
        model = os.environ.get("AGENTIC_CODEX_MODEL") or codex_cfg.get("model")
        reasoning = os.environ.get("AGENTIC_CODEX_REASONING_EFFORT") or codex_cfg.get("model_reasoning_effort") or codex_cfg.get("reasoning_effort")
        if model:
            args.extend(["--model", str(model)])
        if reasoning:
            args.extend(["-c", f"model_reasoning_effort={reasoning}"])
        return args

    def cloud_mode_allowed(self, explicit: bool = False) -> bool:
        if explicit:
            return True
        codex_cfg = self.config.get("codex", {})
        if not codex_cfg.get("cloud_execution_requires_explicit_opt_in", True):
            return True
        env_var = codex_cfg.get("cloud_opt_in_env_var", "AGENTIC_EXPLICIT_CLOUD")
        expected = str(codex_cfg.get("cloud_opt_in_value", "true")).lower()
        return os.environ.get(env_var, "").strip().lower() == expected

    def codex_sandbox(self, allow_write: bool) -> str:
        """Return the sandbox used for nested Codex agents.

        Agentic SDLC agents are already launched inside task-scoped Git
        worktrees. On Windows, forcing early read-only stages into the Codex
        read-only sandbox blocks ordinary inspection commands such as
        PowerShell `Get-ChildItem`. Use the configured sandbox for every stage
        so requirements/design agents have the same local access as
        implementation agents.
        """
        env_sandbox = os.environ.get("AGENTIC_CODEX_SANDBOX", "").strip()
        if env_sandbox:
            return env_sandbox
        if bool(self.config["codex"].get("full_access_agents", True)):
            return "danger-full-access"
        return str(self.config["codex"].get("sandbox", "danger-full-access"))

    def codex_approval_policy(self) -> str:
        env_policy = os.environ.get("AGENTIC_CODEX_APPROVAL_POLICY", "").strip()
        if env_policy:
            return env_policy
        return str(self.config["codex"].get("approval_policy", "never"))

    def codex_stage_timeout_seconds(self, allow_write: bool) -> int:
        max_timeout = self.agent_timeout_max_seconds()
        configured = self.configured_stage_timeout_seconds(allow_write)
        env_key = "AGENTIC_CODEX_WRITE_TIMEOUT_SECONDS" if allow_write else "AGENTIC_CODEX_ANALYSIS_TIMEOUT_SECONDS"
        env_value = os.environ.get(env_key, "").strip()
        if env_value:
            try:
                requested = int(env_value)
            except ValueError:
                requested = configured
            if not allow_write:
                requested = max(requested, configured)
            return self.clamp_agent_timeout(requested, max_timeout)
        return self.clamp_agent_timeout(configured, max_timeout)

    def configured_stage_timeout_seconds(self, allow_write: bool) -> int:
        execution = self.config.get("execution", {})
        key = "write_agent_timeout_seconds" if allow_write else "analysis_agent_timeout_seconds"
        default_timeout = DEFAULT_WRITE_AGENT_TIMEOUT_SECONDS if allow_write else DEFAULT_ANALYSIS_AGENT_TIMEOUT_SECONDS
        try:
            return int(execution.get(key, default_timeout))
        except (TypeError, ValueError):
            return default_timeout

    def agent_timeout_max_seconds(self) -> int:
        env_value = os.environ.get("AGENTIC_CODEX_AGENT_TIMEOUT_MAX_SECONDS", "").strip()
        if env_value:
            try:
                return min(max(1, int(env_value)), DEFAULT_AGENT_TIMEOUT_SECONDS)
            except ValueError:
                return DEFAULT_AGENT_TIMEOUT_SECONDS
        execution = self.config.get("execution", {})
        try:
            configured = int(execution.get("agent_timeout_max_seconds", DEFAULT_AGENT_TIMEOUT_SECONDS))
            return min(max(1, configured), DEFAULT_AGENT_TIMEOUT_SECONDS)
        except (TypeError, ValueError):
            return DEFAULT_AGENT_TIMEOUT_SECONDS

    def clamp_agent_timeout(self, requested: int, max_timeout: int) -> int:
        if requested <= 0:
            return max_timeout
        return min(requested, max_timeout)

    def call_codex(self, prompt: str, cwd: Path, run_dir: Path, agent: str, mode: str, allow_write: bool) -> None:
        run_dir.mkdir(parents=True, exist_ok=True)
        configured_codex_bin = self.config["codex"].get("binary", "codex")
        codex_bin = resolve_executable(str(configured_codex_bin), prefer_cmd_on_windows=True)
        prompt_hash = short_sha(prompt, 10)
        codex_dir = run_dir / "codex"
        out_file = codex_dir / f"{agent}-{prompt_hash}.jsonl"
        final_file = codex_dir / f"{agent}-{prompt_hash}.final.md"
        stderr_file = codex_dir / f"{agent}-{prompt_hash}.stderr.log"
        heartbeat_file = codex_dir / f"{agent}-{prompt_hash}.heartbeat.jsonl"
        codex_dir.mkdir(parents=True, exist_ok=True)
        if self.dry_run:
            write_text(final_file, f"DRY-RUN: would run {agent} in {cwd}\n")
            self.log_info(f"DRY-RUN would run Codex agent={agent} cwd={cwd}")
            return
        if codex_bin is None:
            write_text(final_file, f"Codex binary not found. Prompt saved for manual/local execution.\n")
            write_text(run_dir / "prompts_missing_codex" / f"{agent}-{prompt_hash}.md", prompt)
            if self.dry_run or bool(self.config["codex"].get("allow_missing_codex", False)):
                self.log_warning(f"Codex binary missing; prompt saved for {agent}")
                return
            raise OrchestratorError(f"Codex binary not found: {configured_codex_bin}. Install Codex CLI, run with --dry-run, or set codex.allow_missing_codex=true only for prompt-generation workflows.")
        sandbox = self.codex_sandbox(allow_write)
        approval_policy = self.codex_approval_policy()
        model_env = self.config["codex"].get("model_env_var", "AGENTIC_CODEX_MODEL")
        reasoning_env = self.config["codex"].get("reasoning_effort_env_var", "AGENTIC_CODEX_REASONING_EFFORT")
        model = os.environ.get(model_env) or self.config["codex"].get("model", "gpt-5.5")
        reasoning_effort = os.environ.get(reasoning_env) or self.config["codex"].get("model_reasoning_effort") or self.config["codex"].get("reasoning_effort", "xhigh")
        reasoning_summary = self.config["codex"].get("reasoning_summary", "concise")
        verbosity = self.config["codex"].get("verbosity", "high")
        cmd = [codex_bin]
        if approval_policy:
            cmd.extend(["--ask-for-approval", approval_policy])
        cmd.append("exec")
        json_events = bool(self.config["codex"].get("json_events", True))
        if json_events:
            cmd.append("--json")
        if self.config["codex"].get("ignore_user_config", False):
            cmd.append("--ignore-user-config")
        if model:
            cmd.extend(["--model", str(model)])
        if reasoning_effort:
            cmd.extend(["-c", f"model_reasoning_effort={reasoning_effort}"])
        if reasoning_summary:
            cmd.extend(["-c", f"model_reasoning_summary={reasoning_summary}"])
        if verbosity:
            cmd.extend(["-c", f"model_verbosity={verbosity}"])
        cmd.extend(["--sandbox", sandbox, "-o", str(final_file), "-"])

        heartbeat_seconds = int(self.config.get("logging", {}).get("codex_heartbeat_seconds", os.environ.get("AGENTIC_CODEX_HEARTBEAT_SECONDS", "30")))
        timeout_seconds = self.codex_stage_timeout_seconds(allow_write)
        preview_chars = int(self.config.get("logging", {}).get("codex_preview_chars", os.environ.get("AGENTIC_CODEX_PREVIEW_CHARS", "220")))
        self.log_info(f"Codex start: agent={agent} mode={mode} sandbox={sandbox} model={model} reasoning={reasoning_effort}")
        if timeout_seconds:
            self.log_info(f"Codex timeout budget: agent={agent} seconds={timeout_seconds}")
        self.log_info(f"Codex cwd: {cwd}")
        self.log_info(f"Codex live log: {out_file}")
        self.log_info(f"Codex final: {final_file}")

        def summarize_event(raw_line: str) -> str:
            line = raw_line.strip()
            if not line:
                return ""
            if json_events:
                try:
                    event = json.loads(line)
                    etype = str(event.get("type") or event.get("event") or event.get("name") or "event")
                    for key in ("message", "text", "summary", "status", "detail"):
                        value = event.get(key)
                        if isinstance(value, str) and value.strip():
                            compact = re.sub(r"\s+", " ", value.strip())[:preview_chars]
                            return f"{etype}: {compact}"
                    if "data" in event and isinstance(event["data"], dict):
                        for key in ("message", "text", "summary", "status"):
                            value = event["data"].get(key)
                            if isinstance(value, str) and value.strip():
                                compact = re.sub(r"\s+", " ", value.strip())[:preview_chars]
                                return f"{etype}: {compact}"
                    return etype
                except json.JSONDecodeError:
                    pass
            return re.sub(r"\s+", " ", line)[:preview_chars]

        events: "queue.Queue[Tuple[str, str]]" = queue.Queue()
        stdout_tail: List[str] = []
        stderr_tail: List[str] = []

        try:
            proc = subprocess.Popen(
                cmd,
                cwd=str(cwd),
                text=True,
                encoding="utf-8",
                errors="replace",
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=os.environ.copy(),
                bufsize=1,
            )
        except FileNotFoundError as exc:
            raise OrchestratorError(f"Codex executable not found while starting agent {agent}: {codex_bin}") from exc
        except OSError as exc:
            raise OrchestratorError(f"Could not start Codex agent {agent}: {exc}") from exc

        def stream_reader(stream: Any, path: Path, kind: str) -> None:
            try:
                with path.open("a", encoding="utf-8") as fh:
                    for raw in iter(stream.readline, ""):
                        fh.write(raw)
                        fh.flush()
                        if kind == "stdout":
                            summary = summarize_event(raw)
                        else:
                            summary = re.sub(r"\s+", " ", raw.strip())[:preview_chars]
                        if summary:
                            events.put((kind, summary))
            finally:
                try:
                    stream.close()
                except Exception:
                    pass

        assert proc.stdout is not None and proc.stderr is not None and proc.stdin is not None
        stdout_thread = threading.Thread(target=stream_reader, args=(proc.stdout, out_file, "stdout"), daemon=True)
        stderr_thread = threading.Thread(target=stream_reader, args=(proc.stderr, stderr_file, "stderr"), daemon=True)
        stdout_thread.start()
        stderr_thread.start()
        try:
            proc.stdin.write(prompt)
            proc.stdin.close()
        except BrokenPipeError:
            pass

        started = time.monotonic()
        last_heartbeat = started
        last_event = "process-started"
        timed_out = False
        while True:
            try:
                kind, summary = events.get_nowait()
                last_event = summary
                if kind == "stdout":
                    stdout_tail.append(summary)
                    self.log_status(stream_log_level(kind, summary), f"Codex event: {agent}: {summary}")
                else:
                    stderr_tail.append(summary)
                    self.log_status(stream_log_level(kind, summary), f"Codex stderr: {agent}: {summary}")
            except queue.Empty:
                pass
            rc = proc.poll()
            now = time.monotonic()
            if rc is not None:
                break
            if timeout_seconds and now - started >= timeout_seconds:
                timed_out = True
                elapsed = int(now - started)
                self.log_error(f"Codex timeout: agent={agent} elapsed={elapsed}s pid={proc.pid} last={last_event}")
                try:
                    proc.terminate()
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    proc.wait(timeout=5)
                break
            if now - last_heartbeat >= heartbeat_seconds:
                elapsed = int(now - started)
                heartbeat = {
                    "ts": now_utc(),
                    "agent": agent,
                    "elapsed_seconds": elapsed,
                    "last_event": last_event,
                    "pid": proc.pid,
                    "cwd": str(cwd),
                    "log": str(out_file),
                }
                append_jsonl(heartbeat_file, heartbeat)
                self.log_info(f"Codex still running: agent={agent} elapsed={elapsed}s pid={proc.pid} last={last_event}")
                last_heartbeat = now
            time.sleep(0.2)

        stdout_thread.join(timeout=2)
        stderr_thread.join(timeout=2)
        while True:
            try:
                kind, summary = events.get_nowait()
            except queue.Empty:
                break
            last_event = summary
            if kind == "stdout":
                stdout_tail.append(summary)
                self.log_status(stream_log_level(kind, summary), f"Codex event: {agent}: {summary}")
            else:
                stderr_tail.append(summary)
                self.log_status(stream_log_level(kind, summary), f"Codex stderr: {agent}: {summary}")

        elapsed = time.monotonic() - started
        if timed_out:
            tail = "; ".join((stderr_tail + stdout_tail)[-5:])
            raise CodexAgentTimeout(
                f"Codex agent {agent} timed out after {timeout_seconds}s. "
                f"Last event: {last_event}. "
                f"Recent output: {tail or 'none'}. "
                f"See {out_file}" + (f" and {stderr_file}" if stderr_file.exists() else "")
            )
        if proc.returncode != 0:
            tail = "; ".join((stderr_tail + stdout_tail)[-8:])
            self.log_error(f"Codex failed: agent={agent} exit={proc.returncode} elapsed={elapsed:.1f}s log={out_file} recent={tail or 'none'}")
            raise OrchestratorError(
                f"Codex agent {agent} failed with exit code {proc.returncode}. "
                f"Recent output: {tail or 'none'}. "
                f"See {out_file}" + (f" and {stderr_file}" if stderr_file.exists() else "")
            )
        self.log_success(f"Codex done: agent={agent} exit=0 elapsed={elapsed:.1f}s log={out_file}")

    def write_agent_log(self, story_dir: Path, agent: str, action: str, status: str, summary: str) -> None:
        record = {
            "ts": now_utc(),
            "agent": agent,
            "action": action,
            "status": status,
            "summary": summary,
        }
        append_jsonl(story_dir / "agents.log.jsonl", record)
        md = story_dir / "agents.log.md"
        level = status_log_level(status)
        line = f"- `{record['ts']}` [{level}] **{agent}** `{status}` — {action}: {summary}\n"
        with md.open("a", encoding="utf-8") as fh:
            fh.write(line)

    def collect_evidence(self, spec: SpecCandidate, task: AgentTask, story_dir: Path, task_dir: Path, worktree: Path) -> None:
        rel = Path(self.config["repository"].get("evidence_dir", "docs/agentic-evidence")) / spec.id / task.task_id
        # Dry-run must not dirty the repository; write preview evidence under .agent/runs only.
        target = (task_dir / "ev") if self.dry_run else (worktree / rel)
        target.mkdir(parents=True, exist_ok=True)
        # Copy story log.
        if (story_dir / "agents.log.md").exists():
            write_text(target / "agents.log.md", (story_dir / "agents.log.md").read_text(encoding="utf-8"))
        # Ensure minimum evidence files exist. Agents can replace these with richer content.
        defaults = {
            "qa-checklist.md": self.default_qa_checklist(spec, task),
            "pm-checklist.md": self.default_pm_checklist(spec, task),
            "test-evidence.md": self.default_test_evidence(spec, task, worktree),
            "layered-test-matrix.md": self.default_layered_test_matrix(spec, task),
            "scale-security-architecture-review.md": self.default_scale_review(spec, task),
            "pr-notification.md": self.default_pr_notification(spec, task),
        }
        for name, content in defaults.items():
            path = target / name
            if not path.exists() or not path.read_text(encoding="utf-8").strip():
                write_text(path, content)
        if task.requires_screenshots and not (target / "visual-evidence.md").exists():
            write_text(target / "visual-evidence.md", self.default_visual_evidence(spec, task))

    def validate_evidence_ready(self, worktree: Path, spec: SpecCandidate, task: AgentTask) -> None:
        if not bool(self.config.get("pr_policy", {}).get("block_placeholder_evidence", True)):
            return
        rel = Path(self.config["repository"].get("evidence_dir", "docs/agentic-evidence")) / spec.id / task.task_id
        target = worktree / rel
        required = [
            "agents.log.md",
            "qa-checklist.md",
            "pm-checklist.md",
            "test-evidence.md",
            "layered-test-matrix.md",
            "scale-security-architecture-review.md",
            "pr-notification.md",
        ]
        if task.requires_screenshots:
            required.append("visual-evidence.md")
        failures: List[str] = []
        placeholder_markers = [
            "PENDING_AGENT_VERIFICATION",
            "Generated by automation. Agents should replace",
            "PM decision: Pending",
        ]
        for name in required:
            path = target / name
            if not path.exists() or not path.read_text(encoding="utf-8", errors="replace").strip():
                failures.append(f"missing evidence: {rel / name}")
                continue
            content = path.read_text(encoding="utf-8", errors="replace")
            for marker in placeholder_markers:
                if marker in content:
                    failures.append(f"placeholder evidence still present in {rel / name}: {marker}")
        if failures:
            raise OrchestratorError(
                "Evidence gate failed; agents must replace placeholder evidence before a PR can be created:\n"
                + "\n".join(f"- {item}" for item in failures)
            )

    def default_qa_checklist(self, spec: SpecCandidate, task: AgentTask) -> str:
        return f"""# QA Checklist: {task.title}

Status: PENDING_AGENT_VERIFICATION

- [ ] Unit tests added or confirmed not applicable.
- [ ] Component tests added or confirmed not applicable.
- [ ] Database tests pass before API tests when data is involved.
- [ ] API contract/integration tests pass before frontend E2E when API is involved.
- [ ] Integration/API tests added or confirmed not applicable.
- [ ] E2E tests added or blocked with explicit dependency reason.
- [ ] Visual QA completed for UI changes.
- [ ] Accessibility checked for UI changes.
- [ ] Regression risks reviewed.
- [ ] Bugs found during QA are fixed or logged as follow-up.

Spec: `{spec.path}` on `{spec.branch}`
Task: `{task.task_id}`
"""

    def default_pm_checklist(self, spec: SpecCandidate, task: AgentTask) -> str:
        return f"""# PM Acceptance Checklist: {task.title}

Status: PENDING_AGENT_VERIFICATION

- [ ] User intent is satisfied.
- [ ] Flow is intuitive.
- [ ] UI copy is clear, if applicable.
- [ ] Behavior integrates with the rest of the app.
- [ ] Edge cases are handled or documented.
- [ ] Follow-up product questions are listed.
- [ ] Ready for human AI PM review.

Spec: `{spec.path}` on `{spec.branch}`
Task: `{task.task_id}`
"""

    def default_test_evidence(self, spec: SpecCandidate, task: AgentTask, worktree: Path) -> str:
        status = git_output_or_empty(worktree, "status", "--porcelain")
        return f"""# Test Evidence: {task.title}

Generated by automation. Agents should replace this with concrete command output.

## Expected validation

- Unit tests: required when code behavior changes.
- Integration tests: required for API/backend/database/cloud boundaries.
- E2E tests: required for user flows.
- Local/manual tests: required when cloud cannot run local app.

## Current git status snapshot

```text
{status or 'clean or no changes yet'}
```
"""

    def default_layered_test_matrix(self, spec: SpecCandidate, task: AgentTask) -> str:
        return f"""# Layered Test Matrix: {task.title}

Status: PENDING_AGENT_VERIFICATION

Layer: {self.task_layer(task)}

| Acceptance criterion | Database tests | API/contract tests | Frontend/component tests | Integration/E2E | Evidence | Status |
|---|---|---|---|---|---|---|
| See spec criteria | Required if data is involved | Required if API is involved | Required if UI is involved | Required for layer integration | test-evidence.md | Pending |

Required order: database → API → frontend. Unit tests are not enough for completion.
"""

    def default_scale_review(self, spec: SpecCandidate, task: AgentTask) -> str:
        return f"""# Scale / Security / Architecture Review: {task.title}

Status: PENDING_AGENT_VERIFICATION

- [ ] Clean code and clear boundaries.
- [ ] No unnecessary coupling.
- [ ] Handles concurrency/idempotency where relevant.
- [ ] Uses pagination/batching/streaming where relevant.
- [ ] Has timeouts/retries/backoff where relevant.
- [ ] Avoids new single points of failure.
- [ ] Does not expose secrets or sensitive data.
- [ ] AWS/cloud changes are Terraform-backed when applicable.
- [ ] Cost and sustainability impact considered for cloud resources.
"""

    def default_visual_evidence(self, spec: SpecCandidate, task: AgentTask) -> str:
        return f"""# Visual Evidence: {task.title}

Status: PENDING_AGENT_VERIFICATION

Expected screenshots for UI changes:

- [ ] desktop-empty
- [ ] desktop-valid
- [ ] desktop-invalid
- [ ] mobile-empty
- [ ] mobile-valid
- [ ] mobile-invalid
- [ ] loading/error/success states when applicable

If the environment cannot run the local app, record the blocker and create a local-test request.
"""

    def default_pr_notification(self, spec: SpecCandidate, task: AgentTask) -> str:
        manager = self.config.get("manager", {}).get("github_user", "")
        mention = f"@{manager}" if manager else "AI PM"
        return f"""# PR Notification Draft

{mention}, this PR is ready for review after agent QA/PM gates.

## Summary

Implements one responsibility: **{task.responsibility}**

## Why

From spec `{spec.path}` on branch `{spec.branch}`.

## Validation

See evidence files in this folder, including branch conflict guard results when available.

## Review focus

- Task scope: `{task.task_id}`
- Domain: `{task.domain}`
- Risk: `{task.risk}`

## Rollback

Revert this PR. No production deployment should occur without release gate approval.
"""


    def run_branch_conflict_check(self, worktree: Path, spec: SpecCandidate, task: AgentTask, story_dir: Path, task_dir: Path, phase: str) -> bool:
        cfg = self.config.get("branch_conflict", {})
        if not bool(cfg.get("enabled", True)):
            return True
        script = worktree / ".ai/scripts/branch_conflict_guard.py"
        if not script.exists():
            self.debug("branch_conflict_guard.py not found; skipping branch conflict guard")
            return True
        default_base = str(cfg.get("default_base_branch") or self.config["repository"].get("default_base_branch", "main"))
        current_branch = git_output_or_empty(worktree, "rev-parse", "--abbrev-ref", "HEAD")
        report_dir = task_dir / "bc"
        report_dir.mkdir(parents=True, exist_ok=True)
        cmd = [
            sys.executable, str(script), "guard",
            "--mode", phase,
            "--base", default_base,
            "--current-diff-base", spec.branch,
            "--exclude-branch", spec.branch,
        ]
        if current_branch and current_branch != spec.branch:
            cmd.extend(["--exclude-branch", current_branch])
        cmd.extend([
            "--json-output", str(report_dir / f"{phase}.json"),
            "--markdown-output", str(report_dir / f"{phase}.md"),
        ])
        for pattern in cfg.get("ignore_patterns", []):
            cmd.extend(["--ignore-pattern", str(pattern)])
        expected_paths = self.task_branch_conflict_scopes(spec, task) if self.run_tasks_in_current_worktree() else list(task.expected_paths or [])
        if phase == "preflight":
            if expected_paths:
                for path in expected_paths:
                    cmd.extend(["--path", str(path)])
            else:
                cmd.append("--allow-empty-intent")
            if expected_paths and bool(cfg.get("write_path_leases", True)) and not self.dry_run and not self.run_tasks_in_current_worktree():
                cmd.append("--write-lease")
                cmd.extend(["--task-id", task.task_id, "--story-id", spec.id])
                if bool(cfg.get("commit_path_leases", True)):
                    cmd.append("--commit-lease")
                if bool(cfg.get("push_path_leases", False)):
                    cmd.append("--push-lease")
        else:
            if self.run_tasks_in_current_worktree() and expected_paths:
                for path in expected_paths:
                    cmd.extend(["--path", str(path)])
            else:
                cmd.append("--current-diff")
        if self.dry_run:
            self.log(f"    DRY-RUN would run {' '.join(cmd)}")
            return True
        cp = run(cmd, cwd=worktree, check=False, capture=True)
        write_text(report_dir / f"{phase}.out", (cp.stdout or "") + ("\n# STDERR\n" + cp.stderr if cp.stderr else ""))
        if cp.returncode != 0:
            # Copy report to reviewable evidence if possible for postflight failures.
            message = f"Branch conflict guard failed during {phase}. See {report_dir / (phase + '.md')}"
            if bool(cfg.get("block_on_overlap", True)):
                raise BranchConflictBlocked(message)
            raise OrchestratorError(message)
        return True

    def run_guardrails(self, worktree: Path, spec: SpecCandidate, task: AgentTask, story_dir: Path, task_dir: Path, mode: str) -> None:
        scripts = [
            self.repo / ".ai/scripts/pr_guardrails.py",
            self.repo / ".ai/scripts/aws_terraform_guardrails.py",
        ]
        for script in scripts:
            if script.exists():
                cmd = [sys.executable, str(script), "--base", spec.branch, "--task-id", task.task_id]
                if script.name == "pr_guardrails.py" and task.requires_screenshots:
                    cmd.append("--ui-change")
                if script.name == "pr_guardrails.py":
                    cmd.append("--advisory")
                if script.name == "aws_terraform_guardrails.py" and task.requires_terraform:
                    cmd.append("--aws-change")
                if self.dry_run:
                    self.log(f"    DRY-RUN would run {' '.join(cmd)}")
                else:
                    env = {
                        "AGENTIC_SCOPE_PATHS_JSON": json.dumps(self.task_change_scopes(spec, task)),
                        "AGENTIC_CONFLICT_SCOPE_PATHS_JSON": json.dumps(self.task_branch_conflict_scopes(spec, task)),
                    }
                    if script.name == "pr_guardrails.py" and self.push_tasks_to_source_spec_branch():
                        # Source-spec-branch mode commits validated evidence and
                        # task markers back to the integration branch; the final
                        # PR is the review object, so evidence-only task commits
                        # are allowed while normal task-branch PRs still block them.
                        env["AGENT_ALLOW_EVIDENCE_ONLY"] = "true"
                    if script.name == "pr_guardrails.py":
                        env["AGENT_PR_GUARDRAILS_ADVISORY"] = "true"
                    cp = run(cmd, cwd=worktree, check=False, capture=True, env=env)
                    write_text(task_dir / f"{script.stem}.out", (cp.stdout or "") + (cp.stderr or ""))
                    if script.name == "pr_guardrails.py":
                        findings = self.write_pr_guardrails_diagnostic(task_dir, cp.stdout or "", cp.stderr or "", cp.returncode)
                        if findings:
                            self.write_agent_log(
                                story_dir,
                                "pr-guardrails",
                                "diagnostic_findings",
                                "completed",
                                f"{findings} advisory finding(s); continuing task pipeline",
                            )
                            self.log_warning(
                                f"PR guardrails reported {findings} advisory finding(s) for {task.task_id}; continuing. "
                                f"See {task_dir / 'pr_guardrails-diagnostic.md'}"
                            )
                        if cp.returncode != 0:
                            self.log_warning(
                                f"PR guardrails exited {cp.returncode} for {task.task_id}; treated as advisory so later tasks can continue."
                            )
                        continue
                    if cp.returncode != 0:
                        raise OrchestratorError(f"Guardrail failed: {script.name}. See {task_dir / (script.stem + '.out')}")

    def write_pr_guardrails_diagnostic(self, task_dir: Path, stdout: str, stderr: str, returncode: int) -> int:
        """Write a human-readable advisory report for PR guardrail findings."""
        report: Dict[str, Any] = {}
        try:
            report = json.loads(stdout.strip()) if stdout.strip() else {}
        except json.JSONDecodeError:
            report = {}
        failures = [str(item) for item in report.get("failures", []) if str(item).strip()]
        warnings = [str(item) for item in report.get("warnings", []) if str(item).strip()]
        lines = [
            "# PR Guardrails Diagnostic",
            "",
            "Status: ADVISORY",
            f"Time: {now_utc()}",
            f"Exit code: {returncode}",
            "",
            "PR guardrails are diagnostic in the autonomous SDLC task pipeline. Findings are recorded here so the agent can analyze the cause, but they do not block task completion or later DB/API/frontend tasks.",
            "",
            "## Findings",
            "",
        ]
        if failures:
            lines.append("### Hard Findings")
            lines.append("")
            lines.extend(f"- {item}" for item in failures)
            lines.append("")
        if warnings:
            lines.append("### Reviewability Warnings")
            lines.append("")
            lines.extend(f"- {item}" for item in warnings)
            lines.append("")
        if not failures and not warnings:
            lines.append("- No PR guardrail findings were reported.")
            lines.append("")
        if stderr.strip():
            lines.extend(["## STDERR", "", "```text", stderr.strip(), "```", ""])
        if report:
            lines.extend(["## Raw Report", "", "```json", json.dumps(report, indent=2), "```", ""])
        elif stdout.strip():
            lines.extend(["## Raw Output", "", "```text", stdout.strip(), "```", ""])
        write_text(task_dir / "pr_guardrails-diagnostic.md", "\n".join(lines).rstrip() + "\n")
        return len(failures) + len(warnings)

    def task_completion_path(self, spec: SpecCandidate, task: AgentTask) -> Path:
        return Path(self.config["repository"].get("evidence_dir", "docs/agentic-evidence")) / spec.id / task.task_id / "task-completed.md"

    def task_change_scopes(self, spec: SpecCandidate, task: AgentTask) -> List[str]:
        """Paths this task is allowed to stage/check in current-worktree mode."""
        evidence_root = Path(self.config["repository"].get("evidence_dir", "docs/agentic-evidence"))
        layer_gate_dir = Path(
            self.config.get("layer_gates", {})
            .get("pass_file_dir", "docs/agentic-evidence/{spec_id}/layer-gates")
            .format(spec_id=spec.id)
        )
        scopes: List[str] = []
        scopes.extend(str(path) for path in (task.expected_paths or []))
        scopes.extend([
            str(evidence_root / spec.id / task.task_id),
            str(self.task_completion_path(spec, task)),
            str(layer_gate_dir),
            spec.path,
        ])
        normalized = {str(scope).replace("\\", "/").strip("/") for scope in scopes if str(scope).strip()}
        return sorted(normalized)

    def task_branch_conflict_scopes(self, spec: SpecCandidate, task: AgentTask) -> List[str]:
        """Paths that should count as implementation ownership conflicts.

        The source task-list spec is a progress document in source-spec mode.
        Older spec branches may still touch it, so it must be staged when this
        task completes but should not block implementation ownership checks.
        """
        spec_path = spec.path.replace("\\", "/").strip("/")
        return [path for path in self.task_change_scopes(spec, task) if path != spec_path]

    def preexisting_task_changes(self, spec: SpecCandidate, task: AgentTask) -> set[str]:
        """Changed paths that existed before this current-worktree task began."""
        return set(getattr(self, "task_preexisting_changed_paths", {}).get((spec.id, task.task_id), set()))

    def source_task_commit_exclude_paths(
        self,
        spec: SpecCandidate,
        task: AgentTask,
        scopes: Optional[Iterable[str]],
    ) -> Optional[Iterable[str]]:
        """Return paths to exclude from a source-spec task commit.

        In normal current-worktree PR mode, preexisting scoped edits are left
        untouched so unrelated local work is not swept into the task PR. In
        source-spec mode, the source branch is the integration branch: a rerun
        may start with validated task artifacts already present from a previous
        failed attempt. Excluding those scoped artifacts would commit only the
        completion marker and leave later layer gates unable to see the real
        DB/API/frontend evidence on the branch.
        """
        if not scopes:
            return None
        if self.run_tasks_in_current_worktree() and self.push_tasks_to_source_spec_branch():
            return None
        return self.preexisting_task_changes(spec, task)

    def task_completed_in_source_branch(self, spec: SpecCandidate, task: AgentTask) -> bool:
        """Return true when a previous run committed the task completion marker.

        GitHub Actions runners are ephemeral, so .agent/state is not enough to
        know progress across pushes. This marker is committed to the source spec
        branch and lets the workflow continue API/frontend tasks without repeating
        completed DB/API work every time an agent pushes to the branch.
        """
        ref = self.ref_for_branch(spec.branch)
        rel = str(self.task_completion_path(spec, task)).replace("\\", "/")
        out = git_output_or_empty(self.repo, "show", f"{ref}:{rel}")
        if not out.strip():
            return False
        layer_gate_script = self.repo / ".ai/scripts/layer_gate.py"
        if bool(self.config.get("layer_gates", {}).get("enabled", True)) and layer_gate_script.exists():
            return self.source_branch_has_layer_pass(spec, self.task_layer(task))
        return True

    def update_front_matter_status(self, text: str, status: str, completed_at: Optional[str] = None) -> str:
        """Update simple YAML front matter status fields without external deps."""
        timestamp = completed_at or now_utc()
        if text.startswith("---\n"):
            end = text.find("\n---\n", 4)
            if end != -1:
                raw = text[4:end]
                body = text[end + 5:]
                lines = raw.splitlines()
                seen_status = False
                seen_updated = False
                seen_completed = False
                out: List[str] = []
                for line in lines:
                    if re.match(r"^\s*status\s*:", line):
                        out.append(f"status: {status}")
                        seen_status = True
                    elif re.match(r"^\s*updated_at\s*:", line):
                        out.append(f"updated_at: \"{timestamp[:10]}\"")
                        seen_updated = True
                    elif re.match(r"^\s*completed_at\s*:", line):
                        if status == "completed":
                            out.append(f"completed_at: \"{timestamp}\"")
                        seen_completed = True
                    else:
                        out.append(line)
                if not seen_status:
                    out.append(f"status: {status}")
                if not seen_updated:
                    out.append(f"updated_at: \"{timestamp[:10]}\"")
                if status == "completed" and not seen_completed:
                    out.append(f"completed_at: \"{timestamp}\"")
                return "---\n" + "\n".join(out).rstrip() + "\n---\n" + body
        # No front matter: add one so future scans can classify it.
        header = f"---\nstatus: {status}\nupdated_at: \"{timestamp[:10]}\"\n"
        if status == "completed":
            header += f"completed_at: \"{timestamp}\"\n"
        header += "---\n\n"
        return header + text

    def mark_task_progress_checkbox_done(self, text: str, task: AgentTask) -> str:
        """Mark only the executed split-task checkbox complete.

        The task-list document can contain many implementation checkboxes. A
        single split-task commit must never mark the whole spec done.
        """
        task_id = safe_slug(task.task_id, 48)
        lines = text.splitlines()
        found = False
        for index, line in enumerate(lines):
            stripped = line.strip()
            if not re.match(r"^[-*]\s+\[\s\]\s+", stripped):
                continue
            code_ids = [safe_slug(value, 48) for value in re.findall(r"`([^`]+)`", stripped)]
            checkbox_text = re.sub(r"^[-*]\s+\[\s\]\s+", "", stripped)
            if task_id in code_ids or task_id in safe_slug(checkbox_text, 160):
                lines[index] = re.sub(r"\[\s\]", "[x]", line, count=1)
                found = True
        updated = "\n".join(lines)
        if text.endswith("\n"):
            updated += "\n"
        if found:
            return updated
        progress_line = f"- [x] `{task.task_id}` - {task.title}"
        heading = "## Agentic Split Task Progress"
        if heading in updated:
            return updated.rstrip() + f"\n{progress_line}\n"
        if self.worker_wrapper_task_blueprint(task_id):
            checked_ids = self.completed_split_task_ids_from_text(updated)
            checked_ids.add(task_id)
            canonical = [
                ("worker-wrapper-design-gate", "Clarify worker wrapper design"),
                ("artifact-manifest-contract", "Add artifact manifest contract"),
                ("worker-wrapper-cli", "Add wrapper CLI"),
                ("cdp-security-runtime-guard", "Guard CDP exposure"),
                ("local-fixture-worker-mode", "Add local fixture worker mode"),
                ("container-entrypoint-alignment", "Align container entrypoint"),
                ("worker-wrapper-qa-evidence", "Validate wrapper evidence"),
                ("worker-wrapper-pm-pr-notice", "Prepare PM PR notice"),
            ]
            lines = [heading, ""]
            for split_id, title in canonical:
                mark = "x" if split_id in checked_ids else " "
                lines.append(f"- [{mark}] `{split_id}` - {title}")
            return updated.rstrip() + "\n\n" + "\n".join(lines) + "\n"
        return updated.rstrip() + f"\n\n{heading}\n\n{progress_line}\n"

    def mark_task_spec_completed(self, worktree: Path, spec: SpecCandidate, task: AgentTask, mode: str) -> None:
        """Mark the executed task spec as completed so agents skip it later.

        This updates the task document itself in the implementation worktree. For
        task-branch mode, the completed task file is included in the PR. For
        source-spec-branch mode, it is committed with the task result.
        """
        spec_rel = Path(spec.path)
        spec_path = worktree / spec_rel
        if not spec_path.exists():
            # In unusual detached/worktree layouts, fall back to the repo copy.
            spec_path = self.repo / spec_rel
        if not spec_path.exists():
            self.log(f"    Could not find task spec file to mark completed: {spec.path}")
            return
        original = spec_path.read_text(encoding="utf-8", errors="replace")
        timestamp = now_utc()
        next_status = spec.status if normalize_spec_status(spec.status or "") not in {"completed", "done"} else "ready_for_agents"
        updated = self.update_front_matter_status(original, next_status or "ready_for_agents")
        updated = self.mark_task_progress_checkbox_done(updated, task)
        note = textwrap.dedent(f"""

        ---

        Task completed by agentic SDLC.

        - Completed task id: `{task.task_id}`
        - Completed task title: {task.title}
        - Runtime mode: `{mode}`
        - Completed at: `{timestamp}`
        - Evidence: `docs/agentic-evidence/{spec.id}/{task.task_id}/`
        """)
        if "Task completed by agentic SDLC." not in updated:
            updated = updated.rstrip() + note + "\n"
        spec_path.write_text(updated, encoding="utf-8")

    def write_task_completion_marker(self, worktree: Path, spec: SpecCandidate, task: AgentTask, mode: str) -> None:
        rel = self.task_completion_path(spec, task)
        body = f"""# Task completed

- Spec id: `{spec.id}`
- Spec branch: `{spec.branch}`
- Spec file: `{spec.path}`
- Task id: `{task.task_id}`
- Task title: {task.title}
- Domain: `{task.domain}`
- Layer: `{self.task_layer(task)}`
- Runtime mode: `{mode}`
- Completed at: `{now_utc()}`

This marker allows the POC-to-PR workflow to continue on later pushes without repeating this task.
"""
        write_text(worktree / rel, body)

    def commit_and_push_task_to_source_branch(self, worktree: Path, spec: SpecCandidate, task: AgentTask, story_dir: Path, task_dir: Path) -> None:
        """Commit one validated task and push it to the branch that contains the spec.

        This is intentionally not a PR per task. It is for the POC workflow where the
        spec branch is the integration branch and the final PR is created from that
        branch to the repository base branch.
        """
        scopes = self.task_change_scopes(spec, task) if self.run_tasks_in_current_worktree() else None
        if scopes:
            staged_before = git(worktree, "diff", "--cached", "--name-only")
            if staged_before.strip():
                raise OrchestratorError(
                    "Current-worktree task commits require an empty Git index before staging. "
                    "Commit, unstage, or stash existing staged files first."
                )
        exclude_paths = self.source_task_commit_exclude_paths(spec, task, scopes)
        if scopes and exclude_paths is None:
            preexisting = self.preexisting_task_changes(spec, task)
            if preexisting:
                self.write_agent_log(
                    story_dir,
                    "orchestrator",
                    "preexisting_scoped_changes_included",
                    "completed",
                    f"Included {len(preexisting)} preexisting scoped path(s) in source-spec task commit for rerun safety",
                )
        git_add_changed_paths(worktree, scopes=scopes, exclude_paths=exclude_paths)
        staged = git(worktree, "diff", "--cached", "--name-only")
        if not staged.strip():
            self.write_agent_log(story_dir, "orchestrator", "nothing_staged", "completed", f"No commit for {task.task_id}; runtime artifacts were excluded")
            return
        commit_msg = f"{self.commit_type(task)}({safe_slug(task.domain, 20)}): {task.title[:80]}"
        git(worktree, "commit", "-m", commit_msg)
        remote = self.remote_name()
        git(worktree, "push", remote, f"HEAD:refs/heads/{spec.branch}")
        self.refresh_source_branch_ref(spec.branch)
        self.write_agent_log(story_dir, "orchestrator", "task_pushed_to_spec_branch", "completed", f"{task.task_id} pushed to {spec.branch}")
        print(f"    pushed task {task.task_id} to source spec branch {spec.branch}")

    def create_final_pr_from_spec_branch(self, spec: SpecCandidate, story_dir: Path, mode: str) -> None:
        if not self.create_final_pr_from_spec_branch_enabled():
            return
        if self.dry_run:
            self.log(f"    DRY-RUN would create/update final PR from {spec.branch} to {self.final_pr_base_branch()}")
            return
        if which("gh") is None:
            self.write_agent_log(story_dir, "orchestrator", "final_pr_skipped", "blocked", "gh CLI not installed")
            return
        base = self.final_pr_base_branch()
        remote = self.remote_name()
        self.refresh_source_branch_ref(spec.branch)
        existing = gh(self.repo, "pr", "list", "--head", spec.branch, "--base", base, "--json", "url", "--jq", ".[0].url", check=False)
        if existing.strip():
            self.write_agent_log(story_dir, "orchestrator", "final_pr_exists", "completed", existing.strip())
            print(f"    Final PR already exists: {existing.strip()}")
            return
        body_path = story_dir / "final-pr-body.md"
        write_text(body_path, self.create_final_pr_body(spec, story_dir, mode))
        title = f"feat: {spec.title[:90]}"
        draft_flag = ["--draft"] if self.config.get("pr_policy", {}).get("open_as_draft", True) else []
        try:
            url = gh(self.repo, "pr", "create", "--base", base, "--head", spec.branch, "--title", title, "--body-file", str(body_path), *draft_flag)
        except OrchestratorError as exc:
            write_text(story_dir / "final-pr-create-error.txt", str(exc))
            self.write_agent_log(story_dir, "orchestrator", "final_pr_create_failed", "blocked", str(exc)[:400])
            return
        self.write_agent_log(story_dir, "orchestrator", "final_pr_created", "completed", url)
        print(f"    Final PR: {url}")

    def create_final_pr_body(self, spec: SpecCandidate, story_dir: Path, mode: str) -> str:
        evidence_rel = Path(self.config["repository"].get("evidence_dir", "docs/agentic-evidence")) / spec.id
        task_dirs = []
        tasks_root = story_dir / "tasks"
        if tasks_root.exists():
            task_dirs = sorted([p.name for p in tasks_root.iterdir() if p.is_dir()])
        task_list = "\n".join(f"- `{t}`" for t in task_dirs) or "- See agent evidence"
        return f"""{self.manager_mention()}, this final agentic POC implementation PR is ready for your review.

## Source

- Spec branch: `{spec.branch}`
- Spec file: `{spec.path}`
- Spec id: `{spec.id}`
- Runtime mode: `{mode}`

## What the agents did

{task_list}

## Evidence

- Agent log: `{evidence_rel}/**/agents.log.md`
- QA evidence: `{evidence_rel}/**/qa-checklist.md`
- PM evidence: `{evidence_rel}/**/pm-checklist.md`
- Test evidence: `{evidence_rel}/**/test-evidence.md`
- Layer gates: `{evidence_rel}/layer-gates/`

## Required review order

1. Confirm the design/spec intent.
2. Check DB/data model evidence if applicable.
3. Check API/backend evidence if applicable.
4. Check frontend/UI/E2E evidence if applicable.
5. Wait for Codex AI PR Review Gate to pass.
6. Approve or request changes.

## Guardrails

- New AWS components must be Terraform-backed.
- Unit tests alone are not enough when DB/API/frontend integration is required.
- Production deployment remains human-approved unless this repo explicitly configures otherwise.
- The final PR should be understandable and reversible.

## Codex AI review

Codex review is required before human approval. The PR should receive an automated `@codex review` request and the required Codex PR Review Gate status check.
"""

    def create_pr_if_changed(self, worktree: Path, spec: SpecCandidate, task: AgentTask, story_dir: Path, task_dir: Path, mode: str) -> None:
        if self.dry_run:
            self.log("    DRY-RUN would create PR if meaningful non-evidence changes exist")
            return
        if self.push_tasks_to_source_spec_branch():
            # In source-spec-branch mode, QA/PM/layer evidence is part of the
            # final review object, so evidence-only task commits are allowed.
            self.commit_and_push_task_to_source_branch(worktree, spec, task, story_dir, task_dir)
            return
        status = self.reviewable_status(worktree)
        if not status:
            self.write_agent_log(story_dir, "orchestrator", "no_reviewable_changes", "completed", f"No PR for {task.task_id}; only runtime artifacts changed or no changes exist")
            return
        branch = git(worktree, "rev-parse", "--abbrev-ref", "HEAD")
        title = self.pr_title(task)
        pr_body_path = self.create_pr_body(task_dir, spec, task, mode)
        scopes = self.task_change_scopes(spec, task) if self.run_tasks_in_current_worktree() else None
        if scopes:
            staged_before = git(worktree, "diff", "--cached", "--name-only")
            if staged_before.strip():
                raise OrchestratorError(
                    "Current-worktree task PR creation requires an empty Git index before staging. "
                    "Commit, unstage, or stash existing staged files first."
                )
        git_add_changed_paths(worktree, scopes=scopes, exclude_paths=self.preexisting_task_changes(spec, task) if scopes else None)
        staged = git(worktree, "diff", "--cached", "--name-only")
        if not staged.strip():
            self.write_agent_log(story_dir, "orchestrator", "nothing_staged", "completed", f"No PR for {task.task_id}; runtime artifacts were excluded")
            return
        commit_msg = f"{self.commit_type(task)}({safe_slug(task.domain, 20)}): {task.title[:80]}"
        git(worktree, "commit", "-m", commit_msg)
        git(worktree, "push", "-u", "origin", branch)
        if which("gh") is None:
            self.write_agent_log(story_dir, "orchestrator", "pr_skipped", "blocked", "gh CLI not installed")
            return
        draft_flag = ["--draft"] if self.config.get("pr_policy", {}).get("open_as_draft", True) else []
        cmd = ["pr", "create", "--base", spec.branch, "--head", branch, "--title", title, "--body-file", str(pr_body_path), *draft_flag]
        try:
            url = gh(worktree, *cmd)
        except OrchestratorError as exc:
            # Existing PR is not fatal; record the failure for manual review.
            write_text(task_dir / "pr-create-error.txt", str(exc))
            self.write_agent_log(story_dir, "orchestrator", "pr_create_failed", "blocked", str(exc)[:400])
            return
        self.write_agent_log(story_dir, "orchestrator", "pr_created", "completed", url)
        print(f"    PR: {url}")

    def reviewable_status(self, worktree: Path) -> str:
        status = git(worktree, "status", "--porcelain")
        reviewable = []
        evidence_dir = self.config["repository"].get("evidence_dir", "docs/agentic-evidence")
        for line in status.splitlines():
            path = line[3:] if len(line) > 3 else ""
            normalized = path.replace("\\", "/")
            if not normalized or is_runtime_or_generated_path(normalized) or "/__pycache__/" in normalized or normalized.endswith(".pyc"):
                continue
            # Evidence is committed with real implementation changes, but evidence-only
            # branches must not open empty/no-code PRs.
            if is_evidence_path(normalized, evidence_dir=evidence_dir):
                continue
            reviewable.append(line)
        return "\n".join(reviewable)

    def pr_title(self, task: AgentTask) -> str:
        return f"{self.commit_type(task)}({safe_slug(task.domain, 20)}): {task.title[:90]}"

    def commit_type(self, task: AgentTask) -> str:
        if task.domain in {"cloud", "infra"} or task.requires_terraform:
            return "infra"
        if task.domain in {"qa", "test"}:
            return "test"
        if task.title.lower().startswith("fix"):
            return "fix"
        return "feat"

    def create_pr_body(self, task_dir: Path, spec: SpecCandidate, task: AgentTask, mode: str) -> Path:
        evidence_rel = Path(self.config["repository"].get("evidence_dir", "docs/agentic-evidence")) / spec.id / task.task_id
        pr_body = f"""{self.manager_mention()}, this agent-created PR is ready for review.

## Spec comprehension

Business goal: Implement the user/business outcome requested by `{spec.path}`.
Technical goal: {task.responsibility}
User / stakeholder: See source spec.
Source spec: `{spec.branch}:{spec.path}`
Acceptance criteria satisfied:
{chr(10).join(f'- {ac}' for ac in (task.acceptance_criteria or ['See source spec acceptance criteria.']))}

Assumptions:
- See `{evidence_rel}/agents.log.md`.

Clarifications asked / resolved:
- See `{evidence_rel}/agents.log.md`.

## Design / architecture traceability

Design blueprint: `{evidence_rel}/scale-security-architecture-review.md`
Data model / schema evidence: see `{evidence_rel}/test-evidence.md`
API contract evidence: see `{evidence_rel}/test-evidence.md`
Cloud/Terraform evidence: see `{evidence_rel}/test-evidence.md` when applicable
Paradigm decision: see `{evidence_rel}/scale-security-architecture-review.md`

## Layer gate

Layer: `{self.task_layer(task)}`
Layer gate evidence: `docs/agentic-evidence/{spec.id}/layer-gates/{self.task_layer(task)}.passed.md`
Dependency rule: database → API → frontend. Unit tests alone are not enough for done.

## Test traceability

| AC | DB | API contract | Unit | Component | Integration | E2E | Dev/QA | Evidence | Status |
|---|---|---|---|---|---|---|---|---|---|
| See criteria | See evidence | See evidence | See evidence | See evidence | See evidence | See evidence | See evidence | `{evidence_rel}/test-evidence.md` | Human review requested |

## QA checklist

QA checklist path or artifact: `{evidence_rel}/qa-checklist.md`
QA decision: Agent-reviewed; human verification requested.
Open QA feedback:
- See `{evidence_rel}/agents.log.md`.

## PM checklist

PM checklist path or artifact: `{evidence_rel}/pm-checklist.md`
PM decision: Agent-reviewed; human AI PM review requested.
Open PM feedback:
- See `{evidence_rel}/agents.log.md`.

## Mandatory Codex AI review

Codex PR Review Gate: Pending until GitHub Actions completes.
Required status check: `Agentic Codex PR Review / codex_review_gate`
Codex review artifact/comment: GitHub Actions artifact `.agent/codex-review/` and PR gate comment.
Open Codex findings:
- Pending review.

Manager approval must wait until the Codex PR Review Gate passes or the human manager explicitly documents an override.

## Agent iterations / agents.log

agents.log path/artifact: `{evidence_rel}/agents.log.md`

| Agent | Iteration | Stage | Action | Status | Evidence |
|---|---:|---|---|---|---|
| automated team | 1+ | SDLC | see agents.log | see agents.log | `{evidence_rel}/agents.log.md` |

## Agent-to-agent feedback

| Feedback | From | Owner | Severity | Status | Evidence |
|---|---|---|---|---|---|
| See evidence | agent team | owner agent | see log | see log | `{evidence_rel}/agents.log.md` |

## Screenshots / visual evidence

{f'Required for this task. See `{evidence_rel}/visual-evidence.md`.' if task.requires_screenshots else 'Not UI-related unless QA evidence says otherwise.'}

| State | Viewport | Screenshot / annotation | Status |
|---|---|---|---|
| see evidence | see evidence | `{evidence_rel}/visual-evidence.md` | {('Required' if task.requires_screenshots else 'Not applicable')} |

## Summary

Implements one responsibility: **{task.responsibility}**

## Business goal

From spec `{spec.path}` on branch `{spec.branch}`.

## Technical notes

- Task id: `{task.task_id}`
- Domain: `{task.domain}`
- Risk: `{task.risk}`
- PR scope policy: one responsibility only.

## Runtime

Runtime detected: `{mode}`
Bootstrap commands: `.codex/bootstrap.sh` or `.ai/scripts/bootstrap-task-env.sh` when applicable.
Bootstrap result: see `{evidence_rel}/test-evidence.md`.

## Validation

See `{evidence_rel}/test-evidence.md` and `{evidence_rel}/qa-checklist.md`.

```text
Evidence path: {evidence_rel}
```

## Agent self-review

Quality score: see `{evidence_rel}/scale-security-architecture-review.md`
Findings fixed:
- See agent log.
Findings accepted as follow-up:
- See agent log.

## Scale/readiness review

See `{evidence_rel}/scale-security-architecture-review.md`.

Scale consideration:
- Expected current usage: see spec.
- Main growth risk: see scale/security/architecture evidence.
- Boundary/limit added: see implementation and evidence.
- Observability added: see implementation and evidence.
- Follow-up needed before larger scale: see evidence.

## Architecture impact

Pattern/architecture changes: See evidence and changed files.
ADR required: Agent to mark Yes/No in evidence.
ADR link: See evidence if applicable.
Reversibility: Two-way door unless evidence says otherwise.

## Security impact

Auth/authz changed: See changed files and evidence.
Sensitive data touched: See evidence.
Secrets/config touched: See evidence.
Security reviewer required: Required if auth, secrets, infrastructure, IAM, billing, data deletion, or production config changed.

## Cloud / deployment impact

Cloud/infrastructure changed: {'Yes' if task.requires_terraform or task.domain in {'cloud', 'infra'} else 'No unless evidence says otherwise'}
Deployment changed: See changed files and evidence.
Promotion target: source branch `{spec.branch}` first; production remains human-approved.
Production deployment required: No by default.

## Deletions and data safety

Files deleted: See git diff.
Data deletion risk: See evidence.
Approval required: Yes for protected deletions, migrations, auth/security, billing, production config, or infrastructure.

## Risk

Risk level: `{task.risk}`
Reason: Agent classification from the task plan.

## Rollback

Rollback by reverting this PR. Production deployment remains human-approved unless the repo explicitly configures otherwise.

## Files worth reviewing carefully

- Review changed files in `{task.domain}` scope.
- Review `{evidence_rel}/test-evidence.md`.
- Review `{evidence_rel}/qa-checklist.md`.
- Review `{evidence_rel}/pm-checklist.md`.

## Human AI PM requested action

Review / Approve / Request changes / Decide tradeoff

## Agent checklist

- [ ] Design-first blueprint reviewed before coding.
- [ ] Data model/API/cloud/frontend structure is explicit or marked not applicable.
- [ ] Appropriate paradigm selected and documented.
- [ ] Acceptance criteria satisfied.
- [ ] Layer gate passed for this PR responsibility.
- [ ] QA checklist completed and passed or gaps documented.
- [ ] PM checklist completed and passed or human decision requested.
- [ ] Agent feedback closed or explicitly deferred.
- [ ] agents.log summary included.
- [ ] Screenshots/visual evidence included for UI changes.
- [ ] Accessibility reviewed for user-facing changes.
- [ ] Relevant tests added or updated.
- [ ] Validation commands run.
- [ ] Self-review completed.
- [ ] Scale/readiness review completed.
- [ ] No unrelated broad refactor.
- [ ] No protected file deletion.
- [ ] No secrets committed.
- [ ] Risk documented.
- [ ] Rollback documented.
"""
        path = task_dir / "pr-body.md"
        write_text(path, pr_body)
        return path

    def manager_mention(self) -> str:
        manager = self.config.get("manager", {}).get("github_user", "")
        return f"@{manager}" if manager else "AI PM"

    def ensure_cloud_explicit(self, mode: str) -> None:
        if mode != "cloud":
            return
        if not self.cloud_mode_allowed(explicit=False):
            env_var = self.config.get("codex", {}).get("cloud_opt_in_env_var", "AGENTIC_EXPLICIT_CLOUD")
            raise OrchestratorError(
                "Cloud mode is disabled by default. Re-run with --mode cloud only after explicitly setting "
                f"{env_var}=true or using --allow-cloud. Local mode is the default runtime."
            )

    def run_spec(self, branch: str, spec_path: str, mode: str, fetch: bool = True) -> int:
        self.ensure_cloud_explicit(mode)
        spec = self.get_spec_candidate(branch=branch, spec_path=spec_path, fetch=fetch)
        normalized_status = normalize_spec_status(spec.status or "")
        if normalized_status == "completed":
            self.log(f"Spec is already completed; skipping: {branch}:{spec_path}")
            return 0
        if not self.is_spec_ready(spec):
            print(f"[ERROR] spec is not ready for autonomous implementation: {spec.status or 'no-status'}", file=sys.stderr)
            return 1
        if not self.validate_spec_candidate(spec):
            return 1
        if self.existing_agent_branch_for_spec(spec) and self.config["repository"].get("skip_specs_with_existing_agent_branch", True):
            self.log(f"Existing agent branch found for {spec.id}; skipping to avoid duplicate PRs.")
            return 0
        try:
            completed = self.implement_spec(spec, mode=mode, mark_seen=True)
        except Exception as exc:
            run_id = self.make_run_id(spec, prefix="fail")
            if not self.dry_run:
                self.mark_spec_seen(spec, status="failed", run_id=run_id)
            print(f"[ERROR] processing {spec.id}: {exc}", file=sys.stderr)
            if self.verbose:
                raise
            return 1
        if not completed:
            return 1
        return 0

    def cloud_plan(self) -> int:
        candidates = self.scan(fetch=True)
        new = self.new_specs(candidates)
        report = {
            "generated_at": now_utc(),
            "new_specs": [s.__dict__ for s in new],
            "cloud_safe_work": [
                "spec gap analysis",
                "CI failure debugging",
                "test generation",
                "static security review",
                "Terraform fmt/validate/plan",
                "Lambda/API debugging when logs and scoped credentials are configured",
                "PR evidence and documentation improvements",
            ],
            "local_only_gaps": [
                "localhost-only UI tests unless CI can run the app",
                "manual exploratory testing on your laptop",
                "local database inspection without remote access",
            ],
        }
        path = self.state_dir / "cloud-plan.json"
        write_json(path, report)
        print(f"Cloud continuation plan written to {path}")
        print(json.dumps(report, indent=2))
        return 0

    def status(self) -> int:
        print("Agentic SDLC status")
        print(f"registry: {self.registry_path}")
        seen = self.registry.get("seen", {})
        print(f"tracked spec versions: {len(seen)}")
        for key, item in sorted(seen.items(), key=lambda kv: kv[1].get("updated_at", ""), reverse=True)[:20]:
            print(f"- {item.get('status')} {item.get('spec_id')} {item.get('branch')}:{item.get('path')} at {item.get('updated_at')}")
        return 0

    def watch(self, mode: str, poll_seconds: int, max_specs: Optional[int]) -> int:
        self.ensure_cloud_explicit(mode)
        print(f"Starting agentic SDLC watch loop in {mode} mode. Ctrl+C to stop.")
        while True:
            try:
                self.run_once(mode=mode, max_specs=max_specs, fetch=True)
            except KeyboardInterrupt:
                print("Stopping watch loop.")
                return 0
            except Exception as exc:
                print(f"Watch loop error: {exc}", file=sys.stderr)
                if self.verbose:
                    raise
            time.sleep(poll_seconds)


def deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    result = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Agentic SDLC repo automation")
    parser.add_argument("--repo", type=Path, default=None, help="Repository root. Defaults to current git repo.")
    parser.add_argument("--config", type=Path, default=None, help="Config JSON path.")
    parser.add_argument("--dry-run", action="store_true", help="Generate plans/prompts without creating branches or running Codex.")
    parser.add_argument("--verbose", action="store_true", help="Show debug output.")
    parser.add_argument("--allow-cloud", action="store_true", help="Explicitly allow --mode cloud for this run. Default is local-only.")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("doctor")
    scan = sub.add_parser("scan")
    scan.add_argument("--no-fetch", action="store_true")

    run_once = sub.add_parser("run-once")
    run_once.add_argument("--mode", choices=["local", "cloud"], default="local")
    run_once.add_argument("--max-specs", type=int, default=None)
    run_once.add_argument("--no-fetch", action="store_true")
    run_once.add_argument("--dry-run", action="store_true", default=argparse.SUPPRESS, help="Also accepted here for convenience; same as global --dry-run.")

    run_spec = sub.add_parser("run-spec")
    run_spec.add_argument("--branch", required=True, help="Source branch containing the spec.")
    run_spec.add_argument("--spec", required=True, help="Spec path in the source branch.")
    run_spec.add_argument("--mode", choices=["local", "cloud"], default="local")
    run_spec.add_argument("--no-fetch", action="store_true")
    run_spec.add_argument("--dry-run", action="store_true", default=argparse.SUPPRESS, help="Also accepted here for convenience; same as global --dry-run.")

    watch = sub.add_parser("watch")
    watch.add_argument("--mode", choices=["local", "cloud"], default="local")
    watch.add_argument("--poll-seconds", type=int, default=180)
    watch.add_argument("--max-specs", type=int, default=None)

    sub.add_parser("cloud-plan")
    sub.add_parser("status")
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        repo = (args.repo.resolve() if args.repo else repo_root())
        dry_run = bool(args.dry_run or getattr(args, "dry_run", False))
        orchestrator = AgenticSDLC(repo=repo, config_path=args.config, dry_run=dry_run, verbose=args.verbose)
        if args.command == "doctor":
            return orchestrator.doctor()
        if args.command == "scan":
            orchestrator.scan(fetch=not args.no_fetch)
            return 0
        if args.command in {"run-once", "run-spec", "watch"} and getattr(args, "mode", "local") == "cloud":
            env_var = orchestrator.config.get("codex", {}).get("cloud_opt_in_env_var", "AGENTIC_EXPLICIT_CLOUD")
            if args.allow_cloud:
                os.environ[env_var] = orchestrator.config.get("codex", {}).get("cloud_opt_in_value", "true")
            elif not orchestrator.cloud_mode_allowed(explicit=False):
                print(f"[ERROR] cloud mode is blocked by local-first policy. Re-run with --allow-cloud or set {env_var}=true only when cloud execution is explicitly intended.", file=sys.stderr)
                return 2
        if args.command == "run-once":
            return orchestrator.run_once(mode=args.mode, max_specs=args.max_specs, fetch=not args.no_fetch)
        if args.command == "run-spec":
            return orchestrator.run_spec(branch=args.branch, spec_path=args.spec, mode=args.mode, fetch=not args.no_fetch)
        if args.command == "watch":
            return orchestrator.watch(mode=args.mode, poll_seconds=args.poll_seconds, max_specs=args.max_specs)
        if args.command == "cloud-plan":
            return orchestrator.cloud_plan()
        if args.command == "status":
            return orchestrator.status()
        parser.error(f"Unknown command: {args.command}")
        return 2
    except OrchestratorError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
