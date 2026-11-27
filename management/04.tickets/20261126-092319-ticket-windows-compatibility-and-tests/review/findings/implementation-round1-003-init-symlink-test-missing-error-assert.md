---
id: implementation-round1-003-init-symlink-test-missing-error-assert
title: test_init_rejects_external_symlink_pr_template で拒否理由のアサーションが欠けている
status: done
created: 2026-11-27 03:04:47
updated: 2026-11-27 10:56:42
severity: minor
reviewer: Independent Implementation Reviewer (subagent)
---

# test_init_rejects_external_symlink_pr_template で拒否理由のアサーションが欠けている

## 対象

* **対象ファイル**：`tests/test_lifecycle.py`（L610–624 付近）
* **比較基点**：`738c7a8`（`main`）〜 `b0be0a3`

## 指摘内容と根拠

* 分離された `tests/test_daily_scripts.py` の `test_doctor_rejects_external_symlink_pr_template` では `parse_json_output()` を行い `errors` に `"リポジトリ外を参照しています"` が含まれることまで検証している。
* 一方、`tests/test_lifecycle.py` の `test_init_rejects_external_symlink_pr_template` は `init.py` へ `"--json"` を渡しているにもかかわらず、`returncode == 1` と `aico-manifest.json` の不変のみを検証しており、拒否理由が境界違反エラーであることを検証していない。無関係な原因で `returncode == 1` となっても偽陽性で通過してしまう。
* **推奨修正案**：`sym_data = parse_json_output(p_sym)` を追加し、`self.assertTrue(any("リポジトリ外を参照しています" in e for e in sym_data["errors"]))` を検証する。

## 採否判断（人間選別）

* **判断**：採用（`in-progress`）
* **判断日**：2026-11-27
* **理由**：`test_init_rejects_external_symlink_pr_template` の偽陽性を防ぎ `doctor` 側テストと検証粒度を揃えるため、JSON エラー内容のアサーションを追加する。

## 修正内容

* **修正概要**：`tests/test_lifecycle.py` の `test_init_rejects_external_symlink_pr_template` に `sym_data = parse_json_output(p_sym)` および `self.assertTrue(any("リポジトリ外を参照しています" in e for e in sym_data["errors"]), sym_data)` を追加し、`doctor` 側テストと同等に境界違反エラー理由を検証するようにした。
* **関連コミット**：`e35f726`
* **検証結果**：Linux 37/37 OK、Windows 11 VM（管理者権限）37/37 OK で当該アサーションの通過を確認した。

## 独立再確認結果

* **判定**：解消（`done`）
* **確認日**：2026-11-27
* **確認根拠**：`tests/test_lifecycle.py`（L610–629）に `parse_json_output(p_sym)` と `"リポジトリ外を参照しています"` のエラー検証が追加され、`template/management/scripts/init.py`（L229–234）および `_lib/cli.py` の実出力仕様と一致することを実物照合で確認した。
* **実行環境**：読み取り専用独立ワーカー（Linux / 実物コード照合）
* **未確認事項**：ワーカー内での動的実行（サンドボックス接続制約のため未実施。親セッションの Linux 37/37・Windows 11 VM 37/37 結果と矛盾なし）
