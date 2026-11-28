---
id: implementation-round1-002-runbook-record-path-missing-records-dir
title: 公開境界ルール内の実施記録ディレクトリパスに records/ 階層が欠落している
status: done
created: 2026-11-28 01:50:51
updated: 2026-11-28 13:36:31
severity: minor
reviewer: independent-worker
---

# 公開境界ルール内の実施記録ディレクトリパスに records/ 階層が欠落している

## 対象

* `management/05.runbooks/review-worker-models/runbook.md`（L23）
* 参考：`management/04.tickets/20261124-155511-ticket-worker-models-review-runbook/plan.md`（L21）
* 比較基点：`8ce8f39`

## 指摘内容と根拠

* `runbook.md` L23 では実施記録の配置先を `management/05.runbooks/review-worker-models/<実施記録ID>/` と記載している。
* しかし `management/scripts/create_runbook_record.py`（L43：`rec_dir = rb_dir / "records" / rec_id`）および `_lib/validation.py`（`detect_record_kind`）の実装仕様上、正しいディレクトリ構成は `management/05.runbooks/review-worker-models/records/<実施記録ID>/` である。
* **推奨修正案**：`runbook.md` L23 を `management/05.runbooks/review-worker-models/records/<実施記録ID>/` へ修正する（必要に応じて `plan.md` L21 も整合させる）。

## 採否判断（人間選別）

* **判断**：採用（`in-progress`）
* **理由**：実物の実装パス仕様に合わせて `runbook.md` および `plan.md` の実施記録パス表記へ `records/` 階層を補完する。

## 修正内容

* `management/05.runbooks/review-worker-models/runbook.md`（`## 前提条件`）および `management/04.tickets/20261124-155511-ticket-worker-models-review-runbook/plan.md` の実施記録ディレクトリパスを `management/05.runbooks/review-worker-models/records/<実施記録ID>/` へ修正した（作業ツリー上・未コミット）。

## 独立再確認結果

* **判定**：解消（`done`）
* **確認根拠**：`runbook.md`（L23）および `plan.md`（L18）の実施記録ディレクトリパスが `management/05.runbooks/review-worker-models/records/<実施記録ID>/` へ修正され、`create_runbook_record.py`（L43）と一致しており、`records/` 欠落表記の残存がないことを確認した。
* **実行環境**：独立コンテキストの読み取り専用ワーカー（`view_file` による実物照合）。
* **未確認事項**：ワーカー側での `git diff`・`unittest`・`doctor`・文字コード機械検証（親セッション側で事前合格確認済み）。
