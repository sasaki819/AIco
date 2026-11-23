"""Shared test helpers for AIco unit and E2E tests (stdlib-only)."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = REPO_ROOT / "template"
INSTALLER_DIR = REPO_ROOT / "installer"
SCRIPTS_LIB_ROOT = TEMPLATE_DIR / "management" / "scripts"


def run_cmd(
    args: list[str],
    cwd: Path,
    *,
    env: dict[str, str] | None = None,
    stdin_text: str | None = None,
) -> subprocess.CompletedProcess[str]:
    merged_env = os.environ.copy()
    merged_env["PYTHONUTF8"] = "1"
    merged_env["PYTHONIOENCODING"] = "utf-8"
    if env is not None:
        merged_env.update(env)
    return subprocess.run(
        args,
        cwd=str(cwd),
        input=stdin_text,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=merged_env,
        check=False,
    )


def git(cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
    proc = run_cmd(["git", *args], cwd)
    if proc.returncode != 0:
        raise AssertionError(f"git {' '.join(args)} failed ({proc.returncode}):\n{proc.stdout}\n{proc.stderr}")
    return proc


def init_git_repo(repo_dir: Path, *, default_branch: str = "develop") -> Path:
    repo_dir.mkdir(parents=True, exist_ok=True)
    git(repo_dir, "init", "-b", default_branch)
    git(repo_dir, "config", "user.name", "AIco Test")
    git(repo_dir, "config", "user.email", "aico-test@example.com")
    (repo_dir / "README.md").write_text("# Sample Repo\n", encoding="utf-8", newline="\n")
    git(repo_dir, "add", ".")
    git(repo_dir, "commit", "-m", "chore: initial commit")
    return repo_dir


def setup_installed_repo(
    repo_dir: Path,
    *,
    integration_branch: str = "develop",
    tools: str = "claude,codex,antigravity,copilot",
    management_root: str = "management",
    commit: bool = True,
) -> Path:
    init_git_repo(repo_dir, default_branch=integration_branch)
    res = run_cmd(
        [
            sys.executable,
            str(INSTALLER_DIR / "install.py"),
            "--source",
            str(REPO_ROOT),
            "--management-root",
            management_root,
        ],
        repo_dir,
    )
    if res.returncode != 0:
        raise AssertionError(f"install.py failed:\n{res.stdout}\n{res.stderr}")
    res2 = run_cmd(
        [
            sys.executable,
            str(repo_dir / management_root / "scripts" / "init.py"),
            "--integration-branch",
            integration_branch,
            "--tools",
            tools,
        ],
        repo_dir,
    )
    if res2.returncode != 0:
        raise AssertionError(f"init.py failed:\n{res2.stdout}\n{res2.stderr}")
    if commit:
        git(repo_dir, "add", ".")
        git(repo_dir, "commit", "-m", "chore: install and init AIco")
    return repo_dir


def run_script(
    repo_dir: Path,
    script_name: str,
    *args: str,
    management_root: str = "management",
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    script_path = repo_dir / management_root / "scripts" / script_name
    return run_cmd([sys.executable, str(script_path), *args], repo_dir, env=env)


def parse_json_output(proc: subprocess.CompletedProcess[str]) -> dict[str, Any]:
    try:
        data = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise AssertionError(
            f"Expected JSON stdout (rc={proc.returncode}):\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
        ) from exc
    for key in ("status", "id", "path", "changed_files", "warnings", "errors", "data"):
        if key not in data:
            raise AssertionError(f"Missing common JSON schema key {key!r} in {data!r}")
    return data


def snapshot_tree(root: Path) -> dict[str, tuple[str, int]]:
    """Return {posix_rel_path: (sha256_hex, mtime_ns)} ignoring .git and __pycache__."""
    snap: dict[str, tuple[str, int]] = {}
    for p in sorted(root.rglob("*")):
        if not p.is_file():
            continue
        rel = p.relative_to(root)
        if ".git" in rel.parts or "__pycache__" in rel.parts or p.suffix == ".pyc":
            continue
        digest = hashlib.sha256(p.read_bytes()).hexdigest()
        snap[rel.as_posix()] = (digest, p.stat().st_mtime_ns)
    return snap


def make_source_copy(dst_dir: Path, *, version: str, schema_version: int = 1, strip_git: bool = True) -> Path:
    """Create a standalone copy of template/ and installer/ with customized version."""
    dst_dir.mkdir(parents=True, exist_ok=True)
    shutil.copytree(
        TEMPLATE_DIR,
        dst_dir / "template",
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
    )
    shutil.copytree(
        INSTALLER_DIR,
        dst_dir / "installer",
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
    )
    m_path = dst_dir / "template" / "management" / "aico-manifest.json"
    m_data = json.loads(m_path.read_text(encoding="utf-8"))
    m_data["aico_version"] = version
    m_data["schema_version"] = schema_version
    m_path.write_text(json.dumps(m_data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")

    for py_name in ("install.py", "upgrade.py"):
        py_p = dst_dir / "installer" / py_name
        txt = py_p.read_text(encoding="utf-8")
        txt = txt.replace('AICO_VERSION = "0.1.0"', f'AICO_VERSION = "{version}"')
        py_p.write_text(txt, encoding="utf-8", newline="\n")

    if not strip_git:
        git(dst_dir, "init", "-b", "main")
        git(dst_dir, "config", "user.name", "AIco Release")
        git(dst_dir, "config", "user.email", "release@example.com")
        git(dst_dir, "add", ".")
        git(dst_dir, "commit", "-m", f"release: v{version}")
        git(dst_dir, "tag", f"v{version}")
    return dst_dir
