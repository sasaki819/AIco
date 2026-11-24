---
id: 20261124-234050-ticket-evaluate-ai-dev-standard-comparison
title: ai-dev-standard との比較評価および優位要素の取り込み検討
status: open
created: 2026-11-24 23:40:50
updated: 2026-11-24 23:40:50
phase: drafting
phase_status: working
branch: feature/20261124-234050-ticket-evaluate-ai-dev-standard-comparison
parent: null
children: []
discussions: []
adrs: []
---

# ai-dev-standard との比較評価および優位要素の取り込み検討

## 概要

AIco の前身・着想元である `ai-dev-standard`（`https://gitlab.sasaki819.mydns.jp/open/ai-dev-standard.git`）および、同フレームワークを導入して開発進行中（近く AIco へ移行予定）の実プロジェクト `jotline`（`https://gitlab.sasaki819.mydns.jp/open/jotline.git`）を AIco と比較評価する。  
`ai-dev-standard` を安心して廃止できる根拠を確認するとともに、`ai-dev-standard` 側または `jotline` 実運用側に AIco へ取り込む価値のある優位要素・実践知があれば抽出し、採否判断および取り込み方針（本チケットでの反映または後続チケット化）を決定する。

## AC（受け入れ条件）

* [ ] `ai-dev-standard` および `jotline` の構成・運用実態を一次情報（実リポジトリ）に基づいて調査し、AIco との比較評価（設計思想・構成・コンテキスト管理・ワークフロー・テンプレート・スキル／ルール・スクリプト／CLI・移行観点）が `plan.md` 等に構造化記録されていること。
* [ ] `ai-dev-standard`（および `jotline` の運用実態）に AIco より優れている点・補完すべき実践知があるかを網羅的に棚卸しし、各候補について「AIco への取り込み推奨度・AIco の思想との整合性・期待効果・反映先（本チケット／既存チケット／新規チケット／見送り）」が整理されていること。
* [ ] `ai-dev-standard` の廃止可否判断および取り込み候補の採否について人間の合意が得られ、判断根拠が記録されていること。
* [ ] 本チケットで取り込むと合意された項目がある場合は、仕様書（`docs/`）・配布原本（`template/`・`installer/`）・テスト（`tests/`）へ整合反映され、`python3 -m unittest discover -s tests -v` および `doctor.py` が通過していること（取り込み対象が 0 件または全件別チケット化と合意された場合は、比較評価および引き継ぎ先整理の完了をもって達成とする）。
* [ ] `jotline` の AIco 移行を見据えた気づき（移行時の注意点や AIco 側の不足があれば）が比較結果に整理されていること。

## DoR（着手合意）

* **任せる範囲**：一時ディレクトリへの `ai-dev-standard`・`jotline` の読み取り専用取得（AIco リポジトリを汚さない）、両リポジトリと AIco の比較分析、優位要素・移行観点の抽出および採否提案の作成（`plan.md`）。採否決定後の反映範囲は人間との合意のうえ実施する。
* **未決事項**：
  * 比較評価の結果として採用が決まった項目を、本チケット内で実装まで行うか、本チケットは調査・採否決定までとして既存／新規チケットへ起票し直すか（比較評価の提示時に合意）。
  * 比較レポートを `plan.md` 内に収めるか、必要に応じて別途 ADR や議事録へ昇格するか（比較評価の提示時に確認）。
* **着手合意**：未合意

## 現在地

* **状況**：起票完了（最優先チケット）
* **ブロッカー（確認待ち）**：なし
* **次に取る行動**：DoR を確認し `aico-ticket-start` で作業ブランチを作成し、比較評価（`aico-ticket-plan`）を開始する

## 変更ファイル

<!-- AICO:AUTO:BEGIN:changed-files -->
変更されたプロジェクト資産はない。
<!-- AICO:AUTO:END:changed-files -->

## DoD（完了の定義）

* **AC 検証結果と根拠**：
* **未検証項目と人の判断結果**：なし
* **関連記録・ADR への導線確認**：未確認

## 親子チケット・関連

* [関連チケット：レビューフロー・クローズ手順・AI 進行案内の UX 改善](../20261124-231830-ticket-workflow-review-and-ux-improvements/index.md)
* [関連チケット：worker_models おすすめ設定見直し用 Runbook の作成](../20261124-155511-ticket-worker-models-review-runbook/index.md)
