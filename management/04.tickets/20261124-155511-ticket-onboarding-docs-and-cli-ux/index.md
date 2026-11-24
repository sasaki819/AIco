---
id: 20261124-155511-ticket-onboarding-docs-and-cli-ux
title: 初見ユーザー向けガイド整備と導入・初期設定ツール UX 改善
status: done
created: 2026-11-24 15:55:11
updated: 2026-11-24 23:06:13
phase: closing
phase_status: done
branch: feature/20261124-155511-ticket-onboarding-docs-and-cli-ux
parent: null
children: []
discussions:
  - 20261124-140309-discussion-onboarding-improvement
adrs: []
---

# 初見ユーザー向けガイド整備と導入・初期設定ツール UX 改善

## 概要

AI エージェントを最近プロジェクトで使い始めた若手エンジニアが、AIco を迷わず導入して最初の 1 チケットを完走できるよう、`docs/04.user-guide/` の新設・`template/management/01.manual/` への同期配布・`README.md` の入口刷新・導入および初期設定ツール（`install.py`・`init.py`・`upgrade.py`・`template/AGENTS.md`）の UX 改善を行う。

## AC（受け入れ条件）

* [x] `docs/04.user-guide/` 配下に 6 ファイル（`index.md`・`01.getting-started.md`・`02.tutorial.md`・`03.cheatsheet.md`・`04.user-guide.md`・`05.worker-models.md`）が整備され、`docs/03.spec/` の詳細仕様と二重管理しない「使いこなしガイド」になっていること。
* [x] `docs/04.user-guide/` 内の相対リンクが同ディレクトリ内で自己完結しており、`template/management/01.manual/` へ完全同一コピーが配置され、旧 `workflow-reference.md` が廃止されていること。
* [x] `tests/` に `docs/04.user-guide/` と `template/management/01.manual/` の完全一致を検証する自動テストが追加されていること。
* [x] `README.md` に初見ユーザー向けの導入導線（概要・前提・クイックスタート・`docs/04.user-guide/` への案内・目的別ドキュメント導線）が整備され、`docs/03.spec/08.adoption-and-migration.md` の構成図および `install.py --init` 仕様・設計意図（非必須ショートカット・廃止可能）が整合更新されていること。
* [x] `01.getting-started.md` では 2 段階導入（`install.py` → `tools/aico.sh init`）を基本として案内し、`--init` オプションは 1 文の補足にとどめていること。また `05.worker-models.md` へのリンクおよび `AGENTS.md` 記入例が含まれていること。
* [x] `installer/install.py` に完了時・エラー時案内の強化および `--init` オプション（配置済み `init.py` を呼ぶ薄いラッパー）が実装され、`template/management/scripts/init.py` の対話案内・完了後ステップ案内・`WARN` 補足が改善されていること。
* [x] `template/AGENTS.md` のマニュアル参照先が新しい 6 ファイル構成へ更新され、`installer/upgrade.py` で既存導入先の旧 `workflow-reference.md` が安全に整理されること。
* [x] ワーカー同期アダプター（`manifest.py`・`agents_sync.py`・`docs/03.spec/05.agent-config.md`）が公式仕様に整合していること（Antigravity は `effort` 非対応として未設定警告対象外・出力省略、GitHub Copilot は `reasoning-effort` キーで出力）。
* [x] 追加・更新した全 Markdown が `aico-markdown-write` 規約（UTF-8 BOM なし・LF・強制改行の行末半角スペース 2 個・リンク切れなし）を満たし、`python3 -m unittest discover -s tests -v` が全件通過すること。

## DoR（着手合意）

* **任せる範囲**：設計詳細（`plan.md`）・`docs/04.user-guide/` および `README.md`・`docs/03.spec/08` の執筆更新、`template/`・`installer/`・`tests/` の実装とテスト検証。なお AIco 本体運営領域（ルート直下の `AGENTS.md`・`management/01.manual/` 等）の自己適用はリリース前手順に従い本チケット作業ブランチ内では直接改造しない。
* **未決事項**：`05.worker-models.md` に記載する初版の 4 ツール別推奨モデル値は、計画または実装時に現在の AIco 本体 `management/aico-manifest.json` 実績および公式情報をもとに確認のうえ設定する（Runbook 整備は別チケットで対応）。
* **着手合意**：合意済み（2026-11-24）

## 現在地

* **状況**：完了（人間レビュー round1・独立ワーカーレビュー round2 および再確認の全 5 指摘を解消し、DoD 確認・完了確定済み）
* **ブロッカー（確認待ち）**：なし
* **次に取る行動**：作業ブランチを統合ブランチ（`main`）へ統合後、統合ブランチ側で `rebuild_indexes.py`（`aico-ticket-close` 統合後ステップ）を実行し、後続チケット（レビューフロー整備）を起票する

## 変更ファイル

<!-- AICO:AUTO:BEGIN:changed-files -->
| 種別 | パス |
| :--- | :--- |
| `M` | `README.md` |
| `M` | `docs/03.spec/05.agent-config.md` |
| `M` | `docs/03.spec/08.adoption-and-migration.md` |
| `A` | `docs/04.user-guide/01.getting-started.md` |
| `A` | `docs/04.user-guide/02.tutorial.md` |
| `A` | `docs/04.user-guide/03.cheatsheet.md` |
| `A` | `docs/04.user-guide/04.user-guide.md` |
| `A` | `docs/04.user-guide/05.worker-models.md` |
| `A` | `docs/04.user-guide/index.md` |
| `M` | `installer/install.py` |
| `M` | `template/AGENTS.md` |
| `A` | `template/management/01.manual/01.getting-started.md` |
| `A` | `template/management/01.manual/02.tutorial.md` |
| `A` | `template/management/01.manual/03.cheatsheet.md` |
| `A` | `template/management/01.manual/04.user-guide.md` |
| `A` | `template/management/01.manual/05.worker-models.md` |
| `D` | `template/management/01.manual/getting-started.md` |
| `M` | `template/management/01.manual/index.md` |
| `D` | `template/management/01.manual/workflow-reference.md` |
| `M` | `template/management/02.discussions/index.md` |
| `M` | `template/management/03.adr/index.md` |
| `M` | `template/management/04.tickets/index.md` |
| `M` | `template/management/05.runbooks/index.md` |
| `M` | `template/management/index.md` |
| `M` | `template/management/scripts/_lib/agents_sync.py` |
| `M` | `template/management/scripts/_lib/cli.py` |
| `M` | `template/management/scripts/_lib/manifest.py` |
| `M` | `template/management/scripts/_lib/markers.py` |
| `M` | `template/management/scripts/init.py` |
| `M` | `template/management/templates/review-index.md` |
| `M` | `template/management/templates/ticket-index.md` |
| `M` | `tests/test_daily_scripts.py` |
| `M` | `tests/test_lib.py` |
| `M` | `tests/test_lifecycle.py` |
| `A` | `tests/test_user_guide.py` |
<!-- AICO:AUTO:END:changed-files -->

## DoD（完了の定義）

* **AC 検証結果と根拠**：全 9 項目を達成確認済み。
  * AC-1〜3：`docs/04.user-guide/` 6 ファイル（`index.md`・`01.getting-started.md`〜`05.worker-models.md`）を整備し、`template/management/01.manual/` へ完全同一コピー同期（旧 `workflow-reference.md`・無番ファイル廃止）および `tests/test_user_guide.py` による同期・リンク自己完結・Markdown 品質自動検証を追加。
  * AC-4〜5：`README.md`・`docs/03.spec/08.adoption-and-migration.md`（構成図・`--init` 設計意図・`latest` fast-forward 専用ブランチ運用）・`01.getting-started.md`（2 段階基本、`--init` 1 文補足、`05.worker-models.md` リンク、`AGENTS.md` 記入例）を整備。
  * AC-6〜7：`installer/install.py`（案内強化・`--init` ラッパー）・`template/management/scripts/init.py`・`_lib/cli.py`（`stdout` 送出・重複 `WARN:` 抑止）・`_lib/markers.py`（`AICO:AUTO` 前後空行）・`template/AGENTS.md` 更新を実装し、`tests/test_lifecycle.py`・`tests/test_lib.py` で検証。
  * AC-8：`manifest.py`・`agents_sync.py`・`docs/03.spec/05.agent-config.md` を Antigravity（`effort` 非対応）および Copilot（`reasoning-effort`）公式仕様へ整合し、`tests/test_lib.py`・`tests/test_lifecycle.py` で検証。
  * AC-9：`python3 -m unittest discover -s tests -v`（30/30 OK）、`uv run management/scripts/doctor.py --json`（OK=9 / WARN=0 / ERROR=0）、人間レビュー round1（2 件 `done`）・独立ワーカーレビュー round2（3 件 `done`・未解決 0 件）を通過。
* **未検証項目と人の判断結果**：なし（独立ワーカー内サンドボックス制約で未実行だった動的コマンド検証は親セッションで全件実行・通過済み。人間による完了承認取得済み）
* **関連記録・ADR への導線確認**：確認済み（議事録 `20261124-140309-discussion-onboarding-improvement` および関連チケット `20261124-155511-ticket-worker-models-review-runbook` へのリンク実在を `doctor.py` で検証済み。新規 ADR 対象なし）

## 親子チケット・関連

* [議事録：初見ユーザー向けの導入・利用ハードル低減の整備](../../02.discussions/20261124-140309-discussion-onboarding-improvement.md)
* [関連チケット：worker_models おすすめ設定見直し用 Runbook の作成](../20261124-155511-ticket-worker-models-review-runbook/index.md)
