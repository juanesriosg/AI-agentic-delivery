#!/usr/bin/env python3
"""Focused regression tests for agentic_sdlc task sequencing."""

from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("agentic_sdlc.py")
SPEC = importlib.util.spec_from_file_location("agentic_sdlc", MODULE_PATH)
assert SPEC and SPEC.loader
agentic_sdlc = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = agentic_sdlc
SPEC.loader.exec_module(agentic_sdlc)


CRUD_SPEC = """---
doc_type: task_list
status: ready_for_agents
---

# Task List - CRUD Smoke Page

Build a small CRUD page with a React frontend and a Python backend API.

## Agentic Split Task Progress

- [x] `crud-design-gate` - Clarify design and contracts.
- [ ] `crud-database` - Add local data model.
- [ ] `crud-api` - Add Python CRUD API.
- [ ] `crud-frontend` - Add React CRUD page.
"""


LEGACY_WORKER_WRAPPER_SPEC = """---
doc_type: task_list
status: ready_for_agents
title: "Task List - Worker Wrapper and Artifact Contract"
source_trd: "specs/city-pipeline-aws-cost-mvp/trds/trd-p0-f1-t1-worker-wrapper-artifacts.md"
completed_at: "2026-05-20T13:29:54Z"
---

# Task List - P0-F1-T1

## Tasks

- [x] 1.0 Add wrapper module and CLI.
- [x] 2.0 Add artifact manifest builder.
- [x] 3.0 Add local fixture mode and tests.

---

Task completed by agentic SDLC.

- Completed task id: `worker-wrapper-design-gate`
- Completed task title: Clarify worker wrapper design
"""


def make_orchestrator() -> object:
    orchestrator = agentic_sdlc.AgenticSDLC.__new__(agentic_sdlc.AgenticSDLC)
    orchestrator.config = {
        "layer_gates": {
            "enabled": True,
            "order": ["design", "cloud", "database", "api", "frontend", "qa", "pm"],
        },
        "repository": {"evidence_dir": "docs/agentic-evidence"},
        "branching": {
            "push_tasks_to_source_spec_branch": True,
            "run_tasks_in_current_worktree": False,
        },
        "codex": {"sandbox": "workspace-write", "approval_policy": "never"},
    }
    orchestrator.write_agent_log = lambda *args, **kwargs: None
    orchestrator.task_completed_in_source_branch_by_id = lambda *args, **kwargs: False
    return orchestrator


class AgenticSdlcDependencyTests(unittest.TestCase):
    def test_path_scope_matching_accepts_children_without_sibling_leakage(self) -> None:
        scopes = ["city_pipelines/cloud", "docs/agentic-evidence/spec/task"]

        self.assertTrue(agentic_sdlc.path_within_scopes("city_pipelines/cloud/artifacts.py", scopes))
        self.assertTrue(agentic_sdlc.path_within_scopes("docs/agentic-evidence/spec/task/test-evidence.md", scopes))
        self.assertFalse(agentic_sdlc.path_within_scopes("city_pipelines/cloud_extra/artifacts.py", scopes))
        self.assertFalse(agentic_sdlc.path_within_scopes("docs/agentic-evidence/spec/other/test-evidence.md", scopes))

    def test_git_add_changed_paths_can_stage_only_task_scopes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            subprocess.run(["git", "init"], cwd=repo, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            subprocess.run(["git", "config", "user.email", "agent@example.com"], cwd=repo, check=True)
            subprocess.run(["git", "config", "user.name", "Agent"], cwd=repo, check=True)
            (repo / "tracked.txt").write_text("base\n", encoding="utf-8")
            subprocess.run(["git", "add", "tracked.txt"], cwd=repo, check=True)
            subprocess.run(["git", "commit", "-m", "base"], cwd=repo, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            (repo / "tracked.txt").write_text("changed\n", encoding="utf-8")
            (repo / "task").mkdir()
            (repo / "task" / "owned.txt").write_text("owned\n", encoding="utf-8")
            (repo / "other.txt").write_text("other\n", encoding="utf-8")

            staged = agentic_sdlc.git_add_changed_paths(repo, scopes=["task"])
            cached = subprocess.run(
                ["git", "diff", "--cached", "--name-only"],
                cwd=repo,
                check=True,
                text=True,
                stdout=subprocess.PIPE,
            ).stdout.splitlines()

            self.assertEqual(staged, ["task/owned.txt"])
            self.assertEqual(cached, ["task/owned.txt"])

    def test_current_worktree_mode_can_be_enabled_by_config_or_env(self) -> None:
        orchestrator = make_orchestrator()

        self.assertFalse(orchestrator.run_tasks_in_current_worktree())
        orchestrator.config["branching"]["run_tasks_in_current_worktree"] = True
        self.assertTrue(orchestrator.run_tasks_in_current_worktree())
        orchestrator.config["branching"]["run_tasks_in_current_worktree"] = False

        old_value = os.environ.get("AGENTIC_RUN_IN_CURRENT_WORKTREE")
        try:
            os.environ["AGENTIC_RUN_IN_CURRENT_WORKTREE"] = "true"
            self.assertTrue(orchestrator.run_tasks_in_current_worktree())
        finally:
            if old_value is None:
                os.environ.pop("AGENTIC_RUN_IN_CURRENT_WORKTREE", None)
            else:
                os.environ["AGENTIC_RUN_IN_CURRENT_WORKTREE"] = old_value

    def test_task_change_scopes_include_expected_evidence_layer_and_spec_paths(self) -> None:
        orchestrator = make_orchestrator()
        spec = agentic_sdlc.SpecCandidate(
            branch="dev/task-f1-t1",
            path="specs/city-pipeline-aws-cost-mvp/tasks/tasks-trd-p0-f1-t1-worker-wrapper-artifacts.md",
            sha="aaa",
            content=LEGACY_WORKER_WRAPPER_SPEC,
            status="ready_for_agents",
        )
        task = agentic_sdlc.AgentTask(
            task_id="artifact-manifest-contract",
            title="Add artifact manifest contract",
            responsibility="Define manifest.",
            domain="backend",
            acceptance_criteria=["Manifest is defined."],
            expected_paths=["city_pipelines/cloud/artifacts.py"],
            layer="database",
            depends_on=["worker-wrapper-design-gate"],
        )

        scopes = orchestrator.task_change_scopes(spec, task)

        self.assertIn("city_pipelines/cloud/artifacts.py", scopes)
        self.assertIn(f"docs/agentic-evidence/{spec.id}/artifact-manifest-contract", scopes)
        self.assertIn(f"docs/agentic-evidence/{spec.id}/layer-gates", scopes)
        self.assertIn(spec.path, scopes)

    def test_windows_worktree_shell_scripts_are_normalized_to_lf(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            scripts = repo / ".ai" / "scripts"
            scripts.mkdir(parents=True)
            shell_script = scripts / "detect-runtime.sh"
            python_script = scripts / "helper.py"
            shell_script.write_bytes(b"#!/usr/bin/env bash\r\nset -euo pipefail\r\necho ok\r\n")
            python_script.write_bytes(b"print('untouched')\r\n")

            changed = agentic_sdlc.normalize_shell_script_line_endings(repo)

            self.assertEqual(changed, [".ai/scripts/detect-runtime.sh"])
            self.assertNotIn(b"\r", shell_script.read_bytes())
            self.assertIn(b"\r", python_script.read_bytes())

    def test_nested_codex_agents_use_full_access_for_all_stages(self) -> None:
        orchestrator = make_orchestrator()

        self.assertEqual(orchestrator.codex_sandbox(allow_write=False), "danger-full-access")
        self.assertEqual(orchestrator.codex_sandbox(allow_write=True), "danger-full-access")
        self.assertEqual(orchestrator.codex_approval_policy(), "never")

    def test_spec_id_is_stable_for_crud_spec_progress_updates(self) -> None:
        first = agentic_sdlc.SpecCandidate(
            branch="dev/crud-smoke",
            path="specs/crud-smoke/tasks.md",
            sha="aaa",
            content=CRUD_SPEC,
            status="ready_for_agents",
        )
        second = agentic_sdlc.SpecCandidate(
            branch="dev/crud-smoke",
            path="specs/crud-smoke/tasks.md",
            sha="bbb",
            content=CRUD_SPEC + "\n- [x] `crud-database` - Add local data model.\n",
            status="ready_for_agents",
        )

        self.assertEqual(first.id, second.id)

    def test_crud_react_python_tasks_are_ordered_by_dependencies_before_layer_rank(self) -> None:
        orchestrator = make_orchestrator()
        tasks = [
            agentic_sdlc.AgentTask(
                task_id="crud-container",
                title="Container smoke",
                responsibility="Package smoke validation.",
                domain="cloud",
                acceptance_criteria=["Container smoke runs after frontend is complete."],
                layer="cloud",
                depends_on=["crud-frontend"],
            ),
            agentic_sdlc.AgentTask(
                task_id="crud-frontend",
                title="React CRUD page",
                responsibility="Implement React CRUD screen.",
                domain="frontend",
                acceptance_criteria=["React page calls the real Python API."],
                layer="frontend",
                depends_on=["crud-api"],
            ),
            agentic_sdlc.AgentTask(
                task_id="crud-api",
                title="Python CRUD API",
                responsibility="Implement Python CRUD endpoints.",
                domain="backend",
                acceptance_criteria=["Python API exposes CRUD behavior."],
                layer="api",
                depends_on=["crud-database"],
            ),
            agentic_sdlc.AgentTask(
                task_id="crud-database",
                title="Local CRUD data model",
                responsibility="Implement local persistence contract.",
                domain="database",
                acceptance_criteria=["Data model supports CRUD records."],
                layer="database",
                depends_on=["crud-design-gate"],
            ),
        ]

        ordered = orchestrator.order_tasks_by_layer(tasks)

        self.assertEqual(
            [task.task_id for task in ordered],
            ["crud-database", "crud-api", "crud-frontend", "crud-container"],
        )

    def test_crud_task_list_progress_creates_local_plan_without_codex(self) -> None:
        orchestrator = make_orchestrator()
        spec = agentic_sdlc.SpecCandidate(
            branch="dev/crud-smoke",
            path="specs/crud-smoke/tasks.md",
            sha="aaa",
            content=CRUD_SPEC,
            status="ready_for_agents",
        )

        tasks = orchestrator.plan_tasks_from_task_list(spec)
        ordered = orchestrator.order_tasks_by_layer(tasks)

        self.assertEqual(
            [task.task_id for task in ordered],
            ["crud-database", "crud-api", "crud-frontend"],
        )
        self.assertEqual(ordered[0].layer, "database")
        self.assertEqual(ordered[1].layer, "api")
        self.assertEqual(ordered[2].layer, "frontend")
        self.assertEqual(ordered[0].depends_on, ["crud-design-gate"])
        self.assertEqual(ordered[1].depends_on, ["crud-database"])
        self.assertEqual(ordered[2].depends_on, ["crud-api"])

    def test_worker_wrapper_task_list_progress_uses_code_producing_first_task(self) -> None:
        orchestrator = make_orchestrator()
        spec = agentic_sdlc.SpecCandidate(
            branch="dev/worker-artifacts",
            path="specs/city-pipeline-aws-cost-mvp/tasks/tasks-trd-p0-f1-t1-worker-wrapper-artifacts.md",
            sha="aaa",
            content="""---
doc_type: task_list
status: ready_for_agents
---

# Task List - Worker Wrapper and Artifact Contract

## Agentic Split Task Progress

- [x] `worker-wrapper-design-gate` - Clarify worker wrapper design.
- [ ] `artifact-manifest-contract` - Add artifact manifest contract.
- [ ] `worker-wrapper-cli` - Add wrapper CLI.
- [ ] `container-entrypoint-alignment` - Align container entrypoint.
""",
            status="ready_for_agents",
        )

        tasks = orchestrator.order_tasks_by_layer(orchestrator.plan_tasks_from_task_list(spec))

        self.assertEqual([task.task_id for task in tasks], [
            "artifact-manifest-contract",
            "worker-wrapper-cli",
            "cdp-security-runtime-guard",
            "local-fixture-worker-mode",
            "container-entrypoint-alignment",
            "worker-wrapper-qa-evidence",
            "worker-wrapper-pm-pr-notice",
        ])
        self.assertEqual(tasks[0].expected_paths[1], "city_pipelines/cloud/artifacts.py")
        self.assertEqual(tasks[0].depends_on, ["worker-wrapper-design-gate"])
        self.assertEqual(tasks[2].depends_on, ["worker-wrapper-cli"])

    def test_worker_wrapper_legacy_task_list_without_progress_uses_canonical_plan(self) -> None:
        orchestrator = make_orchestrator()
        spec = agentic_sdlc.SpecCandidate(
            branch="dev/task-f1-t1",
            path="specs/city-pipeline-aws-cost-mvp/tasks/tasks-trd-p0-f1-t1-worker-wrapper-artifacts.md",
            sha="aaa",
            content=LEGACY_WORKER_WRAPPER_SPEC,
            status="ready_for_agents",
        )

        tasks = orchestrator.order_tasks_by_layer(orchestrator.plan_tasks_from_task_list(spec))

        self.assertEqual([task.task_id for task in tasks], [
            "artifact-manifest-contract",
            "worker-wrapper-cli",
            "cdp-security-runtime-guard",
            "local-fixture-worker-mode",
            "container-entrypoint-alignment",
            "worker-wrapper-qa-evidence",
            "worker-wrapper-pm-pr-notice",
        ])
        self.assertEqual(tasks[0].depends_on, ["worker-wrapper-design-gate"])

    def test_worker_wrapper_marking_adds_full_progress_section_when_missing(self) -> None:
        orchestrator = make_orchestrator()
        task = agentic_sdlc.AgentTask(
            task_id="artifact-manifest-contract",
            title="Add artifact manifest contract",
            responsibility="Define manifest.",
            domain="backend",
            acceptance_criteria=["Manifest is defined."],
            layer="database",
            depends_on=["worker-wrapper-design-gate"],
        )

        updated = orchestrator.mark_task_progress_checkbox_done(LEGACY_WORKER_WRAPPER_SPEC, task)

        self.assertIn("- [x] `worker-wrapper-design-gate` - Clarify worker wrapper design", updated)
        self.assertIn("- [x] `artifact-manifest-contract` - Add artifact manifest contract", updated)
        self.assertIn("- [ ] `worker-wrapper-cli` - Add wrapper CLI", updated)

    def test_worker_wrapper_dependency_accepts_legacy_completion_note(self) -> None:
        orchestrator = make_orchestrator()
        spec = agentic_sdlc.SpecCandidate(
            branch="dev/task-f1-t1",
            path="specs/city-pipeline-aws-cost-mvp/tasks/tasks-trd-p0-f1-t1-worker-wrapper-artifacts.md",
            sha="aaa",
            content=LEGACY_WORKER_WRAPPER_SPEC,
            status="ready_for_agents",
        )
        task = agentic_sdlc.AgentTask(
            task_id="artifact-manifest-contract",
            title="Add artifact manifest contract",
            responsibility="Define manifest.",
            domain="backend",
            acceptance_criteria=["Manifest is defined."],
            layer="database",
            depends_on=["worker-wrapper-design-gate"],
        )

        with tempfile.TemporaryDirectory() as tmp:
            task_dir = Path(tmp)
            orchestrator.ensure_task_dependencies_satisfied(
                spec,
                task,
                story_dir=task_dir,
                task_dir=task_dir,
                completed_task_ids=set(),
            )

    def test_task_dependency_preflight_blocks_unfinished_crud_backend_dependency(self) -> None:
        orchestrator = make_orchestrator()
        spec = agentic_sdlc.SpecCandidate(
            branch="dev/crud-smoke",
            path="specs/crud-smoke/tasks.md",
            sha="aaa",
            content=CRUD_SPEC,
            status="ready_for_agents",
        )
        task = agentic_sdlc.AgentTask(
            task_id="crud-frontend",
            title="React CRUD page",
            responsibility="Implement React CRUD screen.",
            domain="frontend",
            acceptance_criteria=["React page calls the real Python API."],
            layer="frontend",
            depends_on=["crud-api"],
        )

        with tempfile.TemporaryDirectory() as tmp:
            task_dir = Path(tmp)
            with self.assertRaises(agentic_sdlc.TaskDependencyBlocked):
                orchestrator.ensure_task_dependencies_satisfied(
                    spec,
                    task,
                    story_dir=task_dir,
                    task_dir=task_dir,
                    completed_task_ids=set(),
                )
            self.assertTrue((task_dir / "task-dependency-blocked.md").exists())

    def test_task_dependency_preflight_accepts_completed_crud_design_checkbox(self) -> None:
        orchestrator = make_orchestrator()
        spec = agentic_sdlc.SpecCandidate(
            branch="dev/crud-smoke",
            path="specs/crud-smoke/tasks.md",
            sha="aaa",
            content=CRUD_SPEC,
            status="ready_for_agents",
        )
        task = agentic_sdlc.AgentTask(
            task_id="crud-database",
            title="Local CRUD data model",
            responsibility="Implement local persistence contract.",
            domain="database",
            acceptance_criteria=["Data model supports CRUD records."],
            layer="database",
            depends_on=["crud-design-gate"],
        )

        with tempfile.TemporaryDirectory() as tmp:
            task_dir = Path(tmp)
            orchestrator.ensure_task_dependencies_satisfied(
                spec,
                task,
                story_dir=task_dir,
                task_dir=task_dir,
                completed_task_ids=set(),
            )


if __name__ == "__main__":
    unittest.main()
