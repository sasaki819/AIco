---
id: 20261124-234050-ticket-evaluate-ai-dev-standard-comparison
title: ai-dev-standard との比較評価および優位要素の取り込み検討
status: done
created: 2026-11-24 23:40:50
updated: 2026-11-25 00:30:57
phase: closing
phase_status: done
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

* [x] `ai-dev-standard` および `jotline` の構成・運用実態を一次情報（実リポジトリ）に基づいて調査し、AIco との比較評価（設計思想・構成・コンテキスト管理・ワークフロー・テンプレート・スキル／ルール・スクリプト／CLI・移行観点）が `plan.md` 等に構造化記録されていること。
* [x] `ai-dev-standard`（および `jotline` の運用実態）に AIco より優れている点・補完すべき実践知があるかを網羅的に棚卸しし、各候補について「AIco への取り込み推奨度・AIco の思想との整合性・期待効果・反映先（本チケット／既存チケット／新規チケット／見送り）」が整理されていること。
* [x] `ai-dev-standard` の廃止可否判断および取り込み候補の採否について人間の合意が得られ、判断根拠が記録されていること。
* [x] 本チケットで取り込むと合意された項目がある場合は、仕様書（`docs/`）・配布原本（`template/`・`installer/`）・テスト（`tests/`）へ整合反映され、`python3 -m unittest discover -s tests -v` および `doctor.py` が通過していること（取り込み対象が 0 件または全件別チケット化と合意された場合は、比較評価および引き継ぎ先整理の完了をもって達成とする）。
* [x] `jotline` の AIco 移行を見据えた気づき（移行時の注意点や AIco 側の不足があれば）が比較結果に整理されていること。

## DoR（着手合意）

* **任せる範囲**：一時ディレクトリへの `ai-dev-standard`・`jotline` の読み取り専用取得（AIco リポジトリを汚さない）、両リポジトリと AIco の比較分析、優位要素・移行観点の抽出および採否提案の作成（`plan.md`）。採否決定後の反映範囲は人間との合意のうえ実施する。
* **未決事項**：
  * 比較評価の結果として採用が決まった項目を、本チケット内で実装まで行うか、本チケットは調査・採否決定までとして既存／新規チケットへ起票し直すか（比較評価の提示時に合意）。
  * 比較レポートを `plan.md` 内に収めるか、必要に応じて別途 ADR や議事録へ昇格するか（比較評価の提示時に確認）。
* **着手合意**：合意済み（2026-11-24）

## 現在地

* **状況**：完了（`ai-dev-standard`・`jotline` との比較評価および採否決定・引き継ぎ方針の人間合意が完了）
* **ブロッカー（確認待ち）**：なし
* **次に取る行動**：`main` へマージ・旧作業ブランチ削除・統合後一覧再生成を行い、採用項目（A-1〜A-4・B-1〜B-3）を `20261124-231830-ticket-workflow-review-and-ux-improvements` へ統合する

## 変更ファイル

<!-- AICO:AUTO:BEGIN:changed-files -->
変更されたプロジェクト資産はない。
<!-- AICO:AUTO:END:changed-files -->

## DoD（完了の定義）

* **AC 検証結果と根拠**：全 5 項目を達成確認済み。
  * AC-1・AC-2・AC-5：`ai-dev-standard`（`2d2c6eb`）および `jotline`（`81c7e0b`）の実リポジトリを調査し、全体比較・取り込み候補 8 件（A-1〜A-4・B-1〜B-4）・見送り 7 件・`jotline` 移行観点を [比較評価レポート](notes/001-comparison-evaluation.md) へ構造化記録した。
  * AC-3・AC-4：人間と「`ai-dev-standard` は安全に廃止可能」「A-1〜A-4（A-2 は `pr_template` 任意パス指定＋任意 CI ガイド方式）・B-1〜B-3 を採用し既存 UX 改善チケット `20261124-231830-ticket-workflow-review-and-ux-improvements` へ統合」「B-4 は将来 Runbook 候補」を合意・記録済み。`uv run management/scripts/doctor.py --json` 異常なし。
* **未検証項目と人の判断結果**：なし（調査・採否決定チケットのため設計・実装フェーズは人間合意のもとスキップし、全採用項目を `20261124-231830-ticket-workflow-review-and-ux-improvements` へ引き継ぐことで完了承認取得済み）
* **関連記録・ADR への導線確認**：確認済み（引き継ぎ先チケット `20261124-231830-ticket-workflow-review-and-ux-improvements` および [比較評価レポート](notes/001-comparison-evaluation.md) へのリンク実在を `doctor.py` で検証済み。新規 ADR 対象なし）

## 親子チケット・関連

* [関連チケット：レビューフロー・クローズ手順・AI 進行案内の UX 改善](../20261124-231830-ticket-workflow-review-and-ux-improvements/index.md)
* [関連チケット：worker_models おすすめ設定見直し用 Runbook の作成](../20261124-155511-ticket-worker-models-review-runbook/index.md)
