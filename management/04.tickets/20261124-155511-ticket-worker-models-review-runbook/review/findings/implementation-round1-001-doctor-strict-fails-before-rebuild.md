---
id: implementation-round1-001-doctor-strict-fails-before-rebuild
title: 手順 5・手順 6 の doctor --strict が一覧鮮度ドリフト WARN により必ず失敗する
status: done
created: 2026-11-28 01:50:51
updated: 2026-11-28 13:36:31
severity: major
reviewer: independent-worker
---

# 手順 5・手順 6 の doctor --strict が一覧鮮度ドリフト WARN により必ず失敗する

## 対象

* `management/05.runbooks/review-worker-models/runbook.md`（L66-L85, L101-L102, L113-L114）
* 比較基点：`8ce8f39`

## 指摘内容と根拠

* 手順 1（L37）で統合ブランチ（`main`）上に `create_runbook_record.py` で新規実施記録（`status: in-progress`）を作成する一方、`rebuild_indexes.py` の実行は手順 7（L93）に配置されている。
* `management/scripts/doctor.py`（カテゴリ 7）および `_lib/indexes.py`（`check_index_freshness`・`render_runbooks_list`）の実装上、統合ブランチ上で新規実施記録が追加されて `management/05.runbooks/index.md` が未更新の状態では、必ず `WARN: 一覧の鮮度ドリフト: management/05.runbooks/index.md` が発生する。
* そのため、手順 5（L67, L71）および手順 6（L82）で `tools/aico.sh doctor --strict` を実行して「診断エラー・警告 0 件を確認する」とする手順は、将来の実運用時に毎回必ず終了コード 1 で失敗する。
* あわせて `## 異常時の対応`（L113-L114）にも一覧鮮度ドリフト（`rebuild_indexes` 未実行）の確認観点が不足している。
* **推奨修正案**：
  * **案 A（推奨）**：手順 5・手順 6 では `tools/aico.sh doctor`（`--strict` なし）で `ERROR=0`（および警告が出る場合は手順 7 前の `management/05.runbooks/index.md` 鮮度ドリフトのみであること）を確認し、手順 7 の `rebuild_indexes.py` 実行後に `tools/aico.sh doctor --strict` で `ERROR=0 / WARN=0` を最終確認する構成へ改める（`## 完了条件` および `## 異常時の対応` も整合させる）。
  * **案 B**：手順 1 で `create_runbook_record.py` 直後にも `rebuild_indexes.py` を実行して `in-progress` 状態を一覧へ反映させ、手順 7 の `status: done` 更新後に再度 `rebuild_indexes.py` と `doctor --strict` を実行する。

## 採否判断（人間選別）

* **判断**：採用（`in-progress`）
* **理由**：実運用時に毎回必ず失敗する手順矛盾であるため、案 A（手順 5・6 は `doctor` で `ERROR=0` および鮮度ドリフト以外の警告なしを確認し、手順 7 の `rebuild_indexes.py` 後に `doctor --strict` で最終検証、`完了条件`・`異常時の対応` も整合）で修正する。

## 修正内容

* `management/05.runbooks/review-worker-models/runbook.md`（および `plan.md`）を案 A に従って修正した（作業ツリー上・未コミット）。
  * 手順 5・手順 6 のコマンドを `tools/aico.sh doctor` へ変更し、`ERROR=0` および手順 7 前の一覧鮮度ドリフト（`management/05.runbooks/index.md`）以外の警告がないことを確認する手順へ整理した。
  * 手順 7 の `rebuild_indexes.py` 実行後に `tools/aico.sh doctor --strict` で `ERROR=0 / WARN=0` を最終確認する構成へ統一した。
  * `## 完了条件` を手順 7 後の `doctor --strict` 確認に整合させ、`## 異常時の対応` に `doctor` / `doctor --strict` 失敗時および一覧鮮度ドリフト（`rebuild_indexes.py` 未実行）の確認観点を追記した。

## 独立再確認結果

* **判定**：解消（`done`）
* **確認根拠**：`runbook.md` の手順 5（L73-L80）・手順 6（L82-L92）・手順 7（L94-L103）・`## 完了条件`（L112）・`## 異常時の対応`（L121-L122）および `plan.md`（L33, L36）が案 A に沿って一貫修正されており、`_lib/indexes.py` の実物仕様とも整合していることを確認した。
* **実行環境**：独立コンテキストの読み取り専用ワーカー（`view_file` による実物照合）。
* **未確認事項**：ワーカー側での `git diff`・`unittest`・`doctor`・文字コード機械検証（親セッション側で事前合格確認済み）。
