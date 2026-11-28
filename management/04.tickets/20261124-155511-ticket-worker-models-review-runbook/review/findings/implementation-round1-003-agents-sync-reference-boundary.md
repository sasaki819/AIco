---
id: implementation-round1-003-agents-sync-reference-boundary
title: 配布ガイド照合用の agents_sync.py 参照先が運営領域側と template/ 原本側で混在している
status: done
created: 2026-11-28 01:50:51
updated: 2026-11-28 13:36:31
severity: minor
reviewer: independent-worker
---

# 配布ガイド照合用の agents_sync.py 参照先が運営領域側と template/ 原本側で混在している

## 対象

* `management/05.runbooks/review-worker-models/runbook.md`（L30, L38, L64）
* 参考：`management/04.tickets/20261124-155511-ticket-worker-models-review-runbook/plan.md`（L25）
* 比較基点：`8ce8f39`

## 指摘内容と根拠

* `AGENTS.md`（配布原本と運営領域の分離）および `docs/03.spec/08.adoption-and-migration.md`（1.1・1.3 節）では、配布物の原本は `template/` 配下であり、ルート直下の `management/` はリリース前の自己適用（`tools/aico.sh update --source .`）まで前版を保持する運営領域と定義されている。
* `runbook.md` は手順 2（L50）と `## 異常時の対応`（L109）で `template/management/scripts/_lib/agents_sync.py` を指している一方、`## 入力`（L30）と手順 1（L38）では運営領域側の `[management/scripts/_lib/agents_sync.py](../../scripts/_lib/agents_sync.py)` を参照している。リリース前の開発途中に `template/` 側のアダプタ仕様が先行変更された場合、配布ガイドとの照合元を取り違える恐れがある。
* また L64 の「自己適用（`upgrade.py`）」も、`AGENTS.md` および仕様書の公式表記に合わせて `tools/aico.sh update --source .`（内部で `upgrade.py` へ委譲）と記載する方が正確である。
* **推奨修正案**：`## 入力`（L30）および手順 1（L38）の参照先を配布原本の `[template/management/scripts/_lib/agents_sync.py](../../../template/management/scripts/_lib/agents_sync.py)`（必要に応じ `EFFORT_SUPPORTED_TOOLS` を定義する `template/management/scripts/_lib/manifest.py` も補足）へ統一し、L64 の自己適用表記を `tools/aico.sh update --source .` 基準へ揃える。

## 採否判断（人間選別）

* **判断**：採用（`in-progress`）
* **理由**：配布原本（`template/`）と運営領域（ルート `management/`）の境界規約に合わせ、参照先を `template/management/scripts/_lib/agents_sync.py`（および `manifest.py` 補足）へ統一し、自己適用表記も `tools/aico.sh update --source .` 基準へ揃える。

## 修正内容

* `management/05.runbooks/review-worker-models/runbook.md`（`## 入力`・手順 1・手順 4）および `plan.md` を修正した（作業ツリー上・未コミット）。
  * ワーカー同期実装の参照先を配布原本の `template/management/scripts/_lib/agents_sync.py` へ統一し、`EFFORT_SUPPORTED_TOOLS` 定義元の `template/management/scripts/_lib/manifest.py` を補足リンクとして追加した。
  * 手順 4 の自己適用表記を「リリース時の自己適用（`tools/aico.sh update --source .`、内部で `upgrade.py` へ委譲）」へ正確化した。

## 独立再確認結果

* **判定**：解消（`done`）
* **確認根拠**：`runbook.md` の `## 入力`（L30）・手順 1（L41）・手順 2（L54）・`## 異常時の対応`（L117）で配布原本 `template/management/scripts/_lib/agents_sync.py` および `manifest.py` へ統一され、相対リンク実在と手順 4（L71）の `tools/aico.sh update --source .` 表記、ならびに `plan.md`（L21, L29）との整合を確認した。
* **実行環境**：独立コンテキストの読み取り専用ワーカー（`view_file` による実物照合）。
* **未確認事項**：ワーカー側での `git diff`・`unittest`・`doctor`・文字コード機械検証（親セッション側で事前合格確認済み）。
