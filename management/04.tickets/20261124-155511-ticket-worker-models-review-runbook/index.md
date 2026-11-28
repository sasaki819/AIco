---
id: 20261124-155511-ticket-worker-models-review-runbook
title: worker_models おすすめ設定見直し用 Runbook の作成
status: done
created: 2026-11-24 15:55:11
updated: 2026-11-28 13:55:58
phase: closing
phase_status: done
branch: feature/20261124-155511-ticket-worker-models-review-runbook
parent: null
children: []
discussions:
  - 20261124-140309-discussion-onboarding-improvement
adrs: []
---

# worker_models おすすめ設定見直し用 Runbook の作成

## 概要

`docs/04.user-guide/05.worker-models.md`（および配布コピー `template/management/01.manual/05.worker-models.md`）に掲載する 4 ツール別おすすめ `worker_models` 設定例が陳腐化しないよう、AIco 本体の定常作業として定期見直し手順書（Runbook）を `management/05.runbooks/` に新設する。

## AC（受け入れ条件）

* [x] `management/05.runbooks/review-worker-models/runbook.md` が `aico-create-runbook` 規約および `aico-markdown-write` 規約に従って作成されていること。
* [x] Runbook の手順に、対象 4 ツール（Claude Code・Codex・Antigravity・GitHub Copilot）の最新モデル・`effort` 仕様の確認、`docs/04.user-guide/05.worker-models.md` および `template/management/01.manual/05.worker-models.md` の更新・最終確認日反映、自動テストおよび `doctor` 検証、必要に応じた AIco 本体 `management/aico-manifest.json` 反映確認が含まれていること。
* [x] 公開リポジトリ・GitHub ミラーの境界を守るルール（手元のベンチマーク比較資料は内部判断の参考にとどめ、非公開 URL および再配布不可のベンチマーク生数値は Runbook 本文・実施記録・公開ドキュメントへ記載しないこと）が明記されていること。
* [x] `management/05.runbooks/index.md` および `management/index.md` が再生成され、`doctor.py` でエラー 0 件であること。

## DoR（着手合意）

* **任せる範囲**：`aico-create-runbook` に従った Runbook 手順書（`management/05.runbooks/review-worker-models/runbook.md`）の作成（作業ブランチ上では `--allow-non-integration` を使用）、公開境界ルールの組み込み、独立レビュー・診断確認、および `main` 統合後の一覧再生成（`management/05.runbooks/index.md`・`management/index.md`）。本チケットでは Runbook の実実施（`05.worker-models.md` や `management/aico-manifest.json` の実モデル値更新）は対象外とする。
* **未決事項**：なし（先行チケット `20261124-155511-ticket-onboarding-docs-and-cli-ux` は完了済み、実際のファイル名 `05.worker-models.md` へ対象パスを整合済み）。
* **着手合意**：合意済み（2026-11-28）

## 現在地

* **状況**：完了（人間の完了承認を得て `status: done / closing / done` を確定済み）
* **ブロッカー（確認待ち）**：なし
* **次に取る行動**：`main` 統合後、`rebuild_indexes.py` による一覧再生成および `doctor.py --strict` の最終確認を実施する

## 変更ファイル

<!-- AICO:AUTO:BEGIN:changed-files -->

変更されたプロジェクト資産はない。

<!-- AICO:AUTO:END:changed-files -->

## DoD（完了の定義）

* **AC 検証結果と根拠**：
  * **AC1（達成）**：`management/05.runbooks/review-worker-models/runbook.md` を `create_runbook.py` で生成し、`aico-create-runbook`・`aico-markdown-write` 規約（`status` 非保持・必須 7 セクション完備・H1 単一・見出しレベル飛びなし・常体統一・コードブロック言語指定・UTF-8 BOM なし・LF・禁止語 0 件・相対リンク 17 件すべて実在）への適合を自動チェックおよび独立レビュー／再確認（全 5 件 `done`・新規指摘 0 件）で実物確認済み。
  * **AC2（達成）**：`runbook.md` の手順 1〜7 に、対象 4 ツール（Claude Code・Codex・Antigravity・GitHub Copilot）の最新モデル・`effort` 仕様確認（`template/management/scripts/_lib/agents_sync.py`・`manifest.py` 原本準拠）、`docs/04.user-guide/05.worker-models.md` および `template/management/01.manual/05.worker-models.md` の同期更新・最終確認日反映・既存敬体維持、`uv run -m unittest discover -s tests -v`（38/38 OK）および `tools/aico.sh doctor` / `doctor --strict` 検証、必要に応じた `management/aico-manifest.json` 反映＋`sync_agents` 確認を網羅済み。
  * **AC3（達成）**：`runbook.md` の `前提条件`・`入力`・手順 7・`完了条件`・`異常時の対応` に公開リポジトリ・GitHub ミラーの境界ルール（手元のベンチマーク比較資料は内部判断の参考にとどめ、非公開 URL および再配布不可のベンチマーク生数値は Runbook 本文・実施記録 `records/<実施記録ID>/`・公開ドキュメントへ一切記載・添付しないこと）を明記し、本チケット変更ファイル自体にも混入がないことを確認済み。
  * **AC4（達成・統合直後に一覧再生成で最終検証）**：作業ブランチ時点の `uv run management/scripts/doctor.py --json`（`OK=9 / WARN=0 / ERROR=0`）および `uv run -m unittest discover -s tests -v`（38/38 OK）を確認済み。`main` マージ直後の統合ブランチ側 `aico-ticket-close`（`rebuild_indexes.py` 実行）にて `management/05.runbooks/index.md`・`management/index.md` を再生成し、`doctor.py --strict`（`OK=9 / WARN=0 / ERROR=0`）で最終検証する前提で人間承認済み。
* **未検証項目と人の判断結果**：
  * `main` 統合後の `rebuild_indexes.py` による `management/05.runbooks/index.md`・`management/index.md` 再生成および `doctor.py --strict`（AC4）：作業ブランチ上では一覧更新禁止のため、マージ直後の統合ブランチ側クローズ手順で一括検証する方針を人間が承認済み（2026-11-28）。
  * 作成した Runbook の実実施（`/aico-runbook-run review-worker-models`）：DoR 合意のとおり本チケットのスコープ外として人間が承認済み（別途必要に応じて実施）。
* **システム設計書・仕様書の更新確認**：更新不要（AIco 本体の定常運用 Runbook 新設のみであり、`docs/03.spec/` や配布テンプレートの仕様変更を伴わないため）。
* **ADR の要否判断**：作成不要（複数作業に跨る新規アーキテクチャ決定はなく、公開境界ルールは議事録 `20261124-140309-discussion-onboarding-improvement` で合意済みの方針を Runbook へ具体化したものであるため）。
* **関連記録・ADR への導線確認**：確認済み（議事録 `20261124-140309-discussion-onboarding-improvement` と相互参照済み、先行チケット `20261124-155511-ticket-onboarding-docs-and-cli-ux` へのリンク実在確認済み、`doctor.py` でリンク切れ 0 件）。

## 親子チケット・関連

* [議事録：初見ユーザー向けの導入・利用ハードル低減の整備](../../02.discussions/20261124-140309-discussion-onboarding-improvement.md)
* [先行チケット：初見ユーザー向けガイド整備と導入・初期設定ツール UX 改善](../20261124-155511-ticket-onboarding-docs-and-cli-ux/index.md)
