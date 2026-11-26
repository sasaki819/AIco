# 作業計画

## 合意した仕様

発端チケット（`20261124-155511-ticket-onboarding-docs-and-cli-ux`）のドッグフーディング課題および比較評価チケット（`20261124-234050-ticket-evaluate-ai-dev-standard-comparison`）で採択された A-1〜A-4・B-1〜B-3、ならびに未決事項 Q1〜Q3 の人間合意（2026-11-25）にもとづき、以下 5 領域を一貫して整備する。  
※AIco 本体運営領域（ルート直下の `AGENTS.md`・`.agents/`・`management/scripts/`・`management/01.manual/` 等）はリリース前の `tools/aico.sh update --source .` で自己適用する分離原則に従い、本作業ブランチ内では直接改造しない。

### 1. レビューフローと状態遷移の整備（A-1・Q1）

* `create_review_finding.py` に `--status {open,in-progress}`（既定：`open`）を追加し、人間レビュー指摘を最初から採用済み（`in-progress`）で起票できるようにする。
* `validation.py` の `validate_transition()` を拡張し、以下を `--force` 不要の正規遷移とする。
  * 同一フェーズ内：`working -> fixing`、`reviewing -> fixing`、`re-reviewing -> reviewing`（同一フェーズ内での複数ラウンドレビュー）。
  * フェーズ間：`planning -> closing`（調査・評価専用チケットでの設計・実装スキップ）。
* `template/.agents/skills/aico-review/SKILL.md` を拡張し、既存 21 スキル構成を維持したまま「人間レビュー指摘の記録モード（`--reviewer human --status in-progress` → `fixing` へ直接遷移し `aico-review-fix` を案内、記録のみ希望時は `--status open` → `triaging`）」および同一フェーズ次ラウンド実施手順を追加する。
* `template/.agents/skills/aico-review-recheck/SKILL.md` に、人間指摘ラウンド解消後に人間確認完了または独立 AI による次ラウンドレビュー（`aico-review`）へ進める導線を明記する。

### 2. クローズ手順の UX 改善と DoD 明示化（Q2・B-3）

* `git_utils.py` の `get_diff_name_status()` に `include_uncommitted: bool = True` を追加し、既定では `merge-base` からの作業ツリー差分（ステージ済み・未ステージ）および `.gitignore` 準拠の未追跡ファイル（`A` 扱い）を統合して `<management_root>/` 除外で抽出する（`include_uncommitted=False` 時は従来の `base...HEAD` コミット済み差分のみ）。
* `update_changed_files.py` は既定で未コミット変更も取り込んで `status: "ok"` で更新し（`data.includes_uncommitted` に真偽値を格納）、旧来挙動が必要な場合に備えて `--committed-only` オプションを設ける。
* `template/management/templates/ticket-index.md` の `## DoD（完了の定義）` および `template/.agents/skills/aico-ticket-close/SKILL.md` を更新し、①「プロジェクト側設計書・仕様書の更新確認（不要時は理由）」、②「ADR の要否判断（不要時は理由）」、③事前仮コミット不要で完了確定後に 1 回コミットできる手順を明示する。

### 3. AI 進行案内・選択肢提示ルールおよび行動ガードレール整備（A-3）

* `template/AGENTS.md` に以下 2 原則を追加する。
  * **進行案内と選択肢提示の原則**：工程完了・人間承認待ち・判断委譲時はオープンな質問だけで終わらず、推奨案を先頭に置いた 2〜4 件の具体的な番号付き選択肢を通常の Markdown リストで提示する（独自タグ内に隠さない）。
  * **行動ガードレール**：①作業中に見つけたスコープ外の課題はその場で直さず別チケット起票を提案する、②検証成功前に完了報告・チェックをせずテスト削除／無効化で通さない、③作業開始時は対象チケット等必要最小限の記録だけを読み込む。
* 節目となる主要スキル（`aico-create-ticket`・`aico-ticket-status`・`aico-ticket-plan`・`aico-ticket-implement`・`aico-review`・`aico-review-triage`・`aico-review-fix`・`aico-review-recheck`・`aico-ticket-close`）の `## 手順`・`## 報告形式` を上記原則と整合させる。

### 4. 任意 `pr_template`・`aico-ticket-pr` 改善・任意 CI ガイド（A-2）

* `template/management/aico-manifest.json` へ任意キー `"pr_template": ""` を追加する（`schema_version: 1` 維持、`manifest.py` では未指定でもエラーにしない後方互換設計。非空時は絶対パス・`..` 参照を拒否）。
* `template/management/templates/pr-template.md`（AIco 推奨 PR/MR テンプレート雛形）を新設する。
* `template/management/scripts/init.py` に対話入力（初回既定 `""`・GitHub / GitLab / Azure DevOps の代表例とスキップ案内付き）および非対話引数 `--pr-template` を追加する。非空パス指定時、ファイル未存在なら `<管理ルート>/templates/pr-template.md` をコピー配置し、既存ファイルがあれば上書きせず保持する。配置後ファイルはプロジェクト所有とし `upgrade.py` / `update.py` では触らない。
* `template/.agents/skills/aico-ticket-pr/SKILL.md` を更新し、①完全オプショナル（複数テンプレート運用等で未使用でも全ワークフロー完結）、②テンプレート参照優先順（ユーザー明示指定 → `aico-manifest.json` の `pr_template` → AIco 標準構成）、③事実未確認のチェック項目へチェックを入れない規約を明記する。

### 5. `doctor.py` 品質ゲート強化（A-4・Q3）およびユーザーガイド同期（B-1・B-2・A-2）

* `template/management/scripts/doctor.py` に以下 3 検査を追加する。
  * `status: done` チケットの `## AC（受け入れ条件）` 内に未チェック項目（`- [ ]` / `* [ ]`）が残っている場合は `ERROR`。
  * `status: cancelled` のレビュー指摘（チケット・Runbook 実施記録）で `## 採否判断（人間選別）` に実質記述がない（空行・HTML コメントのみ）場合は `ERROR`。
  * `aico-manifest.json` の `pr_template` が非空かつ実ファイル不在の場合は `WARN`（未設定・`""` は `OK`）。
* `docs/04.user-guide/` および `template/management/01.manual/`（完全一致同期）を更新し、①`init` の任意 `pr_template` と Windows 混在環境向け `.gitattributes`（`eol=lf`）任意推奨案内（B-1）、②人間レビュー記録・1 コミットクローズ・`aico-ticket-pr` 任意利用、③並列運用・`git worktree` 実践ノウハウ（B-2）、④GitHub Actions / GitLab CI 向け `doctor.py` 任意スニペットと判断基準（A-2）を反映する。
* 仕様書群（`docs/03.spec/01`, `02`, `03`, `05`, `06`, `07`, `08`）を上記変更と整合更新する。

## ステップ一覧

* [x] 1. 仕様書群（`docs/03.spec/01`, `02`, `03`, `05`, `06`, `07`, `08`）を合意仕様に沿って更新する
* [x] 2. テンプレート・スクリプト基盤（`aico-manifest.json`・`pr-template.md`・`ticket-index.md`・`manifest.py`・`validation.py`・`git_utils.py`）を実装する
* [x] 3. 各コマンドスクリプト（`create_review_finding.py`・`update_changed_files.py`・`init.py`・`doctor.py`）を実装する
* [x] 4. `template/AGENTS.md` および主要 `template/.agents/skills/*/SKILL.md` を更新する
* [x] 5. `docs/04.user-guide/` を更新し `template/management/01.manual/` へ完全一致同期する
* [x] 6. 自動テスト（`tests/test_lib.py`・`test_daily_scripts.py`・`test_lifecycle.py`・`test_user_guide.py`）を追加・更新し、全件通過および `doctor.py`・Markdown 品質規約を検証する

## 検証方針

* **自動テスト**：`python3 -m unittest discover -s tests -v` を実行し、既存 30 件＋新規追加ケース（状態遷移拡張・`--status in-progress`・`update_changed_files.py` 未コミット統合＆`--committed-only`・`init.py --pr-template` 配置／非上書き／`upgrade` 非破壊・`doctor.py` の `done` 未チェック AC ERROR / `cancelled` 理由空欄 ERROR / `pr_template` 欠落 WARN・ユーザーガイド完全一致）が全件通過することを確認する。
* **統合診断**：`uv run management/scripts/doctor.py --json` が `ERROR=0`・`WARN=0` で通過することを確認する。
* **独立レビュー**：実装完了後、`aico-review` で独立コンテキストワーカーによるコード・仕様・Markdown 規約レビューを実施し、指摘解消まで完了させる。

## 判断ログ

* 2026-11-25（Q1）：スキル数増加による初見ユーザーの認知負荷を避けるため、21 スキル構成を維持して `aico-review` の人間レビューモード拡張＋`create_review_finding.py --status in-progress` を採用した。
* 2026-11-25（Q2）：クローズ時の仮コミット＋`--amend` の摩擦を根本解消するため、`update_changed_files.py` は既定で作業ツリーの未コミット変更（未追跡ファイル含む）を統合し、必要時のみ `--committed-only` で絞り込む設計とした。
* 2026-11-25（Q3）：`status: done` での未チェック AC および `status: cancelled` 指摘の理由空欄は DoD・監査証跡の欠落であるため `ERROR` とし、`pr_template` の実ファイル不在のみ運用中のリネーム等があり得るため `WARN` とした。
