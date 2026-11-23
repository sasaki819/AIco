#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""AIco upgrade and sequential migration engine (standalone, stdlib-only).

Invoked by target project's `management/scripts/update.py` or directly as emergency fallback
from the target project's Git repository root.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile
from collections import deque
from pathlib import Path
from types import ModuleType
from typing import Any
from urllib.parse import urlparse
from urllib.request import url2pathname

AICO_VERSION = "0.1.0"
DEFAULT_SOURCE_REPO = "https://github.com/sasaki819/AIco.git"
MANAGED_BEGIN = "<!-- AICO:BEGIN -->"
MANAGED_END = "<!-- AICO:END -->"
SEMVER_RE = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")
EXIT_OK = 0
EXIT_ERROR = 1


class UpgradeError(Exception):
    pass


def _configure_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass


def _parse_semver(ver: str) -> tuple[int, int, int] | None:
    m = SEMVER_RE.match(ver.strip())
    if not m:
        return None
    return int(m.group(1)), int(m.group(2)), int(m.group(3))


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


def _find_target_manifest(repo_root: Path, mgmt_root_arg: str | None) -> Path:
    if mgmt_root_arg:
        p = (repo_root / mgmt_root_arg / "aico-manifest.json").resolve()
        if p.is_file():
            return p
        raise UpgradeError(f"aico-manifest.json が見つかりません: {p}")

    default_p = repo_root / "management" / "aico-manifest.json"
    if default_p.is_file():
        return default_p

    # Search direct or nested subdirectories (excluding template/ and .git/)
    found: list[Path] = []
    for cand in sorted(repo_root.rglob("aico-manifest.json")):
        rel_parts = cand.relative_to(repo_root).parts
        if any(p in (".git", "template", "tests") for p in rel_parts):
            continue
        found.append(cand)
    if len(found) == 1:
        return found[0]
    if len(found) > 1:
        raise UpgradeError(
            "複数の aico-manifest.json が見つかりました。--management-root を明示してください: "
            + ", ".join(_to_posix_rel(p, repo_root) for p in found)
        )
    raise UpgradeError("導入先の aico-manifest.json が見つかりません")


def _extract_managed_block(text: str) -> str:
    norm = text.replace("\r\n", "\n")
    begins = list(re.finditer(r"^[ \t]*<!-- AICO:BEGIN -->[ \t]*$", norm, flags=re.MULTILINE))
    ends = list(re.finditer(r"^[ \t]*<!-- AICO:END -->[ \t]*$", norm, flags=re.MULTILINE))
    if len(begins) != 1 or len(ends) != 1 or begins[0].start() >= ends[0].start():
        raise UpgradeError("template/AGENTS.md に AICO:BEGIN〜AICO:END ブロックがありません")
    return norm[begins[0].start() : ends[0].end()]


def _replace_managed_block(existing_text: str, new_block: str) -> str:
    norm = existing_text.replace("\r\n", "\n")
    begins = list(re.finditer(r"^[ \t]*<!-- AICO:BEGIN -->[ \t]*$", norm, flags=re.MULTILINE))
    ends = list(re.finditer(r"^[ \t]*<!-- AICO:END -->[ \t]*$", norm, flags=re.MULTILINE))
    if len(begins) != 1 or len(ends) != 1 or begins[0].start() >= ends[0].start():
        raise UpgradeError("AGENTS.md の AICO:BEGIN / AICO:END マーカーが不正または欠損しています")
    return norm[: begins[0].start()] + new_block + norm[ends[0].end() :]


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


def _cleanup_empty_dirs(paths: list[Path], stop_roots: set[Path]) -> None:
    dirs = sorted({p.parent for p in paths}, key=lambda x: len(x.parts), reverse=True)
    for d in dirs:
        cur = d
        while cur not in stop_roots and cur.exists() and cur.is_dir():
            try:
                next(cur.iterdir())
                break
            except StopIteration:
                try:
                    cur.rmdir()
                except OSError:
                    break
                cur = cur.parent


def _mirror_tree(
    src_dir: Path,
    dst_dir: Path,
    repo_root: Path,
    *,
    dry_run: bool,
    executable_top_py: bool = False,
) -> list[str]:
    changed: list[str] = []
    expected_rels: set[Path] = set()

    for src_file in sorted(src_dir.rglob("*")):
        if not src_file.is_file() or "__pycache__" in src_file.parts or src_file.suffix == ".pyc":
            continue
        rel = src_file.relative_to(src_dir)
        expected_rels.add(rel)
        dst_file = dst_dir / rel
        is_exec = executable_top_py and len(rel.parts) == 1 and src_file.suffix == ".py"
        if _write_bytes_atomic(dst_file, src_file.read_bytes(), dry_run=dry_run, executable=is_exec):
            changed.append(_to_posix_rel(dst_file, repo_root))

    deleted_paths: list[Path] = []
    if dst_dir.is_dir():
        for dst_file in sorted(dst_dir.rglob("*")):
            if not dst_file.is_file() or "__pycache__" in dst_file.parts or dst_file.suffix == ".pyc":
                continue
            rel = dst_file.relative_to(dst_dir)
            if rel not in expected_rels:
                if not dry_run:
                    dst_file.unlink()
                deleted_paths.append(dst_file)
                changed.append(_to_posix_rel(dst_file, repo_root))

    if not dry_run and deleted_paths:
        _cleanup_empty_dirs(deleted_paths, stop_roots={dst_dir.resolve(), repo_root.resolve()})

    return changed


def _load_migrations(migrations_dir: Path) -> list[tuple[str, str, str, ModuleType]]:
    """Return list of (name, from_ver, to_ver, module)."""
    loaded: list[tuple[str, str, str, ModuleType]] = []
    if not migrations_dir.is_dir():
        return loaded

    for p in sorted(migrations_dir.glob("*.py")):
        if p.name.startswith("_"):
            continue
        spec = importlib.util.spec_from_file_location(f"aico_migration_{p.stem}", str(p))
        if spec is None or spec.loader is None:
            raise UpgradeError(f"マイグレーションモジュールの読み込みに失敗しました: {p.name}")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        from_v = getattr(mod, "FROM_VERSION", None)
        to_v = getattr(mod, "TO_VERSION", None)
        if not isinstance(from_v, str) or not isinstance(to_v, str):
            raise UpgradeError(f"マイグレーション '{p.name}' に FROM_VERSION / TO_VERSION が定義されていません")
        fv_t, tv_t = _parse_semver(from_v), _parse_semver(to_v)
        if fv_t is None or tv_t is None or fv_t >= tv_t:
            raise UpgradeError(
                f"マイグレーション '{p.name}' のバージョン境界が不正です ({from_v} -> {to_v})"
            )
        for fn_name in ("check", "plan", "apply", "verify"):
            if not callable(getattr(mod, fn_name, None)):
                raise UpgradeError(f"マイグレーション '{p.name}' に必須関数 {fn_name}(ctx) がありません")
        loaded.append((p.stem, from_v, to_v, mod))
    return loaded


def _resolve_migration_chain(
    *,
    migrations_dir: Path,
    current_ver: str,
    target_ver: str,
    current_schema: int,
    target_schema: int,
) -> list[tuple[str, str, str, ModuleType]]:
    cur_t = _parse_semver(current_ver)
    tgt_t = _parse_semver(target_ver)
    assert cur_t is not None and tgt_t is not None

    if cur_t == tgt_t:
        return []

    all_migs = _load_migrations(migrations_dir)
    # Relevant migrations within [current_ver, target_ver]
    in_range = [
        m
        for m in all_migs
        if (_parse_semver(m[1]) or (0, 0, 0)) >= cur_t
        and (_parse_semver(m[2]) or (0, 0, 0)) <= tgt_t
    ]

    if not in_range:
        if target_schema != current_schema or tgt_t[0] != cur_t[0]:
            raise UpgradeError(
                f"v{current_ver} -> v{target_ver} の必須マイグレーション経路が見つかりません"
                f"（schema_version: {current_schema} -> {target_schema}）"
            )
        return []

    # Build directed graph and run BFS for exact path current_ver -> ... -> target_ver
    adj: dict[str, list[tuple[str, str, str, ModuleType]]] = {}
    for m in in_range:
        adj.setdefault(m[1], []).append(m)

    queue: deque[tuple[str, list[tuple[str, str, str, ModuleType]]]] = deque([(current_ver, [])])
    visited: set[str] = {current_ver}
    best_patch_chain: list[tuple[str, str, str, ModuleType]] | None = None

    while queue:
        ver, path = queue.popleft()
        if ver == target_ver:
            return path
        ver_t = _parse_semver(ver)
        assert ver_t is not None
        if (
            path
            and target_schema == current_schema
            and ver_t[0] == tgt_t[0]
            and ver_t[1] == tgt_t[1]
            and ver_t < tgt_t
        ):
            best_patch_chain = path
        for edge in sorted(adj.get(ver, []), key=lambda x: _parse_semver(x[2]) or (0, 0, 0)):
            nxt = edge[2]
            if nxt not in visited:
                visited.add(nxt)
                queue.append((nxt, path + [edge]))

    if best_patch_chain is not None:
        # Ensure no unexecuted migrations exist strictly after the patch chain's end
        last_t = _parse_semver(best_patch_chain[-1][2])
        assert last_t is not None
        leftover = [m for m in in_range if (_parse_semver(m[1]) or (0, 0, 0)) >= last_t]
        if not leftover:
            return best_patch_chain

    raise UpgradeError(
        f"v{current_ver} -> v{target_ver} のマイグレーション経路が途切れています。"
        f"検出されたマイグレーション: {', '.join(f'{m[1]}->{m[2]}' for m in in_range)}"
    )


def _eval_migration_hook(mig_name: str, hook_name: str, fn: Any, mctx: dict[str, Any]) -> Any:
    try:
        res = fn(mctx)
    except Exception as exc:
        raise UpgradeError(f"マイグレーション '{mig_name}' の {hook_name}() が失敗しました: {exc}") from exc

    if hook_name in ("check", "verify"):
        if res is False:
            raise UpgradeError(f"マイグレーション '{mig_name}' の {hook_name}() が False を返しました")
        if isinstance(res, tuple) and len(res) == 2 and res[0] is False:
            raise UpgradeError(f"マイグレーション '{mig_name}' の {hook_name}() が失敗しました: {res[1]}")
        if isinstance(res, list) and len(res) > 0:
            raise UpgradeError(
                f"マイグレーション '{mig_name}' の {hook_name}() でエラー検出: {'; '.join(str(x) for x in res)}"
            )
    return res


def _run_upgrade(
    *,
    repo_root: Path,
    source_root: Path,
    manifest_path: Path,
    dry_run: bool,
) -> tuple[list[str], list[str], dict[str, Any]]:
    template_dir = source_root / "template"
    if not template_dir.is_dir():
        raise UpgradeError(f"配布元に template/ が見つかりません: {source_root}")

    cur_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    tpl_manifest = json.loads((template_dir / "management" / "aico-manifest.json").read_text(encoding="utf-8"))

    current_ver = str(cur_manifest.get("aico_version", "")).strip()
    target_ver = str(tpl_manifest.get("aico_version", AICO_VERSION)).strip()
    cur_t = _parse_semver(current_ver)
    tgt_t = _parse_semver(target_ver)
    if cur_t is None:
        raise UpgradeError(f"導入先の aico_version が不正です: {current_ver!r}")
    if tgt_t is None:
        raise UpgradeError(f"配布元の aico_version が不正です: {target_ver!r}")
    if cur_t > tgt_t:
        raise UpgradeError(f"ダウングレードは禁止されています（現在: v{current_ver}, 目標: v{target_ver}）")

    # Branch guard
    integ = str(cur_manifest.get("integration_branch", "")).strip()
    br_proc = _run_git(["rev-parse", "--abbrev-ref", "HEAD"], repo_root)
    current_branch = br_proc.stdout.strip() if br_proc.returncode == 0 else ""
    if current_branch != integ:
        raise UpgradeError(
            f"アップデートは統合ブランチ '{integ}' 上でのみ実行できます（現在: '{current_branch or '不明'}'）"
        )

    mgmt_root_rel = str(cur_manifest.get("management_root", "management")).strip()
    mgmt_root = (repo_root / mgmt_root_rel).resolve()

    current_schema = int(cur_manifest.get("schema_version", 1))
    target_schema = int(tpl_manifest.get("schema_version", 1))

    # Step 1: Resolve migration path
    chain = _resolve_migration_chain(
        migrations_dir=source_root / "installer" / "migrations",
        current_ver=current_ver,
        target_ver=target_ver,
        current_schema=current_schema,
        target_schema=target_schema,
    )

    changed: list[str] = []
    warnings: list[str] = []

    # Step 2: Safely replace AIco-owned areas
    # 2a. AGENTS.md marker-only replacement
    agents_dst = repo_root / "AGENTS.md"
    if not agents_dst.is_file():
        raise UpgradeError("リポジトリルートに AGENTS.md が存在しません")
    new_block = _extract_managed_block((template_dir / "AGENTS.md").read_text(encoding="utf-8"))
    new_agents = _replace_managed_block(agents_dst.read_text(encoding="utf-8"), new_block)
    if _write_text_atomic(agents_dst, new_agents, dry_run=dry_run):
        changed.append("AGENTS.md")

    # 2b. .agents/skills/aico-* mirror (preserve non-aico custom skills)
    skills_src = template_dir / ".agents" / "skills"
    skills_dst = repo_root / ".agents" / "skills"
    template_aico_skills = sorted(
        p.name for p in skills_src.iterdir() if p.is_dir() and p.name.startswith("aico-")
    )
    for skill_name in template_aico_skills:
        changed.extend(
            _mirror_tree(
                skills_src / skill_name,
                skills_dst / skill_name,
                repo_root,
                dry_run=dry_run,
            )
        )
    if skills_dst.is_dir():
        for existing in sorted(skills_dst.iterdir()):
            if existing.is_dir() and existing.name.startswith("aico-") and existing.name not in template_aico_skills:
                obsolete_files = sorted(p for p in existing.rglob("*") if p.is_file())
                for f in obsolete_files:
                    if not dry_run:
                        f.unlink()
                    changed.append(_to_posix_rel(f, repo_root))
                if not dry_run:
                    _cleanup_empty_dirs(obsolete_files, stop_roots={skills_dst.resolve(), repo_root.resolve()})
                    if existing.exists():
                        try:
                            existing.rmdir()
                        except OSError:
                            pass

    # 2c. management/{01.manual,templates,scripts} mirror
    for subdir, exec_py in (("01.manual", False), ("templates", False), ("scripts", True)):
        changed.extend(
            _mirror_tree(
                template_dir / "management" / subdir,
                mgmt_root / subdir,
                repo_root,
                dry_run=dry_run,
                executable_top_py=exec_py,
            )
        )

    # 2d. tools/aico.{sh,bat} (re-apply custom management_root, skip write if identical)
    for wrapper_name, is_bat, is_exec in (("aico.sh", False, True), ("aico.bat", True, False)):
        src_w = template_dir / "tools" / wrapper_name
        dst_w = repo_root / "tools" / wrapper_name
        w_text = _rewrite_wrapper_root(src_w.read_text(encoding="utf-8"), mgmt_root_rel, is_bat=is_bat)
        if _write_text_atomic(dst_w, w_text, dry_run=dry_run, executable=is_exec):
            changed.append(_to_posix_rel(dst_w, repo_root))

    # Step 3: Execute sequential migrations
    migration_plans: list[dict[str, Any]] = []
    mctx: dict[str, Any] = {
        "repo_root": repo_root,
        "management_root": mgmt_root,
        "manifest_path": manifest_path,
        "source_dir": source_root,
        "current_version": current_ver,
        "target_version": target_ver,
        "dry_run": dry_run,
    }
    for mig_name, fv, tv, mod in chain:
        plan_items = _eval_migration_hook(mig_name, "plan", mod.plan, mctx)
        migration_plans.append(
            {
                "name": mig_name,
                "from": fv,
                "to": tv,
                "plan": plan_items if isinstance(plan_items, list) else [str(plan_items)],
            }
        )
        if not dry_run:
            _eval_migration_hook(mig_name, "check", mod.check, mctx)
            applied = _eval_migration_hook(mig_name, "apply", mod.apply, mctx)
            if isinstance(applied, list):
                for item in applied:
                    rel = _to_posix_rel(Path(item), repo_root) if isinstance(item, (str, Path)) else str(item)
                    if rel not in changed:
                        changed.append(rel)
            _eval_migration_hook(mig_name, "verify", mod.verify, mctx)

    # Step 4: Update manifest version (preserving project-specific settings) + sync_agents + rebuild_indexes
    updated_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    updated_manifest["aico_version"] = target_ver
    updated_manifest["schema_version"] = target_schema
    manifest_text = json.dumps(updated_manifest, ensure_ascii=False, indent=2) + "\n"
    if _write_text_atomic(manifest_path, manifest_text, dry_run=dry_run):
        rel_m = _to_posix_rel(manifest_path, repo_root)
        if rel_m not in changed:
            changed.append(rel_m)

    doctor_summary: dict[str, Any] | None = None
    if not dry_run:
        # Run latest sync_agents.py
        sync_proc = subprocess.run(
            [sys.executable, str(mgmt_root / "scripts" / "sync_agents.py"), "--json"],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        if sync_proc.returncode != 0:
            raise UpgradeError(f"ステップ4 (sync_agents.py) に失敗しました: {sync_proc.stdout}{sync_proc.stderr}")
        try:
            sp = json.loads(sync_proc.stdout)
            for cf in sp.get("changed_files", []):
                if cf not in changed:
                    changed.append(cf)
            warnings.extend(sp.get("warnings", []))
        except json.JSONDecodeError:
            pass

        # Run latest rebuild_indexes.py
        idx_proc = subprocess.run(
            [sys.executable, str(mgmt_root / "scripts" / "rebuild_indexes.py"), "--json"],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        if idx_proc.returncode != 0:
            raise UpgradeError(f"ステップ4 (rebuild_indexes.py) に失敗しました: {idx_proc.stdout}{idx_proc.stderr}")
        try:
            ip = json.loads(idx_proc.stdout)
            for cf in ip.get("changed_files", []):
                if cf not in changed:
                    changed.append(cf)
        except json.JSONDecodeError:
            pass

        # Step 5: Run latest doctor.py
        doc_proc = subprocess.run(
            [sys.executable, str(mgmt_root / "scripts" / "doctor.py"), "--json"],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        doc_payload = None
        try:
            doc_payload = json.loads(doc_proc.stdout)
        except json.JSONDecodeError:
            doc_payload = None

        if doc_proc.returncode != 0:
            doc_errs = (doc_payload or {}).get("errors", [])
            detail = "\n- ".join(doc_errs) if doc_errs else (doc_proc.stdout + doc_proc.stderr).strip()
            raise UpgradeError(f"ステップ5 (doctor.py) でエラーを検出しました:\n- {detail}")

        if doc_payload is not None:
            doctor_summary = doc_payload.get("data", {}).get("summary")
            for w in doc_payload.get("warnings", []):
                if w not in warnings:
                    warnings.append(w)

    # Deduplicate changed list preserving order
    changed = list(dict.fromkeys(changed))
    meta = {
        "from_version": current_ver,
        "to_version": target_ver,
        "migrations": migration_plans,
        "doctor": doctor_summary,
        "dry_run": dry_run,
    }
    return changed, warnings, meta


def main() -> int:
    _configure_stdio()
    parser = argparse.ArgumentParser(description="AIco のアップデートおよび段階的マイグレーションを実行する")
    parser.add_argument("--source", default=None, help="配布元のローカルディレクトリまたはリモート Git URL")
    parser.add_argument("--ref", default=f"v{AICO_VERSION}", help=f"リモート取得時のタグ（既定: v{AICO_VERSION}）")
    parser.add_argument("--management-root", default=None, help="導入先の管理ルート名（省略時は自動検出）")
    parser.add_argument("--dry-run", action="store_true", help="実ファイルを変更せず予定のみ表示")
    parser.add_argument("--json", dest="as_json", action="store_true", help="JSON 形式で出力")
    args = parser.parse_args()

    try:
        cwd = Path.cwd().resolve()
        top = _run_git(["rev-parse", "--show-toplevel"], cwd)
        if top.returncode != 0 or not top.stdout.strip():
            raise UpgradeError("カレントディレクトリが Git リポジトリではありません")
        if Path(top.stdout.strip()).resolve() != cwd:
            raise UpgradeError("カレントディレクトリが Git リポジトリルートではありません")

        st = _run_git(["status", "--porcelain"], cwd)
        if st.returncode != 0:
            raise UpgradeError(f"git status の取得に失敗しました: {st.stderr.strip()}")
        if st.stdout.strip():
            raise UpgradeError("作業ツリーに未コミット変更があるためアップデートを中止します")

        manifest_path = _find_target_manifest(cwd, args.management_root)

        local_dir: Path | None = None
        remote_url: str | None = None
        if args.source is None:
            adjacent = Path(__file__).resolve().parent.parent
            if (adjacent / "template").is_dir():
                local_dir = adjacent
            else:
                remote_url = DEFAULT_SOURCE_REPO
        else:
            local_dir = _try_local_dir(args.source)
            if local_dir is None:
                remote_url = args.source.strip()

        if local_dir is not None:
            changed, warnings, meta = _run_upgrade(
                repo_root=cwd,
                source_root=local_dir,
                manifest_path=manifest_path,
                dry_run=args.dry_run,
            )
        else:
            assert remote_url is not None
            with tempfile.TemporaryDirectory(prefix="aico-upgrade-") as tmp:
                clone_dir = Path(tmp) / "aico-src"
                proc = _run_git(
                    ["clone", "--depth", "1", "--branch", args.ref, remote_url, str(clone_dir)],
                    cwd,
                )
                if proc.returncode != 0:
                    raise UpgradeError(
                        f"配布元 ({remote_url}, ref={args.ref}) の取得に失敗しました: {proc.stderr.strip()}"
                    )
                changed, warnings, meta = _run_upgrade(
                    repo_root=cwd,
                    source_root=clone_dir,
                    manifest_path=manifest_path,
                    dry_run=args.dry_run,
                )

        if args.dry_run:
            msg = (
                f"[DRY-RUN] アップデート予定: v{meta['from_version']} -> v{meta['to_version']} "
                f"(変更予定: {len(changed)}件, マイグレーション: {len(meta['migrations'])}件)"
            )
        elif changed or meta["migrations"]:
            msg = (
                f"アップデート完了: v{meta['from_version']} -> v{meta['to_version']} "
                f"(変更: {len(changed)}件, マイグレーション: {len(meta['migrations'])}件)"
            )
        else:
            msg = f"最新状態です（変更なし）: v{meta['to_version']}"

        return _emit(
            as_json=args.as_json,
            status="warn" if warnings else "ok",
            text=msg,
            changed_files=changed,
            warnings=warnings,
            data=meta,
            exit_code=EXIT_OK,
        )

    except UpgradeError as exc:
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
