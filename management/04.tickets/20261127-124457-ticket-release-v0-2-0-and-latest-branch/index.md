---
id: 20261127-124457-ticket-release-v0-2-0-and-latest-branch
title: v0.2.0 のリリースと latest ブランチ作成（自己適用検証を含む）
status: done
created: 2026-11-27 12:44:57
updated: 2026-11-27 22:37:35
phase: closing
phase_status: done
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

* [x] **バージョン・CHANGELOG 整備**：`template/management/aico-manifest.json`・`installer/install.py`・`installer/upgrade.py` のバージョンが `0.2.0` へ統一され、`CHANGELOG.md` に `docs/03.spec/08.adoption-and-migration.md` 4.2 節の必須項目を満たす `v0.2.0` エントリが記録されていること。また `v0.1.0` → `v0.2.0` のマイグレーション要否と根拠が確認されていること。
* [x] **ドッグフーディング自己適用と厳格診断通過**：AIco 本体リポジトリの統合ブランチ（`main`）上で `tools/aico.sh update --source .` による自己適用が成功し、`management/aico-manifest.json` の `aico_version` が `0.2.0` へ更新されたうえで `tools/aico.sh doctor --strict` が `ERROR=0`・`WARN=0` で通過すること。
* [x] **Linux・Windows 実機での全自動テスト通過**：リリース準備および自己適用完了後の状態に対し、Linux 環境および Windows 11 実機環境（`ssh win11`）の双方で `unittest discover -s tests -v` が全件通過すること（テスト内の `v0.1.0` ハードコード等があれば追従済みであること）。
* [x] **`v0.2.0` タグ発行と `latest` ブランチ作成・公開確認**：自己適用コミットを含む最終コミットに注釈付きまたは正規タグ `v0.2.0` が発行され、同一コミットを指す `latest` ブランチ（fast-forward 専用・同名タグなし）が作成されて開発元リポジトリ（`origin`）へプッシュされ、公開ミラー（GitHub）への反映方針または反映完了が確認されていること。

## DoR（着手合意）

* **任せる範囲**：`v0.1.0..HEAD` の変更棚卸し・マイグレーション要否および自己適用リハーサル調査（`plan.md` 策定）、バージョン定数・`CHANGELOG.md`・関連テストの更新、独立レビュー実施、Linux／Windows 11 VM（管理者＋`gsudo -i Medium` 一般権限）での検証、および人間承認後の自己適用・タグ発行・`latest` ブランチ作成・プッシュ実行。
* **合意済み前提**：
  * リリースタグは `v0.1.0` と同じ注釈付きタグ（`git tag -a v0.2.0 -m "Release v0.2.0"`）を使用する。
  * 公開ミラー（GitHub）は GitLab 側ミラーリポジトリ設定により自動同期される前提とし、`origin`（GitLab）へ `main`・`latest`・`v0.2.0` をプッシュ後に反映を確認する。
* **未決事項（計画フェーズで調査・合意）**：
  * `v0.1.0` 実物運営領域へ `v0.2.0` の `tools/aico.sh update --source .` を一時クローンで事前リハーサル適用し、`doctor.py --strict` の新設品質ゲート等で既存記録の補正やマイグレーション追加が必要か確認する。
  * 作業ブランチ（`feature/<チケットID>`）でのリリース準備マージと、統合ブランチ（`main`）上での自己適用・タグ発行・`latest` 作成の切り分け順序（`docs/03.spec/08.adoption-and-migration.md` 4.2 節の段階 2〜4 との整合）。
* **着手合意**：合意済み（2026-11-27）

## 現在地

* **状況**：全 4 AC 達成・人間による DoD 承認完了（`done / closing / done`）。`v0.2.0` タグ・`latest` ブランチ（`432f075`）の公開および GitHub ミラー反映まで完了
* **ブロッカー（確認待ち）**：なし
* **次に取る行動**：なし（クローズ済み）

## 変更ファイル

<!-- AICO:AUTO:BEGIN:changed-files -->
| 種別 | パス |
| :--- | :--- |
| `M` | `CHANGELOG.md` |
| `M` | `installer/install.py` |
| `M` | `installer/migrations/README.md` |
| `M` | `installer/upgrade.py` |
| `M` | `template/management/aico-manifest.json` |
| `M` | `tests/helpers.py` |
| `M` | `tests/test_lifecycle.py` |
<!-- AICO:AUTO:END:changed-files -->

## DoD（完了の定義）

* **AC 検証結果と根拠**：
  * **AC1（達成）**：`template/management/aico-manifest.json`・`installer/install.py`・`installer/upgrade.py` を `0.2.0` へ統一し、`CHANGELOG.md` に `docs/03.spec/08.adoption-and-migration.md` 4.2 節の必須項目を満たす `v0.2.0` エントリを記録した。マイグレーション不要の根拠を `installer/migrations/README.md` と `plan.md` へ明記し、配布原本 3 箇所のバージョン一致を検証する単体テストを追加した（`414b620`）。
  * **AC2（達成）**：`main` 上で `bash tools/aico.sh update --source . --json` が例外フラグなし・警告／エラー 0 件で完了し、`management/aico-manifest.json` の `aico_version` が `0.2.0` へ更新されたうえで `bash tools/aico.sh doctor --strict --json` が `OK=9 / WARN=0 / ERROR=0` で通過した（`432f075`）。
  * **AC3（達成）**：自己適用後の `main` 状態に対し、Linux（Python 3.14.4 / `uv` 0.13.8）で 38/38 OK（14.532s）、Windows 11 VM（フレッシュクローン・`core.autocrlf=true`・Python 3.15.2 / `uv` 0.13.10）で管理者権限 38/38 OK（102.179s）・`gsudo -i Medium` 一般権限（開発者モード OFF）36 ok / 2 skipped（110.229s）を確認し、`CHANGELOG.md` の検証済み環境記載と完全一致することを確認した。
  * **AC4（達成）**：自己適用コミット `432f075` に注釈付きタグ `v0.2.0`（`1115e08a...`）および同一コミットを指す `latest` ブランチ（同名タグなし）を作成して `origin`（GitLab）へプッシュし、`git ls-remote` にて開発元（GitLab）および公開ミラー（GitHub `https://github.com/sasaki819/AIco.git`）双方での同一コミット反映を確認した。
* **未検証項目と人の判断結果**：なし（macOS 実機および全 AI ツール横断実機確認は `CHANGELOG.md` の未確認環境として明記済みであり、本リリースのスコープ外として合意済み）
* **プロジェクト側設計書・仕様書の更新確認**：更新不要（既存の `docs/03.spec/08.adoption-and-migration.md` リリース仕様どおりの実施であり、仕様変更なし）
* **ADR 要否判断**：不要（既存の SemVer・4 段階リリース・`latest` ブランチ方針に沿った運用実施のため新規設計判断なし）
* **関連記録・ADR への導線確認**：確認済み（`docs/03.spec/08.adoption-and-migration.md` および `v0.2.0` 包含チケット 4 件への相対リンクをすべて実物確認済み）

## 親子チケット・関連

* [導入・移行・リリース仕様（4.2 節・5 節）](../../../docs/03.spec/08.adoption-and-migration.md)
* [v0.2.0 包含チケット 1：初見ユーザー向けガイド整備と導入・初期設定ツール UX 改善](../20261124-155511-ticket-onboarding-docs-and-cli-ux/index.md)
* [v0.2.0 包含チケット 2：ai-dev-standard との比較評価および優位要素の取り込み検討](../20261124-234050-ticket-evaluate-ai-dev-standard-comparison/index.md)
* [v0.2.0 包含チケット 3：レビューフロー・クローズ手順・AI 進行案内の UX 改善](../20261124-231830-ticket-workflow-review-and-ux-improvements/index.md)
* [v0.2.0 包含チケット 4：Windows ネイティブ環境の改行・テスト・シンボリックリンク互換性対応](../20261126-092319-ticket-windows-compatibility-and-tests/index.md)
