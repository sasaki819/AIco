---
id: implementation-round1-001-init-pr-template-validation-order-and-dir-check
title: init.py の pr_template 検証順序不備および既存ディレクトリ指定時の誤判定
status: done
created: 2026-11-25 10:03:21
updated: 2026-11-25 20:37:04
severity: major
reviewer: worker-middle
---

# init.py の pr_template 検証順序不備および既存ディレクトリ指定時の誤判定

## 対象

* `template/management/scripts/init.py`（L199-L221）
* 比較基点：`d3a54b4`

## 指摘内容と根拠

1. **検証前の部分的書き込み**：`save_manifest(ctx.manifest_path, new_manifest, dry_run=args.dry_run)`（L203-L204）が、`pr_dst` のリポジトリ境界チェック（L208-L211：`pr_dst.relative_to(ctx.repo_root.resolve())`）および雛形ファイル存在チェック（L216-L217：`pr_src.is_file()`）の前に実行されている。シンボリックリンク経由でリポジトリ外を指すパスや雛形欠損時に `AicoError` で中断しても、`aico-manifest.json` だけが書き換わった半端な状態が残る。
2. **既存ディレクトリの誤許容**：L212 で `if pr_dst.exists():` を用いているため、既存ディレクトリ（例：`--pr-template .github`）を指定しても `pr_template_action = "kept_existing"` として通過し、直後の `doctor.py` では `.is_file()` が `False` となり実態と食い違う `WARN` が発生する。

**推奨修正案**：
* `save_manifest` の前に、`pr_tpl_rel` 非空時のリポジトリ境界検証・既存パスが通常ファイル以外（ディレクトリ等）の拒否（`pr_dst.exists() and not pr_dst.is_file()`）・新規配置時の `pr_src.is_file()` 検証をすべて完了させる。
* 既存ディレクトリ指定時に `AicoError` となり `aico-manifest.json` が未変更のままであることを `tests/test_lifecycle.py` に追加検証する。

## 採否判断（人間選別）

採用（in-progress）：2026-11-25 人間トリアージにより全 4 件採用確定。エッジケース防御・仕様とスキルの整合性・CI ガイドの正確性を確保するため修正を実施する。

## 修正内容

* `template/management/scripts/init.py` において、`save_manifest` 実行前に `pr_template` のリポジトリ境界検査（`.resolve().relative_to(ctx.repo_root.resolve())`）、既存パスが通常ファイル以外（ディレクトリ等）である場合の拒否（`pr_dst.exists() and not pr_dst.is_file()`）、および新規配置時の雛形ファイル存在確認（`pr_src.is_file()`）をすべて完了させるよう順序を修正した。
* `tests/test_lifecycle.py`（`test_init_pr_template_placement_no_overwrite_and_upgrade_preservation`）へ、既存ディレクトリ（`.github`）・リポジトリ外シンボリックリンク・`..` 指定時に終了コード `1` となり、かつ `aico-manifest.json` が未変更のまま保たれる回帰テストを追加し、`python3 -m unittest discover -s tests -v`（33/33 OK）を確認した。
* 関連コミット：未コミット（作業ツリー上）

## 独立再確認結果

* **判定**：解消（`done`）
* **確認根拠**：`template/management/scripts/init.py`（L222-L252）にて `save_manifest` 実行前に境界検査・通常ファイル判定（ディレクトリ等拒否）・雛形存在確認がすべて完了しており、`--dry-run` 伝播も含め副作用がないことを確認。`tests/test_lifecycle.py`（L577-L595）で `../escape.md`・`.github`・外部シンボリックリンクの 3 ケースすべてで終了コード `1` と `aico-manifest.json` 未変更が検証されていることを確認。
* **実行環境**：Linux / 読み取り専用独立ワーカー（親セッションにて `unittest` 33/33 OK・`doctor.py` OK=9/WARN=0/ERROR=0 確認済み）
* **未確認事項**：Windows 実機でのシンボリックリンク・パス解決挙動
