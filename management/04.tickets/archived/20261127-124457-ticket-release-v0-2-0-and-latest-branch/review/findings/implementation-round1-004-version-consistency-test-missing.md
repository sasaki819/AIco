---
id: implementation-round1-004-version-consistency-test-missing
title: 配布原本 3 箇所のバージョン一致を自動検証するテストの不足
status: done
created: 2026-11-27 14:52:59
updated: 2026-11-27 18:57:01
severity: minor
reviewer: worker-middle（独立レビューワーカー）
---

# 配布原本 3 箇所のバージョン一致を自動検証するテストの不足

## 対象

* `tests/test_lifecycle.py`（または `tests/test_user_guide.py`）
* 比較基点：`715c9de`

## 指摘内容と根拠

* `template/management/aico-manifest.json`（`aico_version`）、`installer/install.py`（`AICO_VERSION`）、`installer/upgrade.py`（`AICO_VERSION`）の 3 箇所はいずれも現在 `0.2.0` で一致している。
* しかし既存 37 テストでは、`make_source_copy()` は 3 箇所すべてを指定版へ上書きしてテストし、`REPO_ROOT` を直接参照するテストもローカル `--source` 指定のため、`install.py` / `upgrade.py` の `--ref v{AICO_VERSION}` と `aico-manifest.json` の一致を検証していない。将来の版上げ（`v0.2.1` / `v0.3.0` 等）で 3 箇所のうちいずれかの更新が漏れても自動テストで検知できない状態である。
* **推奨修正案**：`tests/test_lifecycle.py`（または `tests/test_user_guide.py`）に、`REPO_ROOT` 配下の `template/management/aico-manifest.json` の `aico_version`、`installer/install.py` の `AICO_VERSION`、`installer/upgrade.py` の `AICO_VERSION` がいずれも有効な SemVer であり相互に一致することを検証する単体テストを 1 件追加する。

## 採否判断（人間選別）

* **判断**：採用（`in-progress`）
* **理由**：将来のリリース作業における配布原本 3 箇所のバージョン更新漏れを自動テストで確実に防止するため、単体テストを追加する。

## 修正内容

* `tests/test_lifecycle.py` に `import re` および `TestUpdateUpgradeAndMigrations.test_distribution_source_versions_are_consistent_semver` を追加し、`template/management/aico-manifest.json` の `aico_version` と `installer/install.py`・`installer/upgrade.py` の `AICO_VERSION` がいずれも厳密な `X.Y.Z` 形式の SemVer かつ単一定義であり、3 箇所すべてが一致することを自動検証するようにした。
* 検証結果：
  * Linux（Python 3.14.4 / `uv` 0.13.8）：`uv run -m unittest discover -s tests -v` **38/38 OK**（14.550s）、`uv run management/scripts/doctor.py --json` **`OK=9 / WARN=0 / ERROR=0`**
  * Windows 11 VM（`ssh win11` / Python 3.15.2 / `uv` 0.13.10）：管理者権限 **38/38 OK**（98.292s）、`gsudo -i Medium` 一般権限（`IsAdmin=False`・開発者モード OFF）**36 ok / 2 skipped**（107.110s）
* 関連コミット：未コミット（独立再確認完了後にまとめてコミット予定）

## 独立再確認結果

* **判定**：解消（`done`）
* **確認根拠**：`tests/test_lifecycle.py`（L6・L697-714）および配布原本 3 箇所（`template/management/aico-manifest.json` L3、`installer/install.py` L25、`installer/upgrade.py` L25）を実物照合し、厳密な SemVer 検証・`AICO_VERSION` 単一定義検証・3 箇所相互一致検証がいずれも 1 箇所の不一致・不正値・欠落・重複定義で確実に失敗する実装であることを確認した。
* **実行環境**：独立コンテキストの読み取り専用ワーカー（`view_file` による実物ファイル照合・比較基点 `715c9de`）
* **未確認事項**：ワーカー側での動的コマンド実行（親セッションで Linux 38/38 OK・Win11 管理者 38/38 OK・一般権限 36 ok / 2 skipped 確認済み）、段階 3〜4 の本番実行（後続工程で実施予定）
