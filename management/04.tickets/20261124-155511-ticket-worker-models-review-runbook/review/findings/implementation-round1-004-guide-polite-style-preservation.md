---
id: implementation-round1-004-guide-polite-style-preservation
title: 手順 4 でユーザーガイドの既存文体（敬体）維持が明記されておらず常体規約と衝突し得る
status: done
created: 2026-11-28 01:50:51
updated: 2026-11-28 13:36:31
severity: minor
reviewer: independent-worker
---

# 手順 4 でユーザーガイドの既存文体（敬体）維持が明記されておらず常体規約と衝突し得る

## 対象

* `management/05.runbooks/review-worker-models/runbook.md`（L62）
* 比較基点：`8ce8f39`

## 指摘内容と根拠

* 手順 4（L62）では `docs/04.user-guide/05.worker-models.md` 編集時に `aico-markdown-write` の品質条件を満たすよう指示している。
* 一方、`aico-markdown-write/SKILL.md` は管理記録・仕様・ポリシー向けに「常体（だ・である調）で統一し、同一文書内で敬体と混在させない」と定めているのに対し、実際の `docs/04.user-guide/05.worker-models.md`（およびユーザーガイド一式）は初学者向け文書として**敬体（です・ます調）**で記述されている。
* 文体維持の注記がないと、将来 AI エージェントが本 Runbook を実施する際に常体を混在させる、または文書全体を常体へ書き換えてしまうリスクがある。
* **推奨修正案**：手順 4（L62）に「ユーザーガイドの文体は既存の敬体（です・ます調）を維持し、常体と混在させない」旨を明記する。

## 採否判断（人間選別）

* **判断**：採用（`in-progress`）
* **理由**：将来の Runbook 実施時にユーザーガイドの文体が常体へ書き換わったり混在したりするのを防ぐため、手順 4 に既存敬体維持の注記を明記する。

## 修正内容

* `management/05.runbooks/review-worker-models/runbook.md` の手順 4（および `plan.md`）へ、「ユーザーガイドの文体は既存の**敬体（です・ます調）**を維持し、常体と混在させない」旨と、`aico-markdown-write` は文体以外の共通品質規約を適用する旨を明記した（作業ツリー上・未コミット）。

## 独立再確認結果

* **判定**：解消（`done`）
* **確認根拠**：`runbook.md` 手順 4（L68-L69）および `plan.md`（L28）に既存の敬体維持・常体混在禁止および `aico-markdown-write` 適用範囲の注記が明記され、文体規約の衝突が解消していることを確認した。
* **実行環境**：独立コンテキストの読み取り専用ワーカー（`view_file` による実物照合）。
* **未確認事項**：ワーカー側での `git diff`・`unittest`・`doctor`・文字コード機械検証（親セッション側で事前合格確認済み）。
