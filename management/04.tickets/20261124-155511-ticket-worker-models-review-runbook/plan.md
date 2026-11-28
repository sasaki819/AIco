# 作業計画

## 合意した仕様

### 1. 成果物と配置先

* **Runbook 手順書**：`management/05.runbooks/review-worker-models/runbook.md`
* **生成方式**：作業ブランチ上で `uv run management/scripts/create_runbook.py --slug review-worker-models --title "worker_models おすすめ設定見直し手順" --allow-non-integration --json` を実行してひな形を生成し、`management/templates/runbook.md`・`aico-create-runbook`・`aico-markdown-write` の規約に沿って本文を作成する。
* **メタデータ・構造**：
  * Frontmatter は `id`（`review-worker-models`）・`title`・`created`・`updated` とし、`status` キーは持たない。
  * 必須 7 セクション（`## 概要`・`## 前提条件`・`## 入力`・`## 手順`・`## 完了条件`・`## 異常時の対応`・`## 改訂履歴`）を備える。

### 2. Runbook 本文に含める手順・制約

1. **公開リポジトリ・GitHub ミラーの境界ルール（AC3）**
   * AIco リポジトリは GitHub 公開リポジトリへミラーされる前提を明記する。
   * 手元のベンチマーク比較資料（個人リポジトリや再配布不可の外部ベンチマーク生データ等）はメンテナ内部の選定判断の参考にとどめる。
   * Runbook 本文・Runbook 実施記録（`management/05.runbooks/review-worker-models/records/<実施記録ID>/`）・公開ドキュメントには、**非公開リポジトリ URL および再配布不可のベンチマーク生数値を一切記載しない**。
   * 記録してよい情報は、選定したモデル ID・`effort` 値・定性的な選定理由・各ツール公式確認手段による動作確認結果に限定する。
2. **対象 4 ツールの最新モデル・`effort` 仕様確認（AC2）**
   * `template/management/scripts/_lib/agents_sync.py`（および `template/management/scripts/_lib/manifest.py`）と `docs/04.user-guide/05.worker-models.md` の仕様に合わせ、4 ツールごとに確認対象・確認方法・注意点を明記する。
     * **Claude Code**（`.claude/agents/worker-{level}.md`）：`model`＋`effort`。公式エイリアス（`opus` / `sonnet` / `haiku`）または明示 ID。セッション内 `/model` および公式ドキュメントで確認。
     * **Codex**（`.codex/agents/worker-{level}.toml`）：`model`＋`model_reasoning_effort`。`codex debug models` および公式ドキュメントで確認。
     * **Antigravity**（`.agents/agents/worker-{level}.md`）：抽象ティアのみ（`pro` / `flash` / `flash_lite` / `inherit`）、`effort` は未使用（`""`）。公式仕様・現行アダプタ仕様で確認。
     * **GitHub Copilot（VS Code）**（`.github/agents/worker-{level}.agent.md`）：`model`＋`reasoning-effort`。VS Code で `.github/agents/worker-high.agent.md` の `model:` 行にて Ctrl+Space 補完および公式ドキュメントで確認。
   * ツール側のフロントマター仕様変更等により `template/management/scripts/_lib/agents_sync.py` 等のコード改修が必要と判明した場合は、Runbook 内で直接コードを改造せず別チケットを起票して引き継ぐ分岐を明記する。
3. **ガイド更新・同期と最終確認日の反映（AC2）**
   * `docs/04.user-guide/05.worker-models.md` と配布コピー `template/management/01.manual/05.worker-models.md` を完全一致で更新する（一覧表・JSON コピペ例・補足説明、`最終確認日：YYYY-MM-DD` および見出し `## ツール別おすすめ設定（YYYY-MM-DD 時点）` を整合更新し、既存の敬体文体を維持する）。
   * AIco 本体ルートの `management/01.manual/05.worker-models.md` はリリース時の自己適用（`tools/aico.sh update --source .`）で更新される領域であり、本 Runbook で直接手動編集しない旨を注記する。
   * 調査の結果「現行設定を維持」と判断した場合の扱い（最終確認日のみ更新するか変更なしとするかを人間承認で決定し、実施記録に根拠を残す）も明記する。
4. **自動テストおよび `doctor` 検証（AC2）**
   * `uv run -m unittest discover -s tests -v`（特に `tests/test_user_guide.py` による完全一致同期・文字コード/LF・禁止語・Markdown 規約・リンク検証）を実行し全件通過を確認する。
   * 一覧再生成前の中間確認では `tools/aico.sh doctor` で `ERROR=0`（および鮮度ドリフト以外の警告なし）を確認し、手順 7 の `rebuild_indexes.py` 実行後に `tools/aico.sh doctor --strict` で `ERROR=0 / WARN=0` を最終確認する。
5. **AIco 本体 `management/aico-manifest.json` への任意反映確認（AC2）**
   * AIco 自身の運用設定（`management/aico-manifest.json` の `worker_models`）も今回のおすすめ設定へ反映するかを人間に確認する。
   * 反映する場合は `management/aico-manifest.json` を更新し、`tools/aico.sh sync_agents` および `tools/aico.sh doctor`（最終確認は手順 7 の `doctor --strict`）でワーカー定義反映と整合を確認する。
6. **実施記録とコミット境界**
   * Runbook 実施は `aico-runbook-run` に従って統合ブランチ（`main`）上で記録を残し、公開境界チェック（非公開 URL・生ベンチマーク数値が差分に含まれないことの確認）を経て人間承認後にコミットする。

### 3. ブランチ運用と一覧再生成の境界（AC4）

* 作業ブランチ（`feature/20261124-155511-ticket-worker-models-review-runbook`）上では、`management/05.runbooks/index.md` および `management/index.md` を編集・再生成しない（AIco のブランチ別一覧更新規約に従う）。
* `main` 統合後の `aico-ticket-close`（統合ブランチ側）で `rebuild_indexes.py` を実行し、`management/05.runbooks/index.md` および `management/index.md` を再生成して AC4 を最終充足させる。

### 4. 対象外（スコープ外）

* 本チケットでは作成した Runbook の実実施（`/aico-runbook-run review-worker-models`）を行わない。
* `docs/04.user-guide/05.worker-models.md`・`template/management/01.manual/05.worker-models.md` の内容更新、および `management/aico-manifest.json` の `worker_models` 実値更新は行わない。
* `template/` 配下のスクリプト・スキル・システム設計書（`docs/03.spec/`）の変更は行わない。

## ステップ一覧

* [x] Step 1：`uv run management/scripts/create_runbook.py --slug review-worker-models --title "worker_models おすすめ設定見直し手順" --allow-non-integration --json` を実行し、`management/05.runbooks/review-worker-models/runbook.md` のひな形を生成する
* [x] Step 2：合意仕様・AC1〜AC3・`aico-create-runbook`・`aico-markdown-write` に従い、`management/05.runbooks/review-worker-models/runbook.md` の本文を執筆する
* [x] Step 3：`uv run -m unittest discover -s tests -v` および `uv run management/scripts/doctor.py --json` で検証し、`aico-review` による独立レビューを実施する
* [x] Step 4：レビュー対応完了後、作業ブランチ側クローズ（`update_changed_files.py`・DoD 整理・コミット）→ `main` 統合 → 統合ブランチ側一覧再生成（`management/05.runbooks/index.md`・`management/index.md`）→ `doctor.py --strict`（`OK=9 / WARN=0 / ERROR=0`）確認をもって AC4 を完了する

## 検証方針

* **文書・規約検証**：`management/05.runbooks/review-worker-models/runbook.md` について、UTF-8（BOM なし）・LF・常体・禁止語なし・必須 7 セクション完備・`status` キーなし・非公開 URL および再配布不可ベンチマーク生数値の混入なしを実物照合する。
* **自動テスト・診断**：
  * `uv run -m unittest discover -s tests -v`（全テスト通過・回帰なし）
  * 作業ブランチ上：`uv run management/scripts/doctor.py --json`（`ERROR=0` であること。`index-freshness` 警告は `main` 統合後の一覧再生成で解消する予定）
  * `main` 統合後：`uv run management/scripts/doctor.py --strict --json`（`OK=9 / WARN=0 / ERROR=0`）
* **独立レビュー**：`aico-review` で独立コンテキストのワーカーへ委譲し、4 ツール仕様との整合・公開境界・実運用手順の抜け漏れ・AIco 規約準拠を検証する。
* **対象環境**：AIco 本体リポジトリ（Linux / `uv` 環境）。

## 判断ログ

* **2026-11-28（対象ファイルパスの補正）**：起票時の記載 `worker-models.md` は先行チケット完了後の実ファイル名 `05.worker-models.md`（`docs/04.user-guide/05.worker-models.md` および `template/management/01.manual/05.worker-models.md`）へ整合させた。
* **2026-11-28（`create_runbook.py` の `--allow-non-integration` 利用と一覧再生成タイミング）**：本チケットは作業ブランチで進行するため、`runbook.md` は作業ブランチ上で `--allow-non-integration` により生成し、`management/05.runbooks/index.md`・`management/index.md` の再生成（AC4）は `main` 統合後に実施する。
* **2026-11-28（`design` フェーズのスキップ）**：システム設計書や配布コードの変更を伴わない Runbook 新設のため、計画承認後は `design` をスキップして `implementation` へ進む方針とした。
