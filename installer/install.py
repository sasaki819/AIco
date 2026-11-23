#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""AIco initial asset installer (standalone, stdlib-only).

Must be executed from the target project's Git repository root.
Places AIco template assets safely without overwriting project-owned files,
then guides the user to run `tools/aico.sh init` (or `tools/aico.bat init`).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any
from urllib.parse import urlparse
from urllib.request import url2pathname

AICO_VERSION = "0.1.0"
DEFAULT_SOURCE_REPO = "https://github.com/sasaki819/AIco.git"
MANAGED_BEGIN = "<!-- AICO:BEGIN -->"
MANAGED_END = "<!-- AICO:END -->"
CLAUDE_MD_EXPECTED = "@AGENTS.md\n"
EXIT_OK = 0
EXIT_ERROR = 1
EXIT_USAGE = 2


class InstallError(Exception):
    pass


def _configure_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass


def _to_posix_rel(path: Path, base: Path) -> str:
    try:
        return path.resolve().relative_to(base.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _emit(
    *,
    as_json: bool,
    status: str,
    text: str,
    changed_files: list[str] | None = None,
    warnings: list[str] | None = None,
    errors: list[str] | None = None,
    data: dict[str, Any] | None = None,
    exit_code: int = EXIT_OK,
) -> int:
    if as_json:
        payload = {
            "status": status,
            "id": None,
            "path": None,
            "changed_files": changed_files or [],
            "warnings": warnings or [],
            "errors": errors or [],
            "data": data or {},
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        if text:
            stream = sys.stderr if status == "error" else sys.stdout
            print(text, file=stream)
    return exit_code


def _run_git(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )


def _write_bytes_atomic(path: Path, content: bytes, *, dry_run: bool, executable: bool = False) -> bool:
    if path.exists():
        try:
            if path.read_bytes() == content:
                if executable and not dry_run and os.name != "nt":
                    os.chmod(path, 0o755)
                return False
        except OSError:
            pass
    if dry_run:
        return True
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=".aico-tmp-", dir=str(path.parent))
    tmp_path = Path(tmp_name)
    try:
        with os.fdopen(fd, "wb") as fh:
            fh.write(content)
            fh.flush()
            os.fsync(fh.fileno())
        if executable and os.name != "nt":
            os.chmod(tmp_path, 0o755)
        os.replace(str(tmp_path), str(path))
    except Exception:
        try:
            tmp_path.unlink(missing_ok=True)
        except OSError:
            pass
        raise
    return True


def _write_text_atomic(path: Path, text: str, *, dry_run: bool, executable: bool = False) -> bool:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    return _write_bytes_atomic(path, normalized.encode("utf-8"), dry_run=dry_run, executable=executable)


def _validate_management_root(raw: str) -> str:
    norm = raw.strip().replace("\\", "/").strip("/")
    if not norm:
        raise InstallError("--management-root は空にできません")
    p = Path(norm)
    if p.is_absolute() or ".." in p.parts:
        raise InstallError(f"--management-root はリポジトリ内の安全な相対パスを指定してください: {raw!r}")
    return norm


def _try_local_dir(raw_source: str) -> Path | None:
    cand: Path | None = None
    if raw_source.startswith("file://"):
        parsed = urlparse(raw_source)
        path_str = url2pathname(parsed.path)
        if parsed.netloc:
            path_str = f"//{parsed.netloc}{path_str}"
        cand = Path(path_str)
    else:
        p = Path(raw_source).expanduser()
        if p.exists():
            cand = p
    if cand is not None and cand.is_dir():
        resolved = cand.resolve()
        if (resolved / "template").is_dir():
            return resolved
    return None


def _extract_managed_block(agents_template_text: str) -> str:
    norm = agents_template_text.replace("\r\n", "\n")
    begins = list(re.finditer(r"^[ \t]*<!-- AICO:BEGIN -->[ \t]*$", norm, flags=re.MULTILINE))
    ends = list(re.finditer(r"^[ \t]*<!-- AICO:END -->[ \t]*$", norm, flags=re.MULTILINE))
    if len(begins) != 1 or len(ends) != 1 or begins[0].start() >= ends[0].start():
        raise InstallError("template/AGENTS.md に AICO:BEGIN〜AICO:END ブロックがありません")
    return norm[begins[0].start() : ends[0].end()]


def _rewrite_wrapper_root(content: str, management_root: str, *, is_bat: bool) -> str:
    if management_root == "management":
        return content
    if is_bat:
        bat_root = management_root.replace("/", "\\")
        return content.replace(
            'set "AICO_DEFAULT_MANAGEMENT_ROOT=management"',
            f'set "AICO_DEFAULT_MANAGEMENT_ROOT={bat_root}"',
            1,
        )
    return content.replace(
        'AICO_DEFAULT_MANAGEMENT_ROOT="management"',
        f'AICO_DEFAULT_MANAGEMENT_ROOT="{management_root}"',
        1,
    )


def _perform_install(
    *,
    repo_root: Path,
    source_root: Path,
    management_root: str,
    recorded_source_repo: str,
    dry_run: bool,
) -> tuple[list[str], dict[str, Any]]:
    template_dir = source_root / "template"
    if not template_dir.is_dir():
        raise InstallError(f"配布元に template/ ディレクトリが見つかりません: {source_root}")

    mgmt_src = template_dir / "management"
    skills_src = template_dir / ".agents" / "skills"
    tools_src = template_dir / "tools"
    agents_src = template_dir / "AGENTS.md"

    for req in (mgmt_src, skills_src, tools_src, agents_src):
        if not req.exists():
            raise InstallError(f"配布元の必須テンプレートが欠損しています: {req}")

    # Conflict checks BEFORE any write
    mgmt_dst = repo_root / management_root
    if mgmt_dst.exists():
        raise InstallError(
            f"管理ルート '{management_root}' がすでに存在します。--management-root で別名を指定するか、既存ディレクトリを退避してください"
        )

    for wrapper_name in ("aico.sh", "aico.bat"):
        w_dst = repo_root / "tools" / wrapper_name
        if w_dst.exists():
            raise InstallError(
                f"既存ファイルと衝突しました: tools/{wrapper_name}。既存ファイルを退避してから再実行してください"
            )

    skills_dst_root = repo_root / ".agents" / "skills"
    if skills_dst_root.is_dir():
        existing_aico_skills = sorted(
            p.name for p in skills_dst_root.iterdir() if p.name.startswith("aico-")
        )
        if existing_aico_skills:
            raise InstallError(
                f".agents/skills/ に既存の aico-* スキルが存在します（{', '.join(existing_aico_skills[:5])}）。既存導入済みの場合は tools/aico.sh update を使用してください"
            )

    agents_dst = repo_root / "AGENTS.md"
    agents_exists = agents_dst.is_file()
    if agents_exists:
        existing_agents_text = agents_dst.read_text(encoding="utf-8")
        if re.search(r"^[ \t]*<!-- AICO:BEGIN -->[ \t]*$", existing_agents_text.replace("\r\n", "\n"), flags=re.MULTILINE):
            raise InstallError(
                "AGENTS.md にすでに <!-- AICO:BEGIN --> が含まれています。既存導入済みの場合は tools/aico.sh update を使用してください"
            )
    else:
        existing_agents_text = ""

    claude_dst = repo_root / "CLAUDE.md"
    if claude_dst.is_file():
        claude_text = claude_dst.read_text(encoding="utf-8").replace("\r\n", "\n")
        if claude_text != CLAUDE_MD_EXPECTED:
            raise InstallError(
                "既存の CLAUDE.md に '@AGENTS.md' 以外の独自記述が含まれています。独自内容を AGENTS.md（マーカー外）へ退避してから再実行してください"
            )

    changed: list[str] = []

    # 1. Copy template/management/ -> <repo_root>/<management_root>/
    for src_file in sorted(mgmt_src.rglob("*")):
        if not src_file.is_file() or "__pycache__" in src_file.parts or src_file.suffix == ".pyc":
            continue
        rel = src_file.relative_to(mgmt_src)
        dst_file = mgmt_dst / rel
        if rel.as_posix() == "aico-manifest.json":
            manifest_data = json.loads(src_file.read_text(encoding="utf-8"))
            manifest_data["management_root"] = management_root
            manifest_data["source_repository"] = recorded_source_repo
            content = json.dumps(manifest_data, ensure_ascii=False, indent=2) + "\n"
            if _write_text_atomic(dst_file, content, dry_run=dry_run):
                changed.append(_to_posix_rel(dst_file, repo_root))
        else:
            is_exec = rel.parts[0] == "scripts" and src_file.suffix == ".py" and len(rel.parts) == 2
            raw_bytes = src_file.read_bytes()
            if _write_bytes_atomic(dst_file, raw_bytes, dry_run=dry_run, executable=is_exec):
                changed.append(_to_posix_rel(dst_file, repo_root))

    # 2. Copy template/.agents/skills/aico-* -> <repo_root>/.agents/skills/
    for skill_dir in sorted(p for p in skills_src.iterdir() if p.is_dir() and p.name.startswith("aico-")):
        for src_file in sorted(skill_dir.rglob("*")):
            if not src_file.is_file():
                continue
            rel = src_file.relative_to(skills_src)
            dst_file = skills_dst_root / rel
            if _write_bytes_atomic(dst_file, src_file.read_bytes(), dry_run=dry_run):
                changed.append(_to_posix_rel(dst_file, repo_root))

    # 3. Copy tools/aico.sh & tools/aico.bat (with custom management_root rewrite)
    for wrapper_name, is_bat, is_exec in (
        ("aico.sh", False, True),
        ("aico.bat", True, False),
    ):
        src_w = tools_src / wrapper_name
        dst_w = repo_root / "tools" / wrapper_name
        w_text = src_w.read_text(encoding="utf-8")
        w_text = _rewrite_wrapper_root(w_text, management_root, is_bat=is_bat)
        if _write_text_atomic(dst_w, w_text, dry_run=dry_run, executable=is_exec):
            changed.append(_to_posix_rel(dst_w, repo_root))

    # 4. AGENTS.md (append managed block if exists, else create new; do NOT create CLAUDE.md)
    agents_tpl_text = agents_src.read_text(encoding="utf-8")
    if agents_exists:
        block = _extract_managed_block(agents_tpl_text)
        base = existing_agents_text.replace("\r\n", "\n").rstrip("\n")
        new_agents = (base + "\n\n" + block + "\n") if base else (block + "\n")
        agents_mode = "appended"
    else:
        new_agents = agents_tpl_text
        agents_mode = "created"

    if _write_text_atomic(agents_dst, new_agents, dry_run=dry_run):
        changed.append("AGENTS.md")

    tpl_manifest = json.loads((mgmt_src / "aico-manifest.json").read_text(encoding="utf-8"))
    meta = {
        "aico_version": tpl_manifest.get("aico_version", AICO_VERSION),
        "management_root": management_root,
        "source_repository": recorded_source_repo,
        "agents_md_mode": agents_mode,
        "dry_run": dry_run,
    }
    return changed, meta


def main() -> int:
    _configure_stdio()
    parser = argparse.ArgumentParser(
        description="AIco の初期資材を導入先プロジェクト（カレントの Git ルート）へ安全に配置する"
    )
    parser.add_argument("--source", default=None, help="配布元のローカルディレクトリまたはリモート Git URL")
    parser.add_argument("--ref", default=f"v{AICO_VERSION}", help=f"リモート取得時のタグ/ブランチ（既定: v{AICO_VERSION}）")
    parser.add_argument("--management-root", default="management", help="管理ルート名（既定: management）")
    parser.add_argument("--dry-run", action="store_true", help="実ファイルを変更せず配置予定のみ表示")
    parser.add_argument("--allow-dirty", action="store_true", help="未コミット変更がある作業ツリーでの実行を許可")
    parser.add_argument("--json", dest="as_json", action="store_true", help="JSON 形式で出力")
    args = parser.parse_args()

    try:
        cwd = Path.cwd().resolve()
        top = _run_git(["rev-parse", "--show-toplevel"], cwd)
        if top.returncode != 0 or not top.stdout.strip():
            raise InstallError("カレントディレクトリが Git リポジトリではありません。導入先プロジェクトのルートで実行してください")
        git_root = Path(top.stdout.strip()).resolve()
        if git_root != cwd:
            raise InstallError(
                f"カレントディレクトリが Git リポジトリルートではありません（ルート: {git_root}）。リポジトリルートで実行してください"
            )

        if not args.allow_dirty:
            st = _run_git(["status", "--porcelain"], cwd)
            if st.returncode != 0:
                raise InstallError(f"git status の取得に失敗しました: {st.stderr.strip()}")
            if st.stdout.strip():
                raise InstallError(
                    "作業ツリーに未コミット変更があるため停止します。コミット・退避するか --allow-dirty を指定してください"
                )

        mgmt_root = _validate_management_root(args.management_root)

        # Resolve source (Spec 08 1.2 & 2.1)
        local_dir: Path | None = None
        remote_url: str | None = None
        recorded_source_repo = ""

        if args.source is None:
            adjacent = Path(__file__).resolve().parent.parent
            if (adjacent / "template").is_dir():
                local_dir = adjacent
                recorded_source_repo = ""
            else:
                remote_url = DEFAULT_SOURCE_REPO
                recorded_source_repo = DEFAULT_SOURCE_REPO
        else:
            local_dir = _try_local_dir(args.source)
            if local_dir is not None:
                recorded_source_repo = ""
            else:
                remote_url = args.source.strip()
                recorded_source_repo = remote_url

        if local_dir is not None:
            changed, meta = _perform_install(
                repo_root=cwd,
                source_root=local_dir,
                management_root=mgmt_root,
                recorded_source_repo=recorded_source_repo,
                dry_run=args.dry_run,
            )
        else:
            assert remote_url is not None
            with tempfile.TemporaryDirectory(prefix="aico-install-") as tmp:
                clone_dir = Path(tmp) / "aico-src"
                proc = _run_git(
                    ["clone", "--depth", "1", "--branch", args.ref, remote_url, str(clone_dir)],
                    cwd,
                )
                if proc.returncode != 0:
                    raise InstallError(
                        f"配布元 ({remote_url}, ref={args.ref}) の取得に失敗しました: {proc.stderr.strip()}"
                    )
                changed, meta = _perform_install(
                    repo_root=cwd,
                    source_root=clone_dir,
                    management_root=mgmt_root,
                    recorded_source_repo=recorded_source_repo,
                    dry_run=args.dry_run,
                )

        if args.dry_run:
            msg = (
                f"[DRY-RUN] AIco v{meta['aico_version']} 配置予定: {len(changed)} ファイル "
                f"(management_root={mgmt_root}, AGENTS.md={meta['agents_md_mode']})"
            )
        else:
            msg = (
                f"AIco v{meta['aico_version']} の資材配置が完了しました（{len(changed)} ファイル）。\n"
                f"次のステップ: 初期設定を実行してください。\n"
                f"  Linux/macOS: tools/aico.sh init\n"
                f"  Windows    : tools\\aico.bat init"
            )
        return _emit(
            as_json=args.as_json,
            status="ok",
            text=msg,
            changed_files=changed,
            data=meta,
            exit_code=EXIT_OK,
        )

    except InstallError as exc:
        return _emit(
            as_json=args.as_json,
            status="error",
            text=f"ERROR: {exc}",
            errors=[str(exc)],
            exit_code=EXIT_ERROR,
        )
    except Exception as exc:
        return _emit(
            as_json=args.as_json,
            status="error",
            text=f"ERROR: 想定外のエラーが発生しました: {exc}",
            errors=[str(exc)],
            exit_code=EXIT_ERROR,
        )


if __name__ == "__main__":
    sys.exit(main())
