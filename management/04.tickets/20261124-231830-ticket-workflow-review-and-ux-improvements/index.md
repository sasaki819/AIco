---
id: 20261124-231830-ticket-workflow-review-and-ux-improvements
title: レビューフロー・クローズ手順・AI 進行案内の UX 改善
status: open
created: 2026-11-24 23:18:30
updated: 2026-11-24 23:18:30
phase: drafting
phase_status: working
branch: feature/20261124-231830-ticket-workflow-review-and-ux-improvements
parent: null
children: []
discussions: []
adrs: []
---

# レビューフロー・クローズ手順・AI 進行案内の UX 改善

## 概要

初回チケットのドッグフーディング運用（`20261124-155511-ticket-onboarding-docs-and-cli-ux`）で検知した 3 つの実運用上の課題を解消し、AIco の日常運用における摩擦を減らして誘導性を高める。  
対象は次の 3 領域である。

1. **レビューフロー整備**：人間が任意のタイミングで指摘を登録・記録する入口、同一フェーズ内での複数ラウンドレビュー遷移（`re-reviewing` → `reviewing`）、および人間自身が挙げた指摘に対する冗長なトリアージ往復の簡略化。
2. **クローズ手順（`update_changed_files.py`）の UX 改善**：作業ブランチ上のクローズ準備時に、事前の仮コミット＋`amend`（または 2 回コミット）を強制せず変更ファイル一覧を更新できる仕組みの整備。
3. **AI 進行案内・選択肢提示ルールの整備**：`template/AGENTS.md` および節目となる主要スキルに対し、工程完了・人間承認待ち時に推奨案を先頭にした具体的な番号付き選択肢を通常の Markdown リストで提示する共通規約を追加する。

## AC（受け入れ条件）

* [ ] **人間レビュー入口とトリアージ簡略化**：人間がレビュー指摘を登録・記録する正規の手順またはスキル（`aico-review` の拡張または専用手順・スクリプト引数）が仕様書（`docs/03.spec/03.workflow.md`・`06.skills.md`・`07.scripts.md`）および `template/` に整備され、人間自身の指摘で冗長な `open` → `triaging` → `in-progress` 往復を省ける運用が定義・実装されていること。
* [ ] **同一フェーズ内複数ラウンド遷移の正規化**：同一フェーズ内で別ラウンドのレビューを追加実施する遷移（例：人間レビュー round1 解消後の `re-reviewing` → AI 独立レビュー round2 の `reviewing`）が `--force` なしで許可されるよう、状態遷移仕様（`docs/03.spec/03.workflow.md`）および `template/management/scripts/_lib/validation.py` が整合更新されていること。
* [ ] **クローズ時の変更ファイル更新 UX 改善**：`template/management/scripts/update_changed_files.py` および `template/.agents/skills/aico-ticket-close/SKILL.md`・仕様書（`06.skills.md`・`07.scripts.md`）が見直され、事前コミット＋`amend` を強制せずに作業ツリー上の未コミット変更（新規ファイル含む）も安全に反映できること。
* [ ] **AI からの選択肢誘導ルール整備**：`template/AGENTS.md` の基本原則に「進行案内と選択肢提示の原則」（オープンな質問で終わらず、推奨案を先頭に置いた具体的な番号付き選択肢を通常の Markdown で提示すること）が明文化され、節目となる主要スキル（`aico-ticket-plan`・`aico-ticket-implement`・`aico-review-triage`・`aico-review-recheck`・`aico-ticket-close` 等）および仕様書（`05.agent-config.md`・`06.skills.md`）が整合更新されていること。
* [ ] **ユーザーガイド同期**：上記変更に伴う利用手順の差分が `docs/04.user-guide/` および `template/management/01.manual/`（完全一致同期）に反映されていること。
* [ ] **検証と品質規約**：変更・追加仕様を検証する自動テストが `tests/` に整備され、`python3 -m unittest discover -s tests -v` が全件通過し、変更した全 Markdown が `aico-markdown-write` 規約（UTF-8 BOM なし・LF・リンク切れなし等）を満たしていること。

## DoR（着手合意）

* **任せる範囲**：現状調査・設計案の策定（`plan.md`）、関連仕様書（`docs/03.spec/`）・ユーザーガイド（`docs/04.user-guide/`）・`template/`・`tests/` の更新およびテスト検証。なお AIco 本体運営領域（ルート直下の `AGENTS.md`・`.agents/`・`management/scripts/`・`management/01.manual/` 等）はリリース前の `tools/aico.sh update --source .` で自己適用するため作業ブランチ内で直接改造しない。
* **未決事項**：
  * 人間レビュー記録を既存 `aico-review` スキルのモード拡張にするか、専用スキル新設にするか（`plan.md` 策定時に比較提案して合意）。
  * `update_changed_files.py` の未コミット差分取り込みを既定挙動にするか、明示オプションにするか（ステージ済み・未追跡ファイルの扱いを含め `plan.md` 策定時に比較提案して合意）。
  * 本チケットの 3 領域を 1 本で進めるか、必要に応じて別チケットへ分割するか（着手時に確認）。
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

* [発端チケット：初見ユーザー向けガイド整備と導入・初期設定ツール UX 改善](../20261124-155511-ticket-onboarding-docs-and-cli-ux/index.md)
