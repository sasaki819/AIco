"""Shared test helpers for AIco unit and E2E tests (stdlib-only)."""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import unittest
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
        if os.name == "nt":
            for k, v in env.items():
                for existing_k in [ek for ek in merged_env if ek.upper() == k.upper()]:
                    del merged_env[existing_k]
                merged_env[k] = v
        else:
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
    git(repo_dir, "config", "core.autocrlf", "false")
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
    source_dir: Path = REPO_ROOT,
    commit: bool = True,
) -> Path:
    init_git_repo(repo_dir, default_branch=integration_branch)
    res = run_cmd(
        [
            sys.executable,
            str(source_dir / "installer" / "install.py"),
            "--source",
            str(source_dir),
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


def run_wrapper(
    repo_dir: Path,
    *args: str,
    env: dict[str, str] | None = None,
    stdin_text: str | None = None,
) -> subprocess.CompletedProcess[str]:
    if os.name == "nt":
        wrapper = repo_dir / "tools" / "aico.bat"
        return run_cmd(["cmd", "/d", "/c", "call", str(wrapper), *args], repo_dir, env=env, stdin_text=stdin_text)
    wrapper = repo_dir / "tools" / "aico.sh"
    return run_cmd(["bash", str(wrapper), *args], repo_dir, env=env, stdin_text=stdin_text)


def create_symlink_or_skip(test_case: unittest.TestCase, link_path: Path, target_path: Path) -> None:
    """Create a symlink, or skip cleanly on Windows without symlink privileges (WinError 1314)."""
    try:
        link_path.symlink_to(target_path)
    except OSError as exc:
        if os.name == "nt" and getattr(exc, "winerror", None) == 1314:
            test_case.skipTest(
                "Windows 環境でシンボリックリンク作成権限が不足しています (WinError 1314)。"
                "開発者モードを有効にするか管理者権限の PowerShell で再実行してください。"
            )
        raise


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
        txt, replaced = re.subn(
            r'^AICO_VERSION\s*=\s*"[^"]+"',
            f'AICO_VERSION = "{version}"',
            txt,
            count=1,
            flags=re.MULTILINE,
        )
        if replaced != 1:
            raise AssertionError(f"AICO_VERSION assignment not found in {py_p}")
        py_p.write_text(txt, encoding="utf-8", newline="\n")

    if not strip_git:
        git(dst_dir, "init", "-b", "main")
        git(dst_dir, "config", "user.name", "AIco Release")
        git(dst_dir, "config", "user.email", "release@example.com")
        git(dst_dir, "add", ".")
        git(dst_dir, "commit", "-m", f"release: v{version}")
        git(dst_dir, "tag", f"v{version}")
    return dst_dir
