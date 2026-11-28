---
id: 20261124-140309-discussion-onboarding-improvement
title: 初見ユーザー向けの導入・利用ハードル低減の整備
status: done
created: 2026-11-24 14:03:09
updated: 2026-11-24 15:56:14
tickets:
  - 20261124-155511-ticket-onboarding-docs-and-cli-ux
  - 20261124-155511-ticket-worker-models-review-runbook
adrs: []
---

# 初見ユーザー向けの導入・利用ハードル低減の整備

## 概要

AIco を初めて知り導入・利用しようとする若手エンジニアに向けて、「まず何をすれば良いのか」が迷わず分かる状態を整備する方針を合意した。  
`docs/04.user-guide/` の新設と `template/management/01.manual/` への同期配布、`README.md` の入口刷新、導入・初期設定ツール UX 改善、および `worker_models` 見直し用 Runbook の新設を 2 チケットに分けて進める。

## 背景

`v0.1.0` のリリースおよび既存プロジェクトへの導入・他者への紹介を踏まえ、AI エージェントを最近プロジェクトで使い始めた若手エンジニアであっても、専門的な事前知識なしに導入して使い始められる導線が必要となった。

## 確認した事実と仮説

* **確認した事実**：
  * `README.md` は概要・目的・基本方針・3層構造・`docs/` リンクのみで構成されており、前提要件・インストール手順・クイックスタート・最初の使い方が記載されていない。
  * 既存 `template/management/01.manual/workflow-reference.md` は 3 軸状態・許容 `status` 表・全 17 スクリプト一覧を掲載しており、`docs/03.spec/` と二重管理になりやすい構成である。
  * `installer/install.py` の完了メッセージは `tools/aico.sh init` 実行案内のみで、導入先マニュアルへの導線がない。
  * `template/management/scripts/init.py` の対話ウィザードでは `worker_models` 設定時に「空欄のままでも各ツールの既定モデルで動作する」「おすすめ設定例がある」旨の案内がなく、完了メッセージにも初回コミットや最初の利用ステップ（チュートリアル案内）が表示されない。
  * 個人プロジェクト資産 `model-chart`（非公開リポジトリ）は Artificial Analysis の公式無料 API から思考レベル別の Intelligence Index・業界別指数（Engineering 等）・タスク当たりコストを比較できるが、無料 API の利用規約上「出典表記付きの内部利用のみ・再配布不可」の制約がある。
  * AIco 本体は GitHub（`https://github.com/sasaki819/AIco.git`）へ公開ミラーされるため、リポジトリ内の公開ファイルや Runbook へ非公開リポジトリ URL や再配布不可のベンチマーク数値を記載してはならない。
* **仮説**：
  * `docs/04.user-guide/` を「仕様詳細の複製」ではなく「最初の使いこなしガイド」に徹することで、`03.spec/` との二重管理を防ぎつつ若手エンジニアの学習負荷を下げられる。
  * 原本（`docs/04.user-guide/`）と配布コピー（`template/management/01.manual/`）の一致を自動テストで検証し、相対リンクを同ディレクトリ内で自己完結させることで、乖離と導入先リンク切れを構造的に防げる。
  * `install.py --init` を配置後に配置済み `init.py` を呼ぶだけの薄いラッパーにとどめ、ドキュメント上は 2 段階方式を基本として 1 文補足のみとすることで、初見の迷いと保守負債を抑えつつ熟練者の利便性も確保できる。

## 議論・合意事項と理由

### 1. 想定ターゲットと `docs/04.user-guide/` の位置づけ

* **想定ターゲット**：スキル自作や高度ツール（Kiro・Devin・Spec-Kit 等）に習熟した層ではなく、「最近プロジェクトで AI エージェントを使えるようになった若手エンジニア」。
* **位置づけ**：`docs/03.spec/` との二重管理を避け、詳しい仕様は AIco リポジトリの `docs/03.spec/` で確認してもらう前提で、最初の「使いこなしガイド」にとどめる。
* **ファイル構成（6 ファイル）**：既存の `workflow-reference.md` は廃止し、以下 6 ファイルへ整理する。
  * `index.md`：目次と「まずここから」の読み順ガイド
  * `getting-started.md`：導入（`install.py`）→ 初期設定（`init`）→ `AGENTS.md` 記入例 → `worker_models` 案内 → `doctor` → `update`
  * `tutorial.md`：最初の 1 チケット完走ハンズオン（AI への具体的な声かけ例つき）
  * `cheatsheet.md`：逆引き早見表、まず覚える基本 6 スキル＋他スキルのひとこと一覧、よく使うコマンド
  * `user-guide.md`：4 種の管理情報の使い分け、ブランチとレビューの基本感覚、FAQ・トラブルシュート
  * `worker-models.md`：おすすめ `worker_models` 設定例（最終確認日、空欄でも動く旨、4 ツール別 JSON 例、`sync_agents` 手順）

### 2. 原本と配布コピーの同期・リンク設計

* `docs/04.user-guide/` を原本とし、`template/management/01.manual/` へ完全同一コピーを配置する。
* `docs/04.user-guide/` 内の相対リンクは同ディレクトリ内で自己完結させ、導入先 `management/01.manual/` でのリンク切れを防ぐ。
* `tests/` に `docs/04.user-guide/` と `template/management/01.manual/` の完全一致を検証する自動テストを追加する。
* `README.md` に入口導線（全体像・クイックスタート・目的別ドキュメント案内）を追加し、`docs/03.spec/08.adoption-and-migration.md` の構成図へも `docs/04.user-guide/` を反映する。

### 3. `worker_models` おすすめ設定例と Runbook の公開境界

* おすすめ設定例を `docs/04.user-guide/worker-models.md` として整備し、`getting-started.md` からリンクする。
* 定期見直し手順を AIco 本体の `management/05.runbooks/` に Runbook として新設する（別チケットで実施）。
* `model-chart` 等のベンチマーク比較資産はメンテナの内部判断資料として活用し、公開ファイルおよび Runbook 本文・実施記録には非公開 URL や再配布不可のベンチマーク生数値を記載しない（推奨モデル ID・`effort`・定性的な選定理由のみ記載する）。

### 4. 導入・初期設定ツール UX 改善と `--init` の設計意図

* `init.py` の対話説明（`worker_models` 空欄許容・おすすめ設定例案内）および完了メッセージ（次の 3 ステップ案内・`WARN` 補足）を親切化する。
* `install.py` の完了案内・エラー時対処例を強化し、任意オプション `--init`（配置後に配置済み `init.py` をそのまま呼び出す薄いラッパー）を追加する。
* **`--init` の設計意図と案内方針**：
  * `getting-started.md` では初心者向けに 2 段階方式（`install.py` → `tools/aico.sh init`）を基本手順として案内し、`--init` は 1 文の補足にとどめる（初手で複数経路を提示して迷わせないため）。
  * `--init` は AIco に慣れた利用者の利便性のための非必須ショートカットであり、保守上の不都合が生じた際は廃止して構わない前提とする。この設計意図を本議事録および `docs/03.spec/08.adoption-and-migration.md` に明記する。
* `template/AGENTS.md` のマニュアル参照先を新しい 6 ファイル構成へ更新し、`upgrade.py` で旧 `workflow-reference.md` の整理（または移行処理）を行えるようにする。

### 5. チケット分割と着手順

* 先に「初見ユーザー向けガイド整備と導入・初期設定ツール UX 改善」チケットを完了し、続いて別チケットとして「`worker_models` おすすめ設定見直し用 Runbook の作成」を実施する。

## 未決事項

* 特になし（詳細な変更設計・テスト計画は各チケットの `plan.md` で策定する）。

## 関連

* [チケット 1：初見ユーザー向けガイド整備と導入・初期設定ツール UX 改善](../../04.tickets/archived/20261124-155511-ticket-onboarding-docs-and-cli-ux/index.md)
* [チケット 2：worker_models おすすめ設定見直し用 Runbook の作成](../../04.tickets/20261124-155511-ticket-worker-models-review-runbook/index.md)
* [README.md](../../../README.md)
* [06. エージェント・スキル方針](../../../docs/02.policy/06.agent-and-skills.md)
* [08. 導入・移行・リリース仕様](../../../docs/03.spec/08.adoption-and-migration.md)
* [installer/install.py](../../../installer/install.py)
* [template/management/scripts/init.py](../../../template/management/scripts/init.py)
