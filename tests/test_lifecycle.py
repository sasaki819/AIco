"""CLI / E2E tests for install.py, init.py, update.py, upgrade.py, and sequential migrations."""

from __future__ import annotations

import json
import re
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

from tests.helpers import (
    INSTALLER_DIR,
    REPO_ROOT,
    create_symlink_or_skip,
    git,
    init_git_repo,
    make_source_copy,
    parse_json_output,
    run_cmd,
    run_script,
    run_wrapper,
    setup_installed_repo,
    snapshot_tree,
)


def _create_mock_remote_bare_repo(base_dir: Path, versions: list[tuple[str, int, dict[str, str]]]) -> Path:
    """Create a local bare Git repo tagged with vX.Y.Z releases to act as a remote Git URL."""
    base_dir.mkdir(parents=True, exist_ok=True)
    work = base_dir / "work_remote"
    bare = base_dir / "origin.git"
    git(base_dir, "init", "--bare", str(bare))

    for idx, (ver, schema_ver, extra_migrations) in enumerate(versions):
        stage = base_dir / f"stage_{ver}"
        make_source_copy(stage, version=ver, schema_version=schema_ver, strip_git=True)
        for m_name, m_code in extra_migrations.items():
            (stage / "installer" / "migrations" / m_name).write_text(m_code, encoding="utf-8", newline="\n")

        if idx == 0:
            stage.rename(work)
            git(work, "init", "-b", "main")
            git(work, "config", "user.name", "Release")
            git(work, "config", "user.email", "release@example.com")
            git(work, "remote", "add", "origin", str(bare))
        else:
            shutil.rmtree(work / "template")
            shutil.rmtree(work / "installer")
            shutil.copytree(stage / "template", work / "template")
            shutil.copytree(stage / "installer", work / "installer")

        # Marker in AGENTS.md so we can verify managed block updates cleanly
        agents_p = work / "template" / "AGENTS.md"
        agents_txt = agents_p.read_text(encoding="utf-8")
        agents_txt = agents_txt.replace("\n<!-- AICO:END -->", f"\n<!-- version:{ver} -->\n<!-- AICO:END -->")
        agents_p.write_text(agents_txt, encoding="utf-8", newline="\n")

        git(work, "add", "-A")
        git(work, "commit", "-m", f"release: v{ver}")
        git(work, "tag", f"v{ver}")
        git(work, "push", "origin", "main", "--tags")

    return bare


class TestInstallAndInit(unittest.TestCase):
    def test_install_from_three_sources_and_existing_agents_preserved(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)

            # Prepare 3 source types: (1) local git clone, (2) .git-less archive, (3) bare remote repo
            src_clone = make_source_copy(base / "src_clone", version="0.1.0", strip_git=False)
            src_archive = make_source_copy(base / "src_archive", version="0.1.0", strip_git=True)
            bare_remote = _create_mock_remote_bare_repo(base / "remote", [("0.1.0", 1, {})])
            remote_url = bare_remote.as_uri()

            # Case 1: local clone + existing AGENTS.md -> preserves outer content, source_repository == ""
            repo1 = init_git_repo(base / "proj1", default_branch="main")
            (repo1 / "AGENTS.md").write_text("# My Project Rules\n\nKeep me intact.\n", encoding="utf-8", newline="\n")
            git(repo1, "add", ".")
            git(repo1, "commit", "-m", "add existing AGENTS.md")

            # Dry-run leaves repo untouched
            snap = snapshot_tree(repo1)
            p_dry = run_cmd(
                [sys.executable, str(src_clone / "installer" / "install.py"), "--dry-run", "--json"],
                repo1,
            )
            self.assertEqual(p_dry.returncode, 0, p_dry.stdout + p_dry.stderr)
            self.assertEqual(snapshot_tree(repo1), snap)

            # Actual install from local clone
            p1 = run_cmd(
                [sys.executable, str(src_clone / "installer" / "install.py"), "--json"],
                repo1,
            )
            self.assertEqual(p1.returncode, 0, p1.stdout + p1.stderr)
            agents_after = (repo1 / "AGENTS.md").read_text(encoding="utf-8")
            self.assertIn("# My Project Rules\n\nKeep me intact.", agents_after)
            self.assertIn("<!-- AICO:BEGIN -->", agents_after)
            # CLAUDE.md must NOT be placed by install.py (delegated to init / sync_agents.py)
            self.assertFalse((repo1 / "CLAUDE.md").exists())
            m1 = json.loads((repo1 / "management" / "aico-manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(m1["source_repository"], "")

            # Case 2: .git-less extracted archive -> source_repository == "" (no local path leak!)
            repo2 = init_git_repo(base / "proj2", default_branch="main")
            p2 = run_cmd(
                [sys.executable, str(INSTALLER_DIR / "install.py"), "--source", str(src_archive), "--json"],
                repo2,
            )
            self.assertEqual(p2.returncode, 0, p2.stdout + p2.stderr)
            m2 = json.loads((repo2 / "management" / "aico-manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(m2["source_repository"], "")

            # Case 3: remote mock Git URL -> records remote URL in source_repository
            repo3 = init_git_repo(base / "proj3", default_branch="main")
            p3 = run_cmd(
                [
                    sys.executable,
                    str(INSTALLER_DIR / "install.py"),
                    "--source",
                    remote_url,
                    "--ref",
                    "v0.1.0",
                    "--json",
                ],
                repo3,
            )
            self.assertEqual(p3.returncode, 0, p3.stdout + p3.stderr)
            m3 = json.loads((repo3 / "management" / "aico-manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(m3["source_repository"], remote_url)

    def test_install_custom_management_root_and_all_conflict_guards(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            repo = init_git_repo(base / "custom_proj", default_branch="main")

            # Guard 1: Non-git-root execution fails (exit 1)
            sub = repo / "subdir"
            sub.mkdir()
            p_sub = run_cmd([sys.executable, str(INSTALLER_DIR / "install.py"), "--source", str(REPO_ROOT)], sub)
            self.assertEqual(p_sub.returncode, 1)

            # Guard 2: Dirty tree fails without --allow-dirty
            (repo / "dirty.txt").write_text("x\n", encoding="utf-8", newline="\n")
            p_dirty = run_cmd([sys.executable, str(INSTALLER_DIR / "install.py"), "--source", str(REPO_ROOT)], repo)
            self.assertEqual(p_dirty.returncode, 1)
            (repo / "dirty.txt").unlink()

            # Guard 3: Custom CLAUDE.md conflict stops with zero writes
            (repo / "CLAUDE.md").write_text("# Custom Claude Instructions\n", encoding="utf-8", newline="\n")
            git(repo, "add", "CLAUDE.md")
            git(repo, "commit", "-m", "add custom CLAUDE.md")
            snap_c = snapshot_tree(repo)
            p_cl = run_cmd([sys.executable, str(INSTALLER_DIR / "install.py"), "--source", str(REPO_ROOT)], repo)
            self.assertEqual(p_cl.returncode, 1)
            self.assertEqual(snapshot_tree(repo), snap_c)
            git(repo, "rm", "CLAUDE.md")
            git(repo, "commit", "-m", "remove custom CLAUDE.md")

            # Install with custom --management-root
            custom_root = "docs/aico-mgmt"
            p_ok = run_cmd(
                [
                    sys.executable,
                    str(INSTALLER_DIR / "install.py"),
                    "--source",
                    str(REPO_ROOT),
                    "--management-root",
                    custom_root,
                    "--json",
                ],
                repo,
            )
            self.assertEqual(p_ok.returncode, 0, p_ok.stdout + p_ok.stderr)
            self.assertIn(f'AICO_DEFAULT_MANAGEMENT_ROOT="{custom_root}"', (repo / "tools" / "aico.sh").read_text(encoding="utf-8"))
            self.assertIn(r'set "AICO_DEFAULT_MANAGEMENT_ROOT=docs\aico-mgmt"', (repo / "tools" / "aico.bat").read_text(encoding="utf-8"))

            # Guard 4: Re-running install.py on already-installed repo fails with zero changes
            git(repo, "add", ".")
            git(repo, "commit", "-m", "install custom root")
            snap_dup = snapshot_tree(repo)
            p_dup = run_cmd(
                [sys.executable, str(INSTALLER_DIR / "install.py"), "--source", str(REPO_ROOT), "--management-root", "other-mgmt"],
                repo,
            )
            self.assertEqual(p_dup.returncode, 1)
            self.assertEqual(snapshot_tree(repo), snap_dup)

            # Verify wrapper line endings (aico.sh -> LF, aico.bat -> CRLF)
            sh_bytes = (repo / "tools" / "aico.sh").read_bytes()
            bat_bytes = (repo / "tools" / "aico.bat").read_bytes()
            self.assertNotIn(b"\r", sh_bytes)
            self.assertIn(b"\r\n", bat_bytes)
            self.assertNotIn(b"\n", bat_bytes.replace(b"\r\n", b""))

            # tools/aico.{sh,bat} init & doctor work seamlessly with custom management root!
            p_init = run_wrapper(
                repo,
                "init",
                "--integration-branch",
                "main",
                "--tools",
                "claude,codex",
                "--json",
            )
            self.assertEqual(p_init.returncode, 0, p_init.stdout + p_init.stderr)
            self.assertTrue((repo / "CLAUDE.md").is_file())
            self.assertTrue((repo / ".codex" / "agents" / "worker-high.toml").is_file())
            self.assertFalse((repo / ".github" / "skills").exists())

            # Re-running init removing claude cleans up AIco-managed CLAUDE.md & .claude/skills/
            p_reinit = run_wrapper(repo, "init", "--tools", "codex", "--json")
            self.assertEqual(p_reinit.returncode, 0, p_reinit.stdout + p_reinit.stderr)
            self.assertFalse((repo / "CLAUDE.md").exists())
            self.assertFalse((repo / ".claude" / "skills").exists())

            # Non-TTY init with no args does not hang and --dry-run changes nothing
            snap_init = snapshot_tree(repo)
            p_nontty = run_wrapper(repo, "init", "--dry-run", "--json", stdin_text="")
            self.assertEqual(p_nontty.returncode, 0, p_nontty.stdout + p_nontty.stderr)
            self.assertEqual(snapshot_tree(repo), snap_init)


class TestUpdateUpgradeAndMigrations(unittest.TestCase):
    def test_upgrade_preserves_assets_chains_migrations_and_enforces_guards(self) -> None:
        mig_01_02 = """
from pathlib import Path
import json

FROM_VERSION = "0.1.0"
TO_VERSION = "0.2.0"

def check(ctx):
    assert Path(ctx["manifest_path"]).is_file()
    return True

def plan(ctx):
    return ["Record 0.1.0->0.2.0 in migration_trace.json"]

def apply(ctx):
    p = Path(ctx["management_root"]) / "migration_trace.json"
    trace = json.loads(p.read_text(encoding="utf-8")) if p.is_file() else []
    if "0.1.0->0.2.0" not in trace:
        trace.append("0.1.0->0.2.0")
    p.write_text(json.dumps(trace) + "\\n", encoding="utf-8", newline="\\n")
    return [p]

def verify(ctx):
    p = Path(ctx["management_root"]) / "migration_trace.json"
    return "0.1.0->0.2.0" in json.loads(p.read_text(encoding="utf-8"))
"""
        mig_02_03 = """
from pathlib import Path
import json

FROM_VERSION = "0.2.0"
TO_VERSION = "0.3.0"

def check(ctx):
    p = Path(ctx["management_root"]) / "migration_trace.json"
    return p.is_file() and "0.1.0->0.2.0" in json.loads(p.read_text(encoding="utf-8"))

def plan(ctx):
    return ["Append 0.2.0->0.3.0 to migration_trace.json"]

def apply(ctx):
    p = Path(ctx["management_root"]) / "migration_trace.json"
    trace = json.loads(p.read_text(encoding="utf-8"))
    if "0.2.0->0.3.0" not in trace:
        trace.append("0.2.0->0.3.0")
    p.write_text(json.dumps(trace) + "\\n", encoding="utf-8", newline="\\n")
    return [p]

def verify(ctx):
    p = Path(ctx["management_root"]) / "migration_trace.json"
    return json.loads(p.read_text(encoding="utf-8")) == ["0.1.0->0.2.0", "0.2.0->0.3.0"]
"""
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            bare_remote = _create_mock_remote_bare_repo(
                base / "remote",
                [
                    ("0.1.0", 1, {}),
                    ("0.2.0", 1, {"v0.1.0_to_v0.2.0.py": mig_01_02}),
                    ("0.3.0", 2, {"v0.1.0_to_v0.2.0.py": mig_01_02, "v0.2.0_to_v0.3.0.py": mig_02_03}),
                ],
            )
            remote_url = bare_remote.as_uri()

            # Install v0.1.0 from remote into target project
            repo = init_git_repo(base / "target_proj", default_branch="develop")
            (repo / "AGENTS.md").write_text("# Project Custom Header\n\nPreserved across upgrades.\n", encoding="utf-8", newline="\n")
            git(repo, "add", ".")
            git(repo, "commit", "-m", "add custom AGENTS.md")

            self.assertEqual(
                run_cmd(
                    [sys.executable, str(INSTALLER_DIR / "install.py"), "--source", remote_url, "--ref", "v0.1.0"],
                    repo,
                ).returncode,
                0,
            )
            self.assertEqual(
                run_script(repo, "init.py", "--integration-branch", "develop", "--tools", "claude,codex").returncode,
                0,
            )

            # Populate user assets: discussion, custom skill, custom agent, worker_models, obsolete aico skill
            p_disc = run_script(repo, "create_discussion.py", "--slug", "user-note", "--title", "ユーザー議事録", "--json")
            self.assertEqual(p_disc.returncode, 0)
            disc_path = repo / parse_json_output(p_disc)["path"]
            run_script(repo, "rebuild_indexes.py")

            custom_skill = repo / ".agents" / "skills" / "custom-deploy" / "SKILL.md"
            custom_skill.parent.mkdir(parents=True)
            custom_skill.write_text("---\nname: custom-deploy\ndescription: Custom deploy\n---\n\n# custom-deploy\n", encoding="utf-8", newline="\n")

            custom_agent = repo / ".claude" / "agents" / "custom-bot.md"
            custom_agent.write_text("# Custom Bot\n", encoding="utf-8", newline="\n")

            obsolete_skill = repo / ".agents" / "skills" / "aico-obsolete" / "SKILL.md"
            obsolete_skill.parent.mkdir(parents=True)
            obsolete_skill.write_text("---\nname: aico-obsolete\ndescription: Old\n---\n\n# old\n", encoding="utf-8", newline="\n")

            m_path = repo / "management" / "aico-manifest.json"
            m = json.loads(m_path.read_text(encoding="utf-8"))
            m["worker_models"]["claude"]["high"] = {"model": "claude-opus-test", "effort": "high"}
            m_path.write_text(json.dumps(m, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
            run_script(repo, "sync_agents.py")

            git(repo, "add", ".")
            git(repo, "commit", "-m", "chore: setup v0.1.0 with user assets")

            # 1. --check compares versions without modifying files
            snap_chk = snapshot_tree(repo)
            p_chk = run_script(repo, "update.py", "--check", "--json")
            self.assertEqual(p_chk.returncode, 0, p_chk.stdout + p_chk.stderr)
            d_chk = parse_json_output(p_chk)["data"]
            self.assertEqual(d_chk["current_version"], "0.1.0")
            self.assertEqual(d_chk["target_version"], "0.3.0")
            self.assertTrue(d_chk["update_available"])
            self.assertEqual(snapshot_tree(repo), snap_chk)

            # 2. Guards: dirty tree rejected; feature branch rejected
            (repo / "dirty.tmp").write_text("dirty\n", encoding="utf-8", newline="\n")
            self.assertEqual(run_script(repo, "update.py").returncode, 1)
            (repo / "dirty.tmp").unlink()

            git(repo, "checkout", "-b", "feature/wip")
            self.assertEqual(run_script(repo, "update.py").returncode, 1)
            git(repo, "checkout", "develop")

            # 3. --dry-run makes zero changes
            snap_dry = snapshot_tree(repo)
            p_dry = run_script(repo, "update.py", "--dry-run", "--json")
            self.assertEqual(p_dry.returncode, 0, p_dry.stdout + p_dry.stderr)
            self.assertEqual(len(parse_json_output(p_dry)["data"]["migrations"]), 2)
            self.assertEqual(snapshot_tree(repo), snap_dry)

            # 4. Upgrade v0.1.0 -> v0.3.0 (multi-version chained migrations 0.1.0 -> 0.2.0 -> 0.3.0!)
            p_up = run_script(repo, "update.py", "--json")
            self.assertEqual(p_up.returncode, 0, p_up.stdout + p_up.stderr)
            up_d = parse_json_output(p_up)
            self.assertEqual(up_d["data"]["from_version"], "0.1.0")
            self.assertEqual(up_d["data"]["to_version"], "0.3.0")

            # Verify chained migration execution order
            trace = json.loads((repo / "management" / "migration_trace.json").read_text(encoding="utf-8"))
            self.assertEqual(trace, ["0.1.0->0.2.0", "0.2.0->0.3.0"])

            # Verify ALL user assets preserved & AIco-owned updated
            self.assertTrue(disc_path.is_file())
            self.assertTrue(custom_skill.is_file())
            self.assertTrue((repo / ".claude" / "skills" / "custom-deploy" / "SKILL.md").is_file())
            self.assertTrue(custom_agent.is_file())
            self.assertFalse(obsolete_skill.exists())
            agents_txt = (repo / "AGENTS.md").read_text(encoding="utf-8")
            self.assertIn("# Project Custom Header\n\nPreserved across upgrades.", agents_txt)
            self.assertIn("<!-- version:0.3.0 -->", agents_txt)

            m_after = json.loads(m_path.read_text(encoding="utf-8"))
            self.assertEqual(m_after["aico_version"], "0.3.0")
            self.assertEqual(m_after["schema_version"], 2)
            self.assertEqual(m_after["source_repository"], remote_url)
            self.assertEqual(m_after["worker_models"]["claude"]["high"]["model"], "claude-opus-test")

            git(repo, "add", ".")
            git(repo, "commit", "-m", "chore: upgraded to v0.3.0")

            # 5. Same-version re-run is idempotent (0 diffs!)
            p_same = run_script(repo, "update.py", "--json")
            self.assertEqual(p_same.returncode, 0, p_same.stdout + p_same.stderr)
            self.assertEqual(parse_json_output(p_same)["changed_files"], [])

            # 6. Downgrade (--to v0.2.0) is rejected with exit 1
            p_down = run_script(repo, "update.py", "--to", "v0.2.0")
            self.assertEqual(p_down.returncode, 1)

    def test_broken_and_failing_migrations_and_archive_source(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            src_v010 = make_source_copy(base / "src_v010", version="0.1.0", strip_git=True)
            repo = setup_installed_repo(base / "proj", integration_branch="main", source_dir=src_v010)

            # Source archive (no .git) with broken migration chain (0.1.0->0.2.0 and 0.3.0->0.4.0, missing 0.2.0->0.3.0)
            src_broken = make_source_copy(base / "src_broken", version="0.4.0", schema_version=2, strip_git=True)
            (src_broken / "installer" / "migrations" / "v0.1.0_to_v0.2.0.py").write_text(
                'FROM_VERSION="0.1.0"\nTO_VERSION="0.2.0"\ndef check(c): return True\ndef plan(c): return []\ndef apply(c): return []\ndef verify(c): return True\n',
                encoding="utf-8",
                newline="\n",
            )
            (src_broken / "installer" / "migrations" / "v0.3.0_to_v0.4.0.py").write_text(
                'FROM_VERSION="0.3.0"\nTO_VERSION="0.4.0"\ndef check(c): return True\ndef plan(c): return []\ndef apply(c): return []\ndef verify(c): return True\n',
                encoding="utf-8",
                newline="\n",
            )
            p_brk = run_script(repo, "update.py", "--source", str(src_broken), "--json")
            self.assertEqual(p_brk.returncode, 1)
            self.assertIn("途切れています", p_brk.stdout + p_brk.stderr)

            # Source archive with failing migration check() -> stops with exit 1
            src_fail = make_source_copy(base / "src_fail", version="0.2.0", schema_version=1, strip_git=True)
            (src_fail / "installer" / "migrations" / "v0.1.0_to_v0.2.0.py").write_text(
                'FROM_VERSION="0.1.0"\nTO_VERSION="0.2.0"\ndef check(c): return (False, "simulated precheck failure")\ndef plan(c): return ["step"]\ndef apply(c): return []\ndef verify(c): return True\n',
                encoding="utf-8",
                newline="\n",
            )
            p_fail = run_script(repo, "update.py", "--source", str(src_fail), "--json")
            self.assertEqual(p_fail.returncode, 1)
            self.assertIn("simulated precheck failure", p_fail.stdout + p_fail.stderr)
            git(repo, "checkout", "--", ".")

            # Emergency direct upgrade.py execution from .git-less archive (PATCH 0.1.0 -> 0.1.1, no migration needed)
            src_patch = make_source_copy(base / "src_patch", version="0.1.1", schema_version=1, strip_git=True)
            p_em = run_cmd(
                [sys.executable, str(src_patch / "installer" / "upgrade.py"), "--json"],
                repo,
            )
            self.assertEqual(p_em.returncode, 0, p_em.stdout + p_em.stderr)
            m_after = json.loads((repo / "management" / "aico-manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(m_after["aico_version"], "0.1.1")

    def test_install_with_init_flag_and_upgrade_removes_obsolete_workflow_reference(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            src = make_source_copy(base / "src_cur", version="0.1.0", strip_git=True)

            # 1. --init --dry-run --json leaves tree untouched and flags init_planned
            repo_dry = init_git_repo(base / "proj_dry", default_branch="main")
            snap = snapshot_tree(repo_dry)
            p_dry = run_cmd(
                [sys.executable, str(src / "installer" / "install.py"), "--init", "--dry-run", "--json"],
                repo_dry,
            )
            self.assertEqual(p_dry.returncode, 0, p_dry.stdout + p_dry.stderr)
            d_dry = parse_json_output(p_dry)
            self.assertTrue(d_dry["data"].get("init_planned"))
            self.assertEqual(snapshot_tree(repo_dry), snap)

            # 2. --init --json runs install + init and returns single merged JSON
            repo_json = init_git_repo(base / "proj_json", default_branch="main")
            p_json = run_cmd(
                [sys.executable, str(src / "installer" / "install.py"), "--init", "--json"],
                repo_json,
            )
            self.assertEqual(p_json.returncode, 0, p_json.stdout + p_json.stderr)
            d_json = parse_json_output(p_json)
            self.assertIn("init", d_json["data"])
            self.assertTrue((repo_json / "CLAUDE.md").is_file())
            self.assertTrue((repo_json / ".github" / "agents" / "worker-high.agent.md").is_file())

            # 3. --init text mode prints placement + next-steps tutorial guidance
            repo_txt = init_git_repo(base / "proj_txt", default_branch="main")
            p_txt = run_cmd(
                [sys.executable, str(src / "installer" / "install.py"), "--init"],
                repo_txt,
                stdin_text="",
            )
            self.assertEqual(p_txt.returncode, 0, p_txt.stdout + p_txt.stderr)
            self.assertIn("02.tutorial.md", p_txt.stdout)
            self.assertIn("05.worker-models.md", p_txt.stdout)
            self.assertIn("次のステップ:", p_txt.stdout)
            self.assertNotIn("WARN:", p_txt.stderr)

            # 4. Normal install (no --init) prints 01.getting-started.md guidance
            repo_plain = init_git_repo(base / "proj_plain", default_branch="main")
            p_plain = run_cmd(
                [sys.executable, str(src / "installer" / "install.py")],
                repo_plain,
            )
            self.assertEqual(p_plain.returncode, 0, p_plain.stdout + p_plain.stderr)
            self.assertIn("01.getting-started.md", p_plain.stdout)

            # 5. Upgrade removes obsolete 01.manual/workflow-reference.md cleanly and passes doctor
            repo_upg = setup_installed_repo(base / "proj_upg", integration_branch="main", source_dir=src)
            obsolete_ref = repo_upg / "management" / "01.manual" / "workflow-reference.md"
            obsolete_ref.write_text("# Old Workflow Reference\n", encoding="utf-8", newline="\n")
            git(repo_upg, "add", ".")
            git(repo_upg, "commit", "-m", "simulate v0.1.0 with workflow-reference.md")

            src_v2 = make_source_copy(base / "src_v2", version="0.2.0", schema_version=1, strip_git=True)
            p_upg = run_script(repo_upg, "update.py", "--source", str(src_v2), "--json")
            self.assertEqual(p_upg.returncode, 0, p_upg.stdout + p_upg.stderr)
            self.assertEqual(
                json.loads((repo_upg / "management" / "aico-manifest.json").read_text(encoding="utf-8"))["aico_version"],
                "0.2.0",
            )
            self.assertFalse(obsolete_ref.exists())
            for expected in ("index.md", "01.getting-started.md", "02.tutorial.md", "03.cheatsheet.md", "04.user-guide.md", "05.worker-models.md"):
                self.assertTrue((repo_upg / "management" / "01.manual" / expected).is_file())

            # Configure recommended 4-tool settings and verify sync_agents + doctor == 0 warn / 0 error
            m_path = repo_upg / "management" / "aico-manifest.json"
            m_data = json.loads(m_path.read_text(encoding="utf-8"))
            m_data["worker_models"] = {
                "claude": {
                    "high": {"model": "opus", "effort": "high"},
                    "middle": {"model": "sonnet", "effort": "high"},
                    "low": {"model": "haiku", "effort": "high"},
                },
                "codex": {
                    "high": {"model": "gpt-6.2-astra", "effort": "high"},
                    "middle": {"model": "gpt-6.2-sol", "effort": "medium"},
                    "low": {"model": "gpt-6.2-sol", "effort": "low"},
                },
                "antigravity": {
                    "high": {"model": "pro", "effort": ""},
                    "middle": {"model": "flash", "effort": ""},
                    "low": {"model": "flash_lite", "effort": ""},
                },
                "copilot": {
                    "high": {"model": "gemini-4-neon", "effort": "high"},
                    "middle": {"model": "claude-opus-5.5", "effort": "medium"},
                    "low": {"model": "gpt-6.2-sol", "effort": "low"},
                },
            }
            m_path.write_text(json.dumps(m_data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
            p_sync = run_script(repo_upg, "sync_agents.py", "--json")
            self.assertEqual(p_sync.returncode, 0, p_sync.stdout + p_sync.stderr)
            self.assertNotIn("effort:", (repo_upg / ".agents" / "agents" / "worker-high.md").read_text(encoding="utf-8"))
            cp_mid = (repo_upg / ".github" / "agents" / "worker-middle.agent.md").read_text(encoding="utf-8")
            self.assertIn("model: claude-opus-5.5", cp_mid)
            self.assertIn("reasoning-effort: medium", cp_mid)
            p_doc = run_script(repo_upg, "doctor.py", "--strict", "--json")
            self.assertEqual(p_doc.returncode, 0, p_doc.stdout + p_doc.stderr)


    def test_init_pr_template_placement_no_overwrite_and_upgrade_preservation(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            src_v1 = make_source_copy(base / "src_v1", version="0.1.0", strip_git=True)
            repo = setup_installed_repo(base / "prproj", integration_branch="main", source_dir=src_v1)

            # 1. init --pr-template creates file from AIco template when absent
            p_init1 = run_script(
                repo,
                "init.py",
                "--pr-template",
                ".github/pull_request_template.md",
                "--json",
            )
            self.assertEqual(p_init1.returncode, 0, p_init1.stdout + p_init1.stderr)
            d1 = parse_json_output(p_init1)
            self.assertEqual(d1["data"]["pr_template"], ".github/pull_request_template.md")
            self.assertEqual(d1["data"]["pr_template_action"], "created")
            pr_dst = repo / ".github" / "pull_request_template.md"
            self.assertTrue(pr_dst.is_file())
            self.assertEqual(
                pr_dst.read_text(encoding="utf-8"),
                (repo / "management" / "templates" / "pr-template.md").read_text(encoding="utf-8"),
            )

            # 2. Customize project PR template -> re-running init must NOT overwrite it
            custom_body = "## Custom Project PR Template\n\n* [ ] Project check\n"
            pr_dst.write_text(custom_body, encoding="utf-8", newline="\n")
            p_init2 = run_script(
                repo,
                "init.py",
                "--pr-template",
                ".github/pull_request_template.md",
                "--json",
            )
            self.assertEqual(p_init2.returncode, 0, p_init2.stdout + p_init2.stderr)
            d2 = parse_json_output(p_init2)
            self.assertEqual(d2["data"]["pr_template_action"], "kept_existing")
            self.assertEqual(pr_dst.read_text(encoding="utf-8"), custom_body)

            # 3. Upgrade preserves both manifest.pr_template and customized project PR template
            git(repo, "add", ".")
            git(repo, "commit", "-m", "chore: configure custom pr template")
            src_v2 = make_source_copy(base / "src_v2", version="0.2.0", schema_version=1, strip_git=True)
            p_upg = run_script(repo, "update.py", "--source", str(src_v2), "--json")
            self.assertEqual(p_upg.returncode, 0, p_upg.stdout + p_upg.stderr)
            m_after = json.loads((repo / "management" / "aico-manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(m_after["aico_version"], "0.2.0")
            self.assertEqual(m_after["pr_template"], ".github/pull_request_template.md")
            self.assertEqual(pr_dst.read_text(encoding="utf-8"), custom_body)

            # 4. Unsafe path and existing directory rejected WITHOUT mutating aico-manifest.json
            manifest_before_bad = (repo / "management" / "aico-manifest.json").read_text(encoding="utf-8")
            p_bad = run_script(repo, "init.py", "--pr-template", "../escape.md", "--json")
            self.assertEqual(p_bad.returncode, 1)
            self.assertEqual((repo / "management" / "aico-manifest.json").read_text(encoding="utf-8"), manifest_before_bad)

            p_dir = run_script(repo, "init.py", "--pr-template", ".github", "--json")
            self.assertEqual(p_dir.returncode, 1)
            self.assertEqual((repo / "management" / "aico-manifest.json").read_text(encoding="utf-8"), manifest_before_bad)

            # 5. Clearing pr_template to "" passes doctor cleanly
            p_clr = run_script(repo, "init.py", "--pr-template", "", "--json")
            self.assertEqual(p_clr.returncode, 0, p_clr.stdout + p_clr.stderr)
            self.assertEqual(parse_json_output(p_clr)["data"]["pr_template_action"], "unset")

    def test_init_rejects_external_symlink_pr_template(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            repo = setup_installed_repo(base / "prsymproj", integration_branch="main")
            manifest_path = repo / "management" / "aico-manifest.json"
            manifest_before = manifest_path.read_text(encoding="utf-8")

            ext_file = base / "outside-pr-template.md"
            ext_file.write_text("## Outside\n", encoding="utf-8", newline="\n")
            ext_link = repo / "ext-pr-link.md"
            create_symlink_or_skip(self, ext_link, ext_file)

            p_sym = run_script(repo, "init.py", "--pr-template", "ext-pr-link.md", "--json")
            self.assertEqual(p_sym.returncode, 1)
            sym_data = parse_json_output(p_sym)
            self.assertTrue(
                any("リポジトリ外を参照しています" in e for e in sym_data["errors"]),
                sym_data,
            )
            self.assertEqual(manifest_path.read_text(encoding="utf-8"), manifest_before)

    def test_install_and_upgrade_normalize_crlf_source_and_emit_crlf_bat(self) -> None:
        def _poison_newlines(src_root: Path) -> None:
            tpl_root = src_root / "template"
            for p in tpl_root.rglob("*"):
                if not p.is_file():
                    continue
                if p.suffix.lower() in {".md", ".py", ".json", ".sh", ".toml"}:
                    txt = p.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n")
                    p.write_bytes(txt.replace("\n", "\r\n").encode("utf-8"))
                elif p.suffix.lower() == ".bat":
                    txt = p.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n")
                    p.write_bytes(txt.encode("utf-8"))

        def _assert_deployed_newlines(repo_dir: Path) -> None:
            for check_dir in (repo_dir / "management", repo_dir / ".agents" / "skills"):
                for p in check_dir.rglob("*"):
                    if p.is_file() and p.suffix.lower() in {".md", ".py", ".json", ".sh", ".toml"}:
                        self.assertNotIn(b"\r", p.read_bytes(), f"CRLF leaked into {p}")
            self.assertNotIn(b"\r", (repo_dir / "AGENTS.md").read_bytes())
            self.assertNotIn(b"\r", (repo_dir / "tools" / "aico.sh").read_bytes())
            bat_raw = (repo_dir / "tools" / "aico.bat").read_bytes()
            self.assertIn(b"\r\n", bat_raw)
            self.assertNotIn(b"\n", bat_raw.replace(b"\r\n", b""))
            self.assertNotIn(b"\r", bat_raw.replace(b"\r\n", b""))

        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            src_v1 = make_source_copy(base / "src_v1", version="0.1.0", strip_git=True)
            src_v2 = make_source_copy(base / "src_v2", version="0.2.0", strip_git=True)
            _poison_newlines(src_v1)
            _poison_newlines(src_v2)

            repo = init_git_repo(base / "crlf_proj", default_branch="main")
            p_inst = run_cmd(
                [sys.executable, str(src_v1 / "installer" / "install.py"), "--source", str(src_v1), "--json"],
                repo,
            )
            self.assertEqual(p_inst.returncode, 0, p_inst.stdout + p_inst.stderr)
            _assert_deployed_newlines(repo)

            p_init = run_script(repo, "init.py", "--integration-branch", "main", "--tools", "claude,codex", "--json")
            self.assertEqual(p_init.returncode, 0, p_init.stdout + p_init.stderr)
            git(repo, "add", ".")
            git(repo, "commit", "-m", "chore: install from CRLF source")

            # Upgrade from CRLF v0.2.0 source normalizes all assets & passes doctor
            p_upg = run_script(repo, "update.py", "--source", str(src_v2), "--json")
            self.assertEqual(p_upg.returncode, 0, p_upg.stdout + p_upg.stderr)
            _assert_deployed_newlines(repo)
            git(repo, "add", ".")
            git(repo, "commit", "-m", "chore: upgrade from CRLF source")

            # Same-version re-run remains idempotent (0 changed files)
            p_same = run_script(repo, "update.py", "--source", str(src_v2), "--json")
            self.assertEqual(p_same.returncode, 0, p_same.stdout + p_same.stderr)
            self.assertEqual(parse_json_output(p_same)["changed_files"], [])


    def test_distribution_source_versions_are_consistent_semver(self) -> None:
        semver_re = re.compile(r"^\d+\.\d+\.\d+$")
        manifest = json.loads(
            (REPO_ROOT / "template" / "management" / "aico-manifest.json").read_text(encoding="utf-8")
        )
        manifest_ver = manifest["aico_version"]
        self.assertRegex(manifest_ver, semver_re)

        version_re = re.compile(r'^AICO_VERSION\s*=\s*"([^"]+)"', re.MULTILINE)
        for name in ("install.py", "upgrade.py"):
            src = (INSTALLER_DIR / name).read_text(encoding="utf-8")
            matches = version_re.findall(src)
            self.assertEqual(len(matches), 1, f"{name} must declare AICO_VERSION exactly once")
            self.assertRegex(matches[0], semver_re)
            self.assertEqual(
                matches[0],
                manifest_ver,
                f"installer/{name} AICO_VERSION ({matches[0]}) != template aico_version ({manifest_ver})",
            )

if __name__ == "__main__":
    unittest.main()
