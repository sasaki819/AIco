---
id: 20261124-155511-ticket-onboarding-docs-and-cli-ux
title: 初見ユーザー向けガイド整備と導入・初期設定ツール UX 改善
status: open
created: 2026-11-24 15:55:11
updated: 2026-11-24 15:55:11
phase: drafting
phase_status: working
branch: feature/20261124-155511-ticket-onboarding-docs-and-cli-ux
parent: null
children: []
discussions: [20261124-140309-discussion-onboarding-improvement]
adrs: []
---

# 初見ユーザー向けガイド整備と導入・初期設定ツール UX 改善

## 概要

AI エージェントを最近プロジェクトで使い始めた若手エンジニアが、AIco を迷わず導入して最初の 1 チケットを完走できるよう、`docs/04.user-guide/` の新設・`template/management/01.manual/` への同期配布・`README.md` の入口刷新・導入および初期設定ツール（`install.py`・`init.py`・`upgrade.py`・`template/AGENTS.md`）の UX 改善を行う。

## AC（受け入れ条件）

* [ ] `docs/04.user-guide/` 配下に 6 ファイル（`index.md`・`getting-started.md`・`tutorial.md`・`cheatsheet.md`・`user-guide.md`・`worker-models.md`）が整備され、`docs/03.spec/` の詳細仕様と二重管理しない「使いこなしガイド」になっていること。
* [ ] `docs/04.user-guide/` 内の相対リンクが同ディレクトリ内で自己完結しており、`template/management/01.manual/` へ完全同一コピーが配置され、旧 `workflow-reference.md` が廃止されていること。
* [ ] `tests/` に `docs/04.user-guide/` と `template/management/01.manual/` の完全一致を検証する自動テストが追加されていること。
* [ ] `README.md` に初見ユーザー向けの導入導線（概要・前提・クイックスタート・`docs/04.user-guide/` への案内・目的別ドキュメント導線）が整備され、`docs/03.spec/08.adoption-and-migration.md` の構成図および `install.py --init` 仕様・設計意図（非必須ショートカット・廃止可能）が整合更新されていること。
* [ ] `getting-started.md` では 2 段階導入（`install.py` → `tools/aico.sh init`）を基本として案内し、`--init` オプションは 1 文の補足にとどめていること。また `worker-models.md` へのリンクおよび `AGENTS.md` 記入例が含まれていること。
* [ ] `installer/install.py` に完了時・エラー時案内の強化および `--init` オプション（配置済み `init.py` を呼ぶ薄いラッパー）が実装され、`template/management/scripts/init.py` の対話案内・完了後ステップ案内・`WARN` 補足が改善されていること。
* [ ] `template/AGENTS.md` のマニュアル参照先が新しい 6 ファイル構成へ更新され、`installer/upgrade.py` で既存導入先の旧 `workflow-reference.md` が安全に整理されること。
* [ ] 追加・更新した全 Markdown が `aico-markdown-write` 規約（UTF-8 BOM なし・LF・強制改行の行末半角スペース 2 個・リンク切れなし）を満たし、`python3 -m unittest discover -s tests -v` が全件通過すること。

## DoR（着手合意）

* **任せる範囲**：設計詳細（`plan.md`）・`docs/04.user-guide/` および `README.md`・`docs/03.spec/08` の執筆更新、`template/`・`installer/`・`tests/` の実装とテスト検証。なお AIco 本体運営領域（ルート直下の `AGENTS.md`・`management/01.manual/` 等）の自己適用はリリース前手順に従い本チケット作業ブランチ内では直接改造しない。
* **未決事項**：`worker-models.md` に記載する初版の 4 ツール別推奨モデル値は、計画または実装時に現在の AIco 本体 `management/aico-manifest.json` 実績および公式情報をもとに確認のうえ設定する（Runbook 整備は別チケットで対応）。
* **着手合意**：未合意

## 現在地

* **状況**：起票完了
* **ブロッカー（確認待ち）**：なし
* **次に取る行動**：DoR を確認し `aico-ticket-start` で作業ブランチを作成する

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
* [関連チケット：worker_models おすすめ設定見直し用 Runbook の作成](../20261124-155511-ticket-worker-models-review-runbook/index.md)
