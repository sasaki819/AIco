---
id: 20261126-092319-ticket-windows-compatibility-and-tests
title: Windows ネイティブ環境の改行・テスト・シンボリックリンク互換性対応
status: open
created: 2026-11-26 09:23:19
updated: 2026-11-26 09:23:19
phase: drafting
phase_status: working
branch: feature/20261126-092319-ticket-windows-compatibility-and-tests
parent: null
children: []
discussions: []
adrs: []
---

# Windows ネイティブ環境の改行・テスト・シンボリックリンク互換性対応

## 概要

`20261124-231830-ticket-workflow-review-and-ux-improvements` のクローズ時に Windows PowerShell 実機環境でテスト（`uv run -m unittest discover -s tests -v`）を実施した結果、`main` 時点から存在していた Windows ネイティブ環境特有の互換性課題（FAIL 8 件・ERROR 1 件）が顕在化した。  
本チケットでは、Windows ネイティブ環境（PowerShell および Git for Windows の既定設定 `core.autocrlf=true`）でも AIco の導入・初期設定・診断・自動テストが一貫して動作するよう、以下の 3 領域を整備し実機検証を完了する。

1. **改行コード（LF）保証**：AIco リポジトリ自身の `.gitattributes` を整備し、Windows 環境でのクローン時および `install.py` / `update.py` による配布時に Markdown 等が CRLF 化せず LF 規約を満たすようにする。
2. **自動テストの Windows ネイティブ対応**：`tests/test_lifecycle.py`・`tests/test_daily_scripts.py` における `bash tools/aico.sh` 直接呼び出し（PowerShell で `FileNotFoundError: [WinError 2]`）を OS に応じて `tools/aico.bat` / `tools/aico.sh` で切り替えるよう対応し、あわせて Windows 一般権限（開発者モード OFF）での `symlink_to()` 制約にも対応する。
3. **Windows 実機での検証完了**：`init.py`・`doctor.py` の `pr_template` リポジトリ外シンボリックリンク境界検査および改行挙動を含め、Windows 実機環境で自動テスト全件の通過を確認する。

## AC（受け入れ条件）

* [ ] **リポジトリ改行設定と配布時 LF 保証**：AIco リポジトリに `.gitattributes` が整備され、Windows（`core.autocrlf=true`）でクローンしても Markdown・Python・シェルスクリプトが LF で展開されること。あわせて `install.py` / `update.py` で配布されるテキストファイルが `doctor.py` の LF 検査を満たすこと。
* [ ] **テストスイートの Windows ネイティブ対応**：`tests/` 配下のラッパーテストが Windows では `tools/aico.bat` を検証し、`bash` が PATH にない PowerShell 環境でも `FileNotFoundError` で失敗しないこと。またシンボリックリンク作成権限がない Windows 一般権限環境でもテストが破綻しないこと。
* [ ] **Windows 実機および Linux での全テスト通過**：Linux 環境と Windows PowerShell 実機環境の双方で自動テスト（`unittest discover -s tests -v`）が全件通過し、`init.py`・`doctor.py` の `pr_template` シンボリックリンク境界検査および改行挙動が実機確認されていること。
* [ ] **ドキュメント整合と品質規約**：変更に伴う運用・検証前提の差分が必要に応じて `docs/03.spec/`・`docs/04.user-guide/`・`template/management/01.manual/`（完全一致同期）へ反映され、`doctor.py` が `ERROR=0`・`WARN=0` で通過すること。

## DoR（着手合意）

* **任せる範囲**：Windows 互換性原因の詳細調査・計画策定（`plan.md`）、`.gitattributes` 追加、`installer/`・`template/management/scripts/`・`tests/`・関連ドキュメントの修正および Linux 環境での自動テスト検証（Windows 実機検証は人間環境で実施して結果を照合する）。なお AIco 本体運営領域（`management/scripts/` 等）はリリース前の `tools/aico.sh update --source .` で自己適用するため作業ブランチ内で直接改造しない。
* **未決事項**：
  * `install.py` / `update.py` のコピー処理でテキストファイルの改行を明示的に LF 正規化するか、リポジトリの `.gitattributes` による LF 維持と併用するか。
  * Windows の一般権限（開発者モード OFF で `symlink_to` が `WinError 1314` となる環境）におけるシンボリックリンク境界検査テストの扱い（`skipTest` とするか、開発者モード／管理者権限での実行手順を併記するか）。
  * `tests/test_daily_scripts.py` の `no_uv_fallback` 等、POSIX シェル前提のラッパーテストを Windows の `tools/aico.bat` でどこまで等価検証するか。
* **着手合意**：未合意

## 現在地

* **状況**：起票完了（`open / drafting / working`）
* **ブロッカー（確認待ち）**：なし
* **次に取る行動**：DoR を確認・合意し、`aico-ticket-start` で作業ブランチを作成して調査・計画策定へ進む

## 変更ファイル

<!-- AICO:AUTO:BEGIN:changed-files -->
変更されたプロジェクト資産はない。
<!-- AICO:AUTO:END:changed-files -->

## DoD（完了の定義）

* **AC 検証結果と根拠**：
* **未検証項目と人の判断結果**：なし
* **関連記録・ADR への導線確認**：未確認

## 親子チケット・関連

* [引き継ぎ元チケット：レビューフロー・クローズ手順・AI 進行案内の UX 改善](../20261124-231830-ticket-workflow-review-and-ux-improvements/index.md)
