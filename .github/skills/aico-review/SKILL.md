---
name: aico-review
description: 独立コンテキストのワーカーへ委譲して成果物をレビューし、チケット・Runbook 実施記録では指摘ファイルと実施履歴を記録する。
---

# aico-review

## 目的

作成担当セッションとは独立したコンテキストで成果物（チケットの現在フェーズ成果物、Runbook 実施記録、または手順書・ADR・議事録等の単一文書）をレビューし、品質と仕様整合を検証する。

## 入力

* 対象チケット ID・Runbook 実施記録 ID（`<runbook>/<record-id>` 等）、または単一文書のファイルパス
* 対象範囲（省略時は現在フェーズの成果物および統合ブランチとの差分、または対象記録と添付物一式）
* 対象 ID の指定が省略された場合は、以下の3段階フォールバックで解決する。
1. ユーザーの明示指定（ID・`slug`・パス）。
2. `uv run <管理ルート>/scripts/ticket_status.py --json` による現在の Git ブランチと `branch` 属性の照合。
3. 自動特定できない場合は該当状態の候補一覧を提示して人間に選択してもらう。

## 前提条件

* **チケット対象時**：作業ブランチ上であること、`status: in-progress`・`phase_status: reviewing` であること。
* **Runbook 実施記録対象時**：統合ブランチ上であること、対象記録が `status: in-progress` であること。
* **単一文書対象時**：対象ファイルが存在すること。

## 手順

### 1. チケットおよび Runbook 実施記録（`review/` 管理あり）

1. 独立コンテキストのワーカー（**必須委譲**：原則 `worker-middle`、重要な設計レビュー時は `worker-high`）へ、以下の5項目を明示してレビューを委譲する。親セッションの自己追認で代用してはならない。
   サブエージェントワーカーへ委譲する際は、親セッションの会話履歴が引き継がれない前提で、必ず以下の5項目をプロンプトへ明示する。
1. 参照する手順書・スキルパス
2. 対象範囲（ファイル・調査対象・比較基点コミット等）
3. 入力条件・制約（前提条件・対象外・守るべき規約）
4. 変更可否（読み取り専用か、許可する編集範囲はどこか）
5. 期待する成果と報告形式（出力先パス・実行環境・未確認事項を含む）
2. 検出した各指摘を `create_review_finding.py` で1件1ファイル（`status: open`）として作成し、`aico-markdown-write` に従って対象・指摘内容と根拠を記入する。
   ```bash
   uv run <管理ルート>/scripts/create_review_finding.py --target <対象> --slug <slug> --title "<件名>" --severity <critical|major|minor> --reviewer "<実施者>" --json
   ```
3. `record_review_run.py` で `review/index.md` の初期化（Runbook 実施記録で指摘 0 件の場合も含む）および `## レビュー実施記録` の追記を行う。
   ```bash
   uv run <管理ルート>/scripts/record_review_run.py --target <対象> --kind initial --reviewer "<実施者>" --base-commit "<比較基点>" --env "<実行環境>" --unverified "<未確認事項>" --json
   ```
4. `rebuild_indexes.py --scope reviews --target <対象>` で `## 指摘一覧` を再生成する。
5. チケット対象時は、指摘が1件以上あれば `phase_status: triaging` へ更新し、0件であれば人間承認のうえ次フェーズの `working`（`closing` 時は `status: done`・`closing / done`）へ進める（Runbook 実施記録時は `phase_status` を更新しない）。

### 2. 単一文書（Runbook 手順書・ADR・議事録等、`review/` なし）

1. 独立コンテキストのワーカー（原則 `worker-middle`、重要設計時は `worker-high`）へ5項目委譲規約を満たしてレビューを委譲する。
2. 検出した指摘・改善案・実行環境・未確認事項を人間へ報告する（`review/findings/` 作成や状態更新は行わない）。

## 完了条件と状態更新

* 独立ワーカーによるレビューが完了していること。
* チケット対象時：指摘あり → `<phase> / triaging`、指摘なし → 合意した次フェーズ `working`（`closing` 時は `status: done` / `closing / done`）。
* Runbook 実施記録対象時：実施記録追記および指摘ファイル作成（`phase_status` なし）。
* 単一文書対象時：状態変更なし。

## 報告形式

* レビュー対象（チケット時はフェーズ・ラウンド、Runbook 実施記録時はラウンド）
* 検出指摘件数（重要度別内訳）と要点
* 確認した実行環境および未確認事項
* 次スキル案内（`review/` 管理対象時：指摘ありなら `aico-review-triage`）
