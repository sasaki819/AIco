---
id: 20261127-124457-ticket-release-v0-2-0-and-latest-branch
title: v0.2.0 のリリースと latest ブランチ作成（自己適用検証を含む）
status: open
created: 2026-11-27 12:44:57
updated: 2026-11-27 12:44:57
phase: drafting
phase_status: working
branch: feature/20261127-124457-ticket-release-v0-2-0-and-latest-branch
parent: null
children: []
discussions: []
adrs: []
---

# v0.2.0 のリリースと latest ブランチ作成（自己適用検証を含む）

## 概要

`v0.1.0` 以降に `main` へ統合された一連の改善（オンボーディング向けガイド・CLI UX 改善、`ai-dev-standard` 比較評価に基づくレビューフロー・クローズ手順・品質ゲート・AI 進行案内の改善、Windows ネイティブ環境の改行・テスト・シンボリックリンク互換性対応）を **`v0.2.0`** としてリリースする。  
`docs/03.spec/08.adoption-and-migration.md`（4.2 節）のリリース・自己適用手順に従い、以下の 4 点を一貫して完了する。

1. **リリース準備**：`template/management/aico-manifest.json`（`aico_version`）・`installer/install.py`・`installer/upgrade.py`（`AICO_VERSION`）を `0.2.0` へ更新し、`CHANGELOG.md` へ `v0.2.0` エントリ（変更内容・変更意図・移行要否と手順・検証済み／未確認環境）を追記する。あわせて `v0.1.0` → `v0.2.0` 間のマイグレーション要否を確認する。
2. **ドッグフーディング自己適用検証**：統合ブランチ（`main`）上で AIco 本体自身の運営領域へ `tools/aico.sh update --source .` を適用し、`v0.1.0` 運営領域から `v0.2.0` への移行が例外フラグなしで安全に完了すること、`tools/aico.sh doctor --strict` および全自動テスト（Linux・Windows 11 実機）が通過することを検証する。
3. **リリースタグ発行と `latest` ブランチ作成**：自己適用コミットまで含めた最終状態へ `v0.2.0` タグを発行し、最新安定版を指す fast-forward 専用ブランチ `latest` を同一コミット上に作成する（同名 `latest` タグは作成しない）。
4. **リモート公開・ミラー反映確認**：`main`・`latest`・`v0.2.0` タグを開発元リポジトリ（GitLab `origin`）へプッシュし、公開ミラー（GitHub）への反映を確認する。

## AC（受け入れ条件）

* [ ] **バージョン・CHANGELOG 整備**：`template/management/aico-manifest.json`・`installer/install.py`・`installer/upgrade.py` のバージョンが `0.2.0` へ統一され、`CHANGELOG.md` に `docs/03.spec/08.adoption-and-migration.md` 4.2 節の必須項目を満たす `v0.2.0` エントリが記録されていること。また `v0.1.0` → `v0.2.0` のマイグレーション要否と根拠が確認されていること。
* [ ] **ドッグフーディング自己適用と厳格診断通過**：AIco 本体リポジトリの統合ブランチ（`main`）上で `tools/aico.sh update --source .` による自己適用が成功し、`management/aico-manifest.json` の `aico_version` が `0.2.0` へ更新されたうえで `tools/aico.sh doctor --strict` が `ERROR=0`・`WARN=0` で通過すること。
* [ ] **Linux・Windows 実機での全自動テスト通過**：リリース準備および自己適用完了後の状態に対し、Linux 環境および Windows 11 実機環境（`ssh win11`）の双方で `unittest discover -s tests -v` が全件通過すること（テスト内の `v0.1.0` ハードコード等があれば追従済みであること）。
* [ ] **`v0.2.0` タグ発行と `latest` ブランチ作成・公開確認**：自己適用コミットを含む最終コミットに注釈付きまたは正規タグ `v0.2.0` が発行され、同一コミットを指す `latest` ブランチ（fast-forward 専用・同名タグなし）が作成されて開発元リポジトリ（`origin`）へプッシュされ、公開ミラー（GitHub）への反映方針または反映完了が確認されていること。

## DoR（着手合意）

* **任せる範囲**：`v0.1.0..HEAD` の変更棚卸し・マイグレーション要否および自己適用リハーサル調査（`plan.md` 策定）、バージョン定数・`CHANGELOG.md`・関連テストの更新、独立レビュー実施、Linux／Windows 11 VM での検証、および人間承認後の自己適用・タグ発行・`latest` ブランチ作成・プッシュ実行。
* **未決事項**：
  * `v0.1.0` 実物運営領域（既存チケット記録や `AGENTS.md`・`management/01.manual/` 等）へ `v0.2.0` の `tools/aico.sh update --source .` を適用した際に、`doctor.py --strict` の新設品質ゲート等で既存記録の補正またはマイグレーションスクリプト追加が必要になるか（計画フェーズで一時クローンを用いて事前リハーサル確認する）。
  * 作業ブランチ（`feature/<チケットID>`）でのリリース準備マージと、統合ブランチ（`main`）上での自己適用・タグ発行・`latest` 作成の切り分け順序（`docs/03.spec/08.adoption-and-migration.md` 4.2 節の段階 2〜4 との整合）。
  * 公開ミラー（GitHub `https://github.com/sasaki819/AIco.git`）への反映方法（GitLab 側ミラー設定で自動同期されるか、手動プッシュが必要か）。
  * リリース時のタグ形式（注釈付きタグ `git tag -a v0.2.0` と軽量タグのどちらを採るか）。
* **着手合意**：未合意

## 現在地

* **状況**：起票完了（`open / drafting / working`）
* **ブロッカー（確認待ち）**：DoR（着手合意）の確認待ち
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

* [導入・移行・リリース仕様（4.2 節・5 節）](../../../docs/03.spec/08.adoption-and-migration.md)
* [v0.2.0 包含チケット 1：初見ユーザー向けガイド整備と導入・初期設定ツール UX 改善](../20261124-155511-ticket-onboarding-docs-and-cli-ux/index.md)
* [v0.2.0 包含チケット 2：ai-dev-standard との比較評価および優位要素の取り込み検討](../20261124-234050-ticket-evaluate-ai-dev-standard-comparison/index.md)
* [v0.2.0 包含チケット 3：レビューフロー・クローズ手順・AI 進行案内の UX 改善](../20261124-231830-ticket-workflow-review-and-ux-improvements/index.md)
* [v0.2.0 包含チケット 4：Windows ネイティブ環境の改行・テスト・シンボリックリンク互換性対応](../20261126-092319-ticket-windows-compatibility-and-tests/index.md)
