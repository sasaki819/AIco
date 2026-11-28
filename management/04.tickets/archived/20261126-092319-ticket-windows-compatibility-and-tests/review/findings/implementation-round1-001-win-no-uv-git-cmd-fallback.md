---
id: implementation-round1-001-win-no-uv-git-cmd-fallback
title: Windows no_uv_fallback テストで git と uv 同居時の git.cmd 実行が失敗する
status: done
created: 2026-11-27 03:04:47
updated: 2026-11-27 10:56:42
severity: major
reviewer: Independent Implementation Reviewer (subagent)
---

# Windows no_uv_fallback テストで git と uv 同居時の git.cmd 実行が失敗する

## 対象

* **対象ファイル**：`tests/test_daily_scripts.py`（L734–748 付近、関連：`template/management/scripts/_lib/git_utils.py` L23–34）
* **比較基点**：`738c7a8`（`main`）〜 `b0be0a3`

## 指摘内容と根拠

* `test_wrapper_japanese_space_path_nontty_and_no_uv_fallback` の Windows 分岐では、`git` と `uv` が同一ディレクトリに同居する環境（Scoop の `shims` や Chocolatey の `bin` 等）で `no_uv_bin / "git.cmd"` を生成し `no_uv_path` へ追加している。
* しかし `doctor.py` が呼び出す `template/management/scripts/_lib/git_utils.py` の `is_git_available()` は `shutil.which("git")`（`PATHEXT` を参照するため `git.cmd` に一致し `True` を返す）である一方、`run_git()` は `subprocess.run(["git", *args], ...)`（`shell=False`）を実行する。
* Windows の `CreateProcessW`（`shell=False`）は拡張子なしのコマンド名に対して `.exe` のみを補完検索し `.cmd` / `.bat` を実行しないため、`PATH` 上に `git.exe` がなく `git.cmd` のみが存在する状態では `run_git()` で `FileNotFoundError: [WinError 2]` が送出されてテストが失敗する。
* **推奨修正案**：`_dir_has_uv(git_dir)` が `True` の場合は `git.cmd` を生成せず、`git --exec-path` や `Path(git_exe).resolve()` 等から `uv` が同居していない実体 `git.exe` 格納ディレクトリ（`.../Git/cmd`・`.../Git/mingw64/bin` 等）を探索して `path_entries` へ追加する。特定できない環境では明示理由付きで `self.skipTest(...)` とする。

## 採否判断（人間選別）

* **判断**：採用（`in-progress`）
* **判断日**：2026-11-27
* **理由**：Scoop / Chocolatey 等の `git`・`uv` 同居環境でテストが失敗する実害を防ぐため、実体 `git.exe` ディレクトリ探索（または明示 `skipTest`）へ修正する。

## 修正内容

* **修正概要**：`tests/test_daily_scripts.py` の `test_wrapper_japanese_space_path_nontty_and_no_uv_fallback`（Windows 分岐）から `git.cmd` シム生成を削除し、`_find_git_exe_dir_without_uv()` を追加。`Path(git_exe).parent`・`resolve()`・`git --exec-path` の親階層（`cmd` / `bin` / `mingw64/bin` 等）・`PATH` 候補から `uv` 非同居の実体 `git.exe` ディレクトリを探索し、特定不可時のみ明示理由付きで `self.skipTest(...)` する方式へ変更した。
* **関連コミット**：`e35f726`
* **検証結果**：Linux（Python 3.14.4）37/37 OK、Windows 11 VM（Python 3.15.2）37/37 OK。加えて Windows 11 VM で `shims/git.cmd` + `shims/uv.exe` 同居環境を先頭 `PATH` に配置したシミュレーションで対象テスト通過を確認した。

## 独立再確認結果

* **判定**：解消（`done`）
* **確認日**：2026-11-27
* **確認根拠**：`tests/test_daily_scripts.py`（L716–784）で `git.cmd` シム生成が完全に廃止され、`_find_git_exe_dir_without_uv()`（L720–758）が `(cand / "git.exe").is_file() and not _dir_has_uv(cand)` を満たす実体 `git.exe` ディレクトリのみを採用し、特定不可時は明示理由付き `skipTest`（L776–777）となることを実物照合で確認した。
* **実行環境**：読み取り専用独立ワーカー（Linux / 実物コード照合）
* **未確認事項**：ワーカー内での動的実行（サンドボックス接続制約のため未実施。親セッションの Linux 37/37・Windows 11 VM 37/37・`shims/git.cmd` + `shims/uv.exe` 同居シミュレーション結果と矛盾なし）
