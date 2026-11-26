---
id: 20261124-231830-ticket-workflow-review-and-ux-improvements
title: レビューフロー・クローズ手順・AI 進行案内の UX 改善
status: done
created: 2026-11-24 23:18:30
updated: 2026-11-26 08:58:57
phase: closing
phase_status: done
branch: feature/20261124-231830-ticket-workflow-review-and-ux-improvements
parent: null
children: []
discussions: []
adrs: []
---

# レビューフロー・クローズ手順・AI 進行案内の UX 改善

## 概要

初回チケットのドッグフーディング運用（`20261124-155511-ticket-onboarding-docs-and-cli-ux`）で検知した実運用上の課題、および `ai-dev-standard`・`jotline` との比較評価（`20261124-234050-ticket-evaluate-ai-dev-standard-comparison`）で採用合意した実践知（A-1〜A-4・B-1〜B-3）を一貫して AIco へ取り込み、日常運用の摩擦を減らして誘導性と品質ゲートを強化する。  
対象は次の 5 領域である。

1. **レビューフロー・状態遷移の整備（A-1 含む）**：人間が任意のタイミングでレビュー指摘を登録・即採用（`in-progress`）して対応できる正規手順、同一フェーズ内の複数ラウンドレビュー遷移（`re-reviewing` → `reviewing`）、および調査・評価専用チケット等の `planning` → `closing` 遷移の正規化。
2. **クローズ手順・DoD の UX 改善（B-3 含む）**：作業ブランチ上のクローズ準備時に事前コミット＋`amend` を強制せず変更ファイル一覧を更新できる `update_changed_files.py` の改善、および DoD における「プロジェクト側システム設計書の更新確認・ADR 要否判断（不要理由含む）」の明示化。
3. **AI 進行案内・行動ガードレールの整備（A-3 含む）**：`template/AGENTS.md` および主要スキルに対し、①工程完了・人間承認待ち時の具体的な番号付き選択肢による進行先導ルール、②具体的行動ガードレール（スコープ外課題はその場で直さず起票提案・検証成功前の完了報告やテスト無効化の禁止・最小コンテキスト読み込み原則）を明文化する。
4. **任意 `pr_template` 対応・`aico-ticket-pr` 改善・任意 CI ガイド（A-2）**：ホスティング区分を持たず `aico-manifest.json` へ任意キー `pr_template`（相対パス・既定 `""`、後方互換維持）を追加し、`init.py` で未存在時のみ推奨雛形を配置（既存時は上書き禁止・配置後は導入先所有）。`aico-ticket-pr` は明示指定 → `pr_template` → 標準構成の順で尊重し、複数テンプレート運用など `aico-ticket-pr` 非利用プロジェクトでも完全運用可能なオプショナル位置づけを保証する。あわせてユーザーガイドへ GitHub Actions / GitLab CI 向け `doctor.py` 任意スニペットと判断基準を掲載する。
5. **`doctor.py` 品質ゲート強化とユーザーガイド実践知見追記（A-4・B-1・B-2）**：`doctor.py` へ `status: done` チケットの未チェック AC 検知・見送り指摘（`status: cancelled`）の理由空欄検知・`pr_template` 指定先欠落 WARN を追加し、ユーザーガイドへ Windows 向け `.gitattributes` 任意推奨設定（B-1）と並列運用・`git worktree` 実践ノウハウ（B-2）を追記する。

## AC（受け入れ条件）

* [x] **人間レビュー入口と即採用フロー（A-1）**：人間がレビュー指摘を登録・記録する正規の手順またはスキル（`aico-review` 拡張または専用手順・スクリプト引数）が仕様書（`docs/03.spec/03.workflow.md`・`06.skills.md`・`07.scripts.md`）および `template/` に整備され、人間自身の指摘は最初から採用済み（`in-progress`）で登録して即修正へ進める運用が実装されていること。
* [x] **状態遷移の正規化**：同一フェーズ内での複数ラウンドレビュー遷移（`re-reviewing` → `reviewing`）および調査専用チケット等の `planning` → `closing` 遷移が `--force` なしで許可されるよう、仕様（`03.workflow.md`）および `template/management/scripts/_lib/validation.py` が整合更新されていること。
* [x] **クローズ時の変更ファイル更新 UX と DoD 明示化（B-3）**：`template/management/scripts/update_changed_files.py`・`aico-ticket-close`・仕様書（`06.skills.md`・`07.scripts.md`）が見直され、事前コミット＋`amend` を強制せず未コミット変更（新規ファイル含む）も安全に反映できること。また `ticket-index.md`（DoD）と `aico-ticket-close` でプロジェクト側システム設計書更新確認および ADR 要否判断（不要理由含む）が明示されていること。
* [x] **AI 進行案内・行動ガードレール整備（A-3）**：`template/AGENTS.md` と節目となる主要スキル・仕様書（`05.agent-config.md`・`06.skills.md`）に、①工程完了・承認待ち時の推奨案先頭・番号付き通常 Markdown 選択肢提示ルール、②スコープ外課題分離・検証前完了／テスト無効化禁止・最小コンテキスト読み込みの行動ガードレールが明文化されていること。
* [x] **任意 `pr_template`・`aico-ticket-pr`・任意 CI ガイド（A-2）**：`aico-manifest.json`（任意キー `pr_template`、既定 `""`、`schema_version: 1` 後方互換維持）・`manifest.py`・`init.py`（未存在時のみ `<管理ルート>/templates/pr-template.md` を配置、既存ファイル非上書き、配置後は導入先所有、`--pr-template` 対応）・`aico-ticket-pr`（明示指定／`pr_template` 尊重・完全オプショナル保証）が実装・仕様化され、ユーザーガイドへ GitHub Actions / GitLab CI 向け `doctor.py` 任意スニペットと判断基準（個人運用では不要・チーム／手編集／マージ事故防止時に有効）が掲載されていること。
* [x] **`doctor.py` 品質ゲート強化（A-4）**：`template/management/scripts/doctor.py` に、①`status: done` チケットの未チェック AC（`- [ ]`）検知（未検証事項の人間承認ケースの扱いを仕様化）、②見送り指摘（`status: cancelled`）の採否判断（理由）空欄検知、③`pr_template` 設定済みかつ実ファイル欠落時の WARN（未設定時は OK）が実装されていること。
* [x] **ユーザーガイド同期と実践知見追記（B-1・B-2）**：上記変更に伴う利用手順の差分、Windows 混在環境向け `.gitattributes`（`eol=lf`）任意推奨設定、および並列運用・`git worktree` 実践ノウハウが `docs/04.user-guide/` と `template/management/01.manual/`（完全一致同期）に反映されていること。
* [x] **検証と品質規約**：変更・追加仕様を検証する自動テストが `tests/` に整備され、`python3 -m unittest discover -s tests -v` が全件通過し、変更した全 Markdown が `aico-markdown-write` 規約（UTF-8 BOM なし・LF・リンク切れなし等）を満たしていること。

## DoR（着手合意）

* **任せる範囲**：現状調査・設計案の策定（`plan.md`）、関連仕様書（`docs/03.spec/`）・ユーザーガイド（`docs/04.user-guide/`）・`template/`・`tests/` の更新およびテスト検証。なお AIco 本体運営領域（ルート直下の `AGENTS.md`・`.agents/`・`management/scripts/`・`management/01.manual/` 等）はリリース前の `tools/aico.sh update --source .` で自己適用するため作業ブランチ内で直接改造しない。
* **未決事項**：
  * 人間レビュー記録を既存 `aico-review` スキルのモード拡張にするか、専用スキル新設にするか（`plan.md` 策定時に比較提案して合意）。
  * `update_changed_files.py` の未コミット差分取り込みを既定挙動にするか、明示オプションにするか（ステージ済み・未追跡ファイルの扱いを含め `plan.md` 策定時に比較提案して合意）。
  * `doctor.py` の `status: done` 未チェック AC 検知を ERROR にするか WARN にするか（未検証事項の人間受け入れケースとの整合を含め `plan.md` 策定時に提案して合意）。
* **着手合意**：合意済み（2026-11-25）

## 現在地

* **状況**：完了確定済み（`status: done` / `phase: closing` / `phase_status: done`、AC 8 / 8 達成・変更ファイル 40 件反映済み）
* **ブロッカー（確認待ち）**：なし
* **次に取る行動**：作業ブランチの変更をコミットして `main` へ統合し、`main` 側で `rebuild_indexes.py` 実行・ローカル作業ブランチ削除・`origin/main` へ push したのち、Windows 互換性対応の引き継ぎチケットを起票する

## 変更ファイル

<!-- AICO:AUTO:BEGIN:changed-files -->

| 種別 | パス |
| :--- | :--- |
| `M` | `docs/03.spec/01.directory-and-naming.md` |
| `M` | `docs/03.spec/02.records-and-templates.md` |
| `M` | `docs/03.spec/03.workflow.md` |
| `M` | `docs/03.spec/05.agent-config.md` |
| `M` | `docs/03.spec/06.skills.md` |
| `M` | `docs/03.spec/07.scripts.md` |
| `M` | `docs/03.spec/08.adoption-and-migration.md` |
| `M` | `docs/04.user-guide/01.getting-started.md` |
| `M` | `docs/04.user-guide/02.tutorial.md` |
| `M` | `docs/04.user-guide/03.cheatsheet.md` |
| `M` | `docs/04.user-guide/04.user-guide.md` |
| `M` | `template/.agents/skills/aico-create-ticket/SKILL.md` |
| `M` | `template/.agents/skills/aico-review-fix/SKILL.md` |
| `M` | `template/.agents/skills/aico-review-recheck/SKILL.md` |
| `M` | `template/.agents/skills/aico-review-triage/SKILL.md` |
| `M` | `template/.agents/skills/aico-review/SKILL.md` |
| `M` | `template/.agents/skills/aico-ticket-close/SKILL.md` |
| `M` | `template/.agents/skills/aico-ticket-implement/SKILL.md` |
| `M` | `template/.agents/skills/aico-ticket-plan/SKILL.md` |
| `M` | `template/.agents/skills/aico-ticket-pr/SKILL.md` |
| `M` | `template/.agents/skills/aico-ticket-status/SKILL.md` |
| `M` | `template/AGENTS.md` |
| `M` | `template/management/01.manual/01.getting-started.md` |
| `M` | `template/management/01.manual/02.tutorial.md` |
| `M` | `template/management/01.manual/03.cheatsheet.md` |
| `M` | `template/management/01.manual/04.user-guide.md` |
| `M` | `template/management/aico-manifest.json` |
| `M` | `template/management/scripts/_lib/git_utils.py` |
| `M` | `template/management/scripts/_lib/manifest.py` |
| `M` | `template/management/scripts/_lib/validation.py` |
| `M` | `template/management/scripts/create_review_finding.py` |
| `M` | `template/management/scripts/doctor.py` |
| `M` | `template/management/scripts/init.py` |
| `M` | `template/management/scripts/update_changed_files.py` |
| `A` | `template/management/templates/pr-template.md` |
| `M` | `template/management/templates/ticket-index.md` |
| `M` | `tests/test_daily_scripts.py` |
| `M` | `tests/test_lib.py` |
| `M` | `tests/test_lifecycle.py` |
| `M` | `tests/test_user_guide.py` |

<!-- AICO:AUTO:END:changed-files -->

## DoD（完了の定義）

* **AC 検証結果と根拠**：全 8 件達成（実物照合・自動テスト 33/33 OK・`doctor.py` OK=9/WARN=0/ERROR=0・独立レビュー round1 指摘 5/5 件解消）。
  * **AC-1（人間レビュー入口・即採用フロー）**：`create_review_finding.py` の `--status {open,in-progress}`、`aico-review/SKILL.md` の人間レビュー記録モード拡張、`aico-review-recheck/SKILL.md` の次ラウンド導線、`docs/03.spec/03,06,07` 更新および `tests/test_daily_scripts.py`（`test_human_review_status_and_doctor_quality_gates`）通過で確認。
  * **AC-2（状態遷移の正規化）**：`validation.py` の `working -> fixing`・`reviewing -> fixing`・`re-reviewing -> reviewing`・`planning -> closing` の `--force` 不要遷移、`docs/03.spec/03,06,07` 更新および `tests/test_lib.py`（`test_transitions_and_force`）通過で確認。
  * **AC-3（クローズ時変更ファイル更新 UX・DoD 明示化）**：`git_utils.py`・`update_changed_files.py` の既定未コミット統合＆`--committed-only`、`ticket-index.md`・`aico-ticket-close/SKILL.md` の設計書更新確認・ADR 要否判断明示化および `tests/test_daily_scripts.py` 通過で確認。
  * **AC-4（AI 進行案内・行動ガードレール整備）**：`template/AGENTS.md`・主要スキル 10 件・`docs/03.spec/05,06` への選択肢提示ルールおよび 3 ガードレール明文化で確認。
  * **AC-5（任意 `pr_template`・`aico-ticket-pr`・任意 CI ガイド）**：`aico-manifest.json`・`manifest.py`・`pr-template.md`・`init.py`（`--pr-template`・非上書き・境界検証）・`aico-ticket-pr/SKILL.md`・ユーザーガイド CI スニペット＆判断基準および `tests/test_lifecycle.py`・`tests/test_user_guide.py` 通過で確認。
  * **AC-6（`doctor.py` 品質ゲート強化）**：`doctor.py` の `done` 未チェック AC ERROR・`cancelled` 理由空欄 ERROR・`pr_template` 不在 WARN／外部シンボリックリンク ERROR および `tests/test_daily_scripts.py`（3 バッククォート閉じフェンス回帰テスト含む）通過で確認。
  * **AC-7（ユーザーガイド同期・実践知見追記）**：`docs/04.user-guide/` と `template/management/01.manual/` の完全一致同期、`.gitattributes`（`eol=lf`）任意案内および並列運用・`git worktree` 実践知見反映を `tests/test_user_guide.py` 通過で確認。
  * **AC-8（検証と品質規約）**：`python3 -m unittest discover -s tests -v`（33/33 OK）、`uv run management/scripts/doctor.py --json`（OK=9/WARN=0/ERROR=0）、変更 Markdown 全 36 ファイルの UTF-8（BOM なし）・LF 検証（問題 0 件）で確認。
* **プロジェクト側設計書・仕様書の更新確認**：更新済み（`docs/03.spec/01,02,03,05,06,07,08` および `docs/04.user-guide/01,02,03,04` を本チケットの合意仕様と整合更新）。
* **ADR の要否判断**：不要（Q1〜Q3 の設計判断は既存仕様体系の拡張であり `plan.md` 判断ログと `docs/03.spec/` 仕様書群へ反映済みのため新規 ADR 作成・既存 ADR 置換なし）。
* **未検証項目と人の判断結果**：Windows 実機でのシンボリックリンク境界検査・改行挙動および Windows PowerShell 実機検証で判明した既存課題（リポジトリ `.gitattributes` 不在による CRLF 展開・テストの `bash` 直接呼び出し）は、`main` 統合後に専用チケットを起票して引き継ぐ前提で完了承認済み（2026-11-26）。
* **関連記録・ADR への導線確認**：発端チケット（`20261124-155511`）・比較評価チケット（`20261124-234050`）・比較評価レポートへの相対リンク有効を `doctor.py` で確認済み。

## 親子チケット・関連

* [発端チケット：初見ユーザー向けガイド整備と導入・初期設定ツール UX 改善](../20261124-155511-ticket-onboarding-docs-and-cli-ux/index.md)
* [比較評価チケット：ai-dev-standard との比較評価および優位要素の取り込み検討](../20261124-234050-ticket-evaluate-ai-dev-standard-comparison/index.md)
* [比較評価レポート（A-1〜A-4・B-1〜B-3 の根拠・詳細）](../20261124-234050-ticket-evaluate-ai-dev-standard-comparison/notes/001-comparison-evaluation.md)
