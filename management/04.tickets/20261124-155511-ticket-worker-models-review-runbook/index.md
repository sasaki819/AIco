---
id: 20261124-155511-ticket-worker-models-review-runbook
title: worker_models おすすめ設定見直し用 Runbook の作成
status: open
created: 2026-11-24 15:55:11
updated: 2026-11-24 15:55:11
phase: drafting
phase_status: working
branch: feature/20261124-155511-ticket-worker-models-review-runbook
parent: null
children: []
discussions: [20261124-140309-discussion-onboarding-improvement]
adrs: []
---

# worker_models おすすめ設定見直し用 Runbook の作成

## 概要

`docs/04.user-guide/worker-models.md`（および配布コピー `template/management/01.manual/worker-models.md`）に掲載する 4 ツール別おすすめ `worker_models` 設定例が陳腐化しないよう、AIco 本体の定常作業として定期見直し手順書（Runbook）を `management/05.runbooks/` に新設する。

## AC（受け入れ条件）

* [ ] `management/05.runbooks/review-worker-models/runbook.md` が `aico-create-runbook` 規約および `aico-markdown-write` 規約に従って作成されていること。
* [ ] Runbook の手順に、対象 4 ツール（Claude Code・Codex・Antigravity・GitHub Copilot）の最新モデル・`effort` 仕様の確認、`docs/04.user-guide/worker-models.md` および `template/management/01.manual/worker-models.md` の更新・最終確認日反映、自動テストおよび `doctor` 検証、必要に応じた AIco 本体 `management/aico-manifest.json` 反映確認が含まれていること。
* [ ] 公開リポジトリ・GitHub ミラーの境界を守るルール（手元のベンチマーク比較資料は内部判断の参考にとどめ、非公開 URL および再配布不可のベンチマーク生数値は Runbook 本文・実施記録・公開ドキュメントへ記載しないこと）が明記されていること。
* [ ] `management/05.runbooks/index.md` および `management/index.md` が再生成され、`doctor.py` でエラー 0 件であること。

## DoR（着手合意）

* **任せる範囲**：`aico-create-runbook` に従った Runbook 手順書の作成、公開境界ルールの組み込み、一覧再生成および診断確認。
* **未決事項**：前提となる `docs/04.user-guide/worker-models.md` を整備する先行チケット（`20261124-155511-ticket-onboarding-docs-and-cli-ux`）完了後に着手する。
* **着手合意**：未合意

## 現在地

* **状況**：起票完了（先行チケット完了待ち）
* **ブロッカー（確認待ち）**：なし
* **次に取る行動**：先行チケット完了後、DoR を確認し `aico-ticket-start` または `aico-create-runbook` へ進む

## 変更ファイル

<!-- AICO:AUTO:BEGIN:changed-files -->
変更されたプロジェクト資産はない。
<!-- AICO:AUTO:END:changed-files -->

## DoD（完了の定義）

* **AC 検証結果と根拠**：
* **未検証項目と人の判断結果**：なし
* **関連記録・ADR への導線確認**：未確認

## 親子チケット・関連

* [議事録：初見ユーザー向けの導入・利用ハードル低減の整備](../../02.discussions/20261124-140309-discussion-onboarding-improvement.md)
* [先行チケット：初見ユーザー向けガイド整備と導入・初期設定ツール UX 改善](../20261124-155511-ticket-onboarding-docs-and-cli-ux/index.md)
