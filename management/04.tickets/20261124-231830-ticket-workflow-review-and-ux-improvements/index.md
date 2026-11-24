---
id: 20261124-231830-ticket-workflow-review-and-ux-improvements
title: レビューフロー・クローズ手順・AI 進行案内の UX 改善
status: open
created: 2026-11-24 23:18:30
updated: 2026-11-25 00:31:30
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

初回チケットのドッグフーディング運用（`20261124-155511-ticket-onboarding-docs-and-cli-ux`）で検知した実運用上の課題、および `ai-dev-standard`・`jotline` との比較評価（`20261124-234050-ticket-evaluate-ai-dev-standard-comparison`）で採用合意した実践知（A-1〜A-4・B-1〜B-3）を一貫して AIco へ取り込み、日常運用の摩擦を減らして誘導性と品質ゲートを強化する。  
対象は次の 5 領域である。

1. **レビューフロー・状態遷移の整備（A-1 含む）**：人間が任意のタイミングでレビュー指摘を登録・即採用（`in-progress`）して対応できる正規手順、同一フェーズ内の複数ラウンドレビュー遷移（`re-reviewing` → `reviewing`）、および調査・評価専用チケット等の `planning` → `closing` 遷移の正規化。
2. **クローズ手順・DoD の UX 改善（B-3 含む）**：作業ブランチ上のクローズ準備時に事前コミット＋`amend` を強制せず変更ファイル一覧を更新できる `update_changed_files.py` の改善、および DoD における「プロジェクト側システム設計書の更新確認・ADR 要否判断（不要理由含む）」の明示化。
3. **AI 進行案内・行動ガードレールの整備（A-3 含む）**：`template/AGENTS.md` および主要スキルに対し、①工程完了・人間承認待ち時の具体的な番号付き選択肢による進行先導ルール、②具体的行動ガードレール（スコープ外課題はその場で直さず起票提案・検証成功前の完了報告やテスト無効化の禁止・最小コンテキスト読み込み原則）を明文化する。
4. **任意 `pr_template` 対応・`aico-ticket-pr` 改善・任意 CI ガイド（A-2）**：ホスティング区分を持たず `aico-manifest.json` へ任意キー `pr_template`（相対パス・既定 `""`、後方互換維持）を追加し、`init.py` で未存在時のみ推奨雛形を配置（既存時は上書き禁止・配置後は導入先所有）。`aico-ticket-pr` は明示指定 → `pr_template` → 標準構成の順で尊重し、複数テンプレート運用など `aico-ticket-pr` 非利用プロジェクトでも完全運用可能なオプショナル位置づけを保証する。あわせてユーザーガイドへ GitHub Actions / GitLab CI 向け `doctor.py` 任意スニペットと判断基準を掲載する。
5. **`doctor.py` 品質ゲート強化とユーザーガイド実践知見追記（A-4・B-1・B-2）**：`doctor.py` へ `status: done` チケットの未チェック AC 検知・見送り指摘（`status: cancelled`）の理由空欄検知・`pr_template` 指定先欠落 WARN を追加し、ユーザーガイドへ Windows 向け `.gitattributes` 任意推奨設定（B-1）と並列運用・`git worktree` 実践ノウハウ（B-2）を追記する。

## AC（受け入れ条件）

* [ ] **人間レビュー入口と即採用フロー（A-1）**：人間がレビュー指摘を登録・記録する正規の手順またはスキル（`aico-review` 拡張または専用手順・スクリプト引数）が仕様書（`docs/03.spec/03.workflow.md`・`06.skills.md`・`07.scripts.md`）および `template/` に整備され、人間自身の指摘は最初から採用済み（`in-progress`）で登録して即修正へ進める運用が実装されていること。
* [ ] **状態遷移の正規化**：同一フェーズ内での複数ラウンドレビュー遷移（`re-reviewing` → `reviewing`）および調査専用チケット等の `planning` → `closing` 遷移が `--force` なしで許可されるよう、仕様（`03.workflow.md`）および `template/management/scripts/_lib/validation.py` が整合更新されていること。
* [ ] **クローズ時の変更ファイル更新 UX と DoD 明示化（B-3）**：`template/management/scripts/update_changed_files.py`・`aico-ticket-close`・仕様書（`06.skills.md`・`07.scripts.md`）が見直され、事前コミット＋`amend` を強制せず未コミット変更（新規ファイル含む）も安全に反映できること。また `ticket-index.md`（DoD）と `aico-ticket-close` でプロジェクト側システム設計書更新確認および ADR 要否判断（不要理由含む）が明示されていること。
* [ ] **AI 進行案内・行動ガードレール整備（A-3）**：`template/AGENTS.md` と節目となる主要スキル・仕様書（`05.agent-config.md`・`06.skills.md`）に、①工程完了・承認待ち時の推奨案先頭・番号付き通常 Markdown 選択肢提示ルール、②スコープ外課題分離・検証前完了／テスト無効化禁止・最小コンテキスト読み込みの行動ガードレールが明文化されていること。
* [ ] **任意 `pr_template`・`aico-ticket-pr`・任意 CI ガイド（A-2）**：`aico-manifest.json`（任意キー `pr_template`、既定 `""`、`schema_version: 1` 後方互換維持）・`manifest.py`・`init.py`（未存在時のみ `<管理ルート>/templates/pr-template.md` を配置、既存ファイル非上書き、配置後は導入先所有、`--pr-template` 対応）・`aico-ticket-pr`（明示指定／`pr_template` 尊重・完全オプショナル保証）が実装・仕様化され、ユーザーガイドへ GitHub Actions / GitLab CI 向け `doctor.py` 任意スニペットと判断基準（個人運用では不要・チーム／手編集／マージ事故防止時に有効）が掲載されていること。
* [ ] **`doctor.py` 品質ゲート強化（A-4）**：`template/management/scripts/doctor.py` に、①`status: done` チケットの未チェック AC（`- [ ]`）検知（未検証事項の人間承認ケースの扱いを仕様化）、②見送り指摘（`status: cancelled`）の採否判断（理由）空欄検知、③`pr_template` 設定済みかつ実ファイル欠落時の WARN（未設定時は OK）が実装されていること。
* [ ] **ユーザーガイド同期と実践知見追記（B-1・B-2）**：上記変更に伴う利用手順の差分、Windows 混在環境向け `.gitattributes`（`eol=lf`）任意推奨設定、および並列運用・`git worktree` 実践ノウハウが `docs/04.user-guide/` と `template/management/01.manual/`（完全一致同期）に反映されていること。
* [ ] **検証と品質規約**：変更・追加仕様を検証する自動テストが `tests/` に整備され、`python3 -m unittest discover -s tests -v` が全件通過し、変更した全 Markdown が `aico-markdown-write` 規約（UTF-8 BOM なし・LF・リンク切れなし等）を満たしていること。

## DoR（着手合意）

* **任せる範囲**：現状調査・設計案の策定（`plan.md`）、関連仕様書（`docs/03.spec/`）・ユーザーガイド（`docs/04.user-guide/`）・`template/`・`tests/` の更新およびテスト検証。なお AIco 本体運営領域（ルート直下の `AGENTS.md`・`.agents/`・`management/scripts/`・`management/01.manual/` 等）はリリース前の `tools/aico.sh update --source .` で自己適用するため作業ブランチ内で直接改造しない。
* **未決事項**：
  * 人間レビュー記録を既存 `aico-review` スキルのモード拡張にするか、専用スキル新設にするか（`plan.md` 策定時に比較提案して合意）。
  * `update_changed_files.py` の未コミット差分取り込みを既定挙動にするか、明示オプションにするか（ステージ済み・未追跡ファイルの扱いを含め `plan.md` 策定時に比較提案して合意）。
  * `doctor.py` の `status: done` 未チェック AC 検知を ERROR にするか WARN にするか（未検証事項の人間受け入れケースとの整合を含め `plan.md` 策定時に提案して合意）。
* **着手合意**：未合意

## 現在地

* **状況**：起票完了（`ai-dev-standard` 比較評価の採用項目 A-1〜A-4・B-1〜B-3 を統合済み）
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
* [比較評価チケット：ai-dev-standard との比較評価および優位要素の取り込み検討](../20261124-234050-ticket-evaluate-ai-dev-standard-comparison/index.md)
* [比較評価レポート（A-1〜A-4・B-1〜B-3 の根拠・詳細）](../20261124-234050-ticket-evaluate-ai-dev-standard-comparison/notes/001-comparison-evaluation.md)
