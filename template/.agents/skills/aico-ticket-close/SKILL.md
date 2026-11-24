---
name: aico-ticket-close
description: 変更ファイル更新・DoD 確認・完了状態確定（作業ブランチ側）および統合後の一覧再生成（統合ブランチ側）を行う。
---

# aico-ticket-close

## 目的

チケットの完了確認（変更ファイル自動更新・DoD 実物照合・人間承認・完了状態確定）と、統合ブランチ反映後の一覧再生成を安全に行う。

## 入力

* 対象チケット ID（省略可）
* 対象 ID の指定が省略された場合は、以下の3段階フォールバックで解決する。
1. ユーザーの明示指定（ID・`slug`・パス）。
2. `uv run <管理ルート>/scripts/ticket_status.py --json` による現在の Git ブランチと `branch` 属性の照合。
3. 自動特定できない場合は該当状態の候補一覧を提示して人間に選択してもらう。

## 前提条件

* **作業ブランチ側（クロージング準備）**：`status: in-progress`・`phase: closing`・`phase_status: working` であり、`review/findings/` に未解決指摘（`open` / `in-progress`）が 0 件であること。
* **統合ブランチ側（マージ後実行時）**：対象チケットがすでに統合ブランチへマージされ、`status: done`（または `cancelled`）であること。

## 手順

### 1. 作業ブランチ側（クロージング準備）

1. `update_changed_files.py` を実行し、`index.md` の `## 変更ファイル` を統合ブランチとの差分から更新する。
   ```bash
   uv run <管理ルート>/scripts/update_changed_files.py --ticket <チケットID> --json
   ```
2. AC ごとの検証結果・根拠および関連記録・ADR への導線を実物照合し、`index.md` の `## DoD（完了の定義）` へ記録する（実物照合チェックは推奨ワーカー `worker-low` または `worker-middle` へ委譲可）。  
   サブエージェントワーカーへ委譲する際は、親セッションの会話履歴が引き継がれない前提で、必ず以下の5項目をプロンプトへ明示する。
1. 参照する手順書・スキルパス
2. 対象範囲（ファイル・調査対象・比較基点コミット等）
3. 入力条件・制約（前提条件・対象外・守るべき規約）
4. 変更可否（読み取り専用か、許可する編集範囲はどこか）
5. 期待する成果と報告形式（出力先パス・実行環境・未確認事項を含む）
3. 未検証項目がある場合は「受け入れて完了とするか、検証を引き継ぐか」を人間へ確認し、判断結果と追跡先リンクを DoD へ記録する。親チケットの場合は子チケットの結果を参照して親自身の AC を確認する。
4. 人間の完了承認を得たうえで、`update_frontmatter.py` により `status: done`・`phase: closing`・`phase_status: done` へ更新し、`## 現在地` を完了状態へ更新する。
   ```bash
   uv run <管理ルート>/scripts/update_frontmatter.py --file <チケットindex.md> --set status=done --set phase=closing --set phase_status=done --json
   ```
5. ユーザーへコミットおよび統合ブランチへの反映（push・PR/MR またはローカルマージ。PR/MR 文面作成には `aico-ticket-pr` を案内）を提示する。

### 2. 統合ブランチ側（マージ後の一覧再生成）

1. CI/CD パイプラインで自動実行していない場合、統合ブランチ上で `rebuild_indexes.py` を実行して一覧およびダッシュボードを再生成する。
   ```bash
   uv run <管理ルート>/scripts/rebuild_indexes.py --json
   ```

## 完了条件と状態更新

* 作業ブランチ側：`## 変更ファイル`・`## DoD` が整備され、`status: done` / `phase: closing` / `phase_status: done` が確定していること。
* 統合ブランチ側：マージ後の一覧・ダッシュボードが再生成されていること。

## 報告形式

* 変更ファイル数
* AC 別 DoD 判定結果と未検証項目の人間判断結果
* 統合・push/PR 案内（作業ブランチ側）または一覧再生成結果（統合ブランチ側）
