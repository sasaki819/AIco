# ワークフロー・スクリプト参照

## 概要

AIco における記録種別・3軸状態・ブランチ更新責務・レビュー循環および共有スクリプトの参照情報をまとめる。

## 1. 記録種別と統一ステータス

管理ルート配下では以下の記録を管理する。

| 記録種別 | 配置先 | 許容 `status` |
| :--- | :--- | :--- |
| 議事録 | `02.discussions/<YYYYMMDD-HHMMSS>-discussion-<slug>.md` | `open` / `in-progress` / `done` / `cancelled` |
| ADR | `03.adr/<YYYYMMDD-HHMMSS>-adr-<slug>.md` | `open` / `accepted` / `deprecated` / `cancelled` |
| チケット | `04.tickets/<YYYYMMDD-HHMMSS>-ticket-<slug>/index.md` | `open` / `in-progress` / `done` / `cancelled` |
| チケット内ノート | `<チケット>/notes/<NNN>-<slug>.md` | なし（`status` を持たない） |
| レビュー指摘 | `<対象>/review/findings/<id>.md` | `open` / `in-progress` / `done` / `cancelled` |
| Runbook 手順書 | `05.runbooks/<slug>/runbook.md` | なし（`status` を持たない） |
| Runbook 実施記録 | `05.runbooks/<runbook>/records/<YYYYMMDD-HHMMSS>-<slug>/index.md` | `in-progress` / `done` / `cancelled` |

一覧における `active` / `closed` は、`open`・`in-progress` を `active`、`done`・`cancelled` を `closed` へ機械的に集約する。

## 2. チケットの3軸状態管理

チケットの進捗は以下の3軸を `index.md` の YAML frontmatter で管理する。

* **`status`**：`open` / `in-progress` / `done` / `cancelled`
* **`phase`**：`drafting` → `planning` → `design` → `implementation` → `closing`（不要な `design` は合意のうえスキップ可）
* **`phase_status`**：`working` → `reviewing` → `triaging` → `fixing` → `re-reviewing` → `done`

正常クローズ時は `status: done`・`phase: closing`・`phase_status: done` へ確定する。
中止時は `status: cancelled` へ更新し、`phase`・`phase_status` は中止時点の値を維持する。

## 3. ブランチ別の更新責務

* **統合ブランチ（`integration_branch`）**：議事録・ADR・Runbook・チケット起票・`management/index.md` および各区分 `index.md` の再生成・アーカイブ移動を行う。
* **作業ブランチ**：対象チケットの成果物、チケット配下の全記録、`## 変更ファイル` および `review/index.md` の再生成、完了時のチケット `status` 更新を行う。全体一覧（`management/index.md` 等）は更新しない。

## 4. 独立レビューと人間選別

レビュー（`aico-review`）と再確認（`aico-review-recheck`）は、作成担当セッションとは独立したコンテキスト（`worker-middle` または `worker-high`）へ必ず委譲する。
指摘の採否選別（`aico-review-triage`）は必ず人間が決定し、AI が独断で採否を確定してはならない。

## 5. 共有スクリプト一覧

人間は `tools/aico.sh <機能名> [引数...]`（Windows は `tools/aico.bat`）、AI は `uv run <管理ルート>/scripts/<機能名>.py [引数...]` で実行する。

| スクリプト名 | 用途 |
| :--- | :--- |
| `create_discussion.py` | 議事録ファイルを作成 |
| `create_adr.py` | ADR ファイルを作成 |
| `create_ticket.py` | チケットフォルダ一式を作成 |
| `create_ticket_note.py` | チケット内ノートを作成（`NNN` 自動採番） |
| `create_runbook.py` | Runbook 手順書を作成 |
| `create_runbook_record.py` | Runbook 実施記録フォルダを作成 |
| `create_review_finding.py` | レビュー指摘ファイルを作成 |
| `record_review_run.py` | `review/index.md` 初期化・レビュー実施記録追記 |
| `update_frontmatter.py` | frontmatter・3軸状態の検証付き更新・相互参照同期 |
| `update_changed_files.py` | チケット `## 変更ファイル` の自動更新 |
| `rebuild_indexes.py` | ダッシュボード・各区分一覧・指摘一覧のべき等再生成 |
| `ticket_status.py` | 対象チケット自動特定・推奨次スキル判定・未解決指摘照会 |
| `archive_record.py` | 完了済み記録の `archived/` 移動と双方向リンク追従 |
| `sync_agents.py` | スキル同期・ツール別ワーカー定義生成・`CLAUDE.md` 同期 |
| `doctor.py` | 環境・設定・同期・記録規約・リンク切れの総合診断 |
| `init.py` | 導入先固有設定の初期化・再設定 |
| `update.py` | 版比較・配布元取得・アップデート実行委譲 |
