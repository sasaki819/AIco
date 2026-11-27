---
id: 20261126-092319-ticket-windows-compatibility-and-tests
title: Windows ネイティブ環境の改行・テスト・シンボリックリンク互換性対応
status: done
created: 2026-11-26 09:23:19
updated: 2026-11-27 12:03:00
phase: closing
phase_status: done
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

* [x] **リポジトリ改行設定と配布時 LF 保証**：AIco リポジトリに `.gitattributes` が整備され、Windows（`core.autocrlf=true`）でクローンしても Markdown・Python・シェルスクリプトが LF で展開されること。あわせて `install.py` / `update.py` で配布されるテキストファイルが `doctor.py` の LF 検査を満たすこと。
* [x] **テストスイートの Windows ネイティブ対応**：`tests/` 配下のラッパーテストが Windows では `tools/aico.bat` を検証し、`bash` が PATH にない PowerShell 環境でも `FileNotFoundError` で失敗しないこと。またシンボリックリンク作成権限がない Windows 一般権限環境でもテストが破綻しないこと。
* [x] **Windows 実機および Linux での全テスト通過**：Linux 環境と Windows PowerShell 実機環境の双方で自動テスト（`unittest discover -s tests -v`）が全件通過し、`init.py`・`doctor.py` の `pr_template` シンボリックリンク境界検査および改行挙動が実機確認されていること。
* [x] **ドキュメント整合と品質規約**：変更に伴う運用・検証前提の差分が必要に応じて `docs/03.spec/`・`docs/04.user-guide/`・`template/management/01.manual/`（完全一致同期）へ反映され、`doctor.py` が `ERROR=0`・`WARN=0` で通過すること。

## DoR（着手合意）

* **任せる範囲**：Windows 互換性原因の詳細調査・計画策定（`plan.md`）、`.gitattributes` 追加、`installer/`・`template/management/scripts/`・`tests/`・関連ドキュメントの修正および Linux 環境での自動テスト検証（Windows 実機検証は人間環境で実施して結果を照合する）。なお AIco 本体運営領域（`management/scripts/` 等）はリリース前の `tools/aico.sh update --source .` で自己適用するため作業ブランチ内で直接改造しない。
* **未決事項**：
  * `install.py` / `update.py` のコピー処理でテキストファイルの改行を明示的に LF 正規化するか、リポジトリの `.gitattributes` による LF 維持と併用するか。
  * Windows の一般権限（開発者モード OFF で `symlink_to` が `WinError 1314` となる環境）におけるシンボリックリンク境界検査テストの扱い（`skipTest` とするか、開発者モード／管理者権限での実行手順を併記するか）。
  * `tests/test_daily_scripts.py` の `no_uv_fallback` 等、POSIX シェル前提のラッパーテストを Windows の `tools/aico.bat` でどこまで等価検証するか。
* **着手合意**：合意済み（2026-11-26）

## 現在地

* **状況**：完了（`done / closing / done`）。全 4 AC・DoD・レビュー指摘 3 件の独立再確認および Linux・Windows 11 実機検証をすべて完了済み
* **ブロッカー（確認待ち）**：なし
* **次に取る行動**：統合ブランチ（`main`）へマージ後、統合ブランチ側で `rebuild_indexes.py` を実行して一覧を再生成する

## 変更ファイル

<!-- AICO:AUTO:BEGIN:changed-files -->
| 種別 | パス |
| :--- | :--- |
| `A` | `.gitattributes` |
| `M` | `docs/03.spec/08.adoption-and-migration.md` |
| `M` | `docs/04.user-guide/01.getting-started.md` |
| `M` | `installer/install.py` |
| `M` | `installer/upgrade.py` |
| `M` | `template/management/01.manual/01.getting-started.md` |
| `M` | `tests/helpers.py` |
| `M` | `tests/test_daily_scripts.py` |
| `M` | `tests/test_lib.py` |
| `M` | `tests/test_lifecycle.py` |
| `M` | `tests/test_user_guide.py` |
<!-- AICO:AUTO:END:changed-files -->

## DoD（完了の定義）

* **AC 検証結果と根拠**：
  * **AC1（リポジトリ改行設定と配布時 LF 保証）**：達成。ルート `.gitattributes` を新設し（`*.md`/`*.json`/`*.py`/`*.sh`/`*.toml`/`.gitattributes`/`.gitignore` は `eol=lf`、`*.bat` は `eol=crlf`）、`installer/install.py`・`installer/upgrade.py` で配布時改行正規化を実装。`tests/test_user_guide.py` および `tests/test_lifecycle.py`（CRLF ソースからの配布正規化・べき等性）で検証済み、かつ Windows 11 実機（`core.autocrlf=true`・フレッシュクローン）で LF 展開を確認済み。
  * **AC2（テストスイートの Windows ネイティブ対応）**：達成。`tests/helpers.py` に `run_wrapper`・`create_symlink_or_skip`・Windows 環境変数大文字小文字吸収を追加し、`tests/test_lifecycle.py`・`tests/test_daily_scripts.py` を `tools/aico.bat` 対応および `WinError 1314` 時の明示 `skipTest` へ改修。さらにレビュー指摘 3 件（`git`・`uv` 同居時の実体 `git.exe` 探索、`python.cmd` の `chcp 65001 >nul` + UTF-8 出力、`init.py` 外部シンボリックリンク拒否理由アサーション）を修正・独立再確認済み（`done`）。
  * **AC3（Windows 実機および Linux での全テスト通過）**：達成。Linux（Python 3.14.4）37/37 OK、Windows 11 VM 管理者権限（Python 3.15.2 / `core.autocrlf=true`）37/37 OK（加えて `shims/git.cmd` + `shims/uv.exe` 同居シミュレーションおよび日本語パス `.cmd` シム実行も通過）、Windows 11 一般権限（`IsInRole=False`・開発者モード OFF）35 ok / 2 skipped（`WinError 1314` のみ明示スキップ）を確認済み。
  * **AC4（ドキュメント整合と品質規約）**：達成。`docs/03.spec/08.adoption-and-migration.md`・`docs/04.user-guide/01.getting-started.md`・`template/management/01.manual/01.getting-started.md` を更新・完全一致同期し、`uv run management/scripts/doctor.py --json` が `OK=9 / WARN=0 / ERROR=0` で通過することを確認済み。
* **未検証項目と人の判断結果**：なし
* **関連記録・ADR への導線確認**：確認済み（引き継ぎ元チケット `../20261124-231830-ticket-workflow-review-and-ux-improvements/index.md` の実在、`plan.md` の全 7 ステップ完了、`review/index.md` および指摘 3 件すべての `status: done`・`doctor.py` リンク検査通過を確認）

## 親子チケット・関連

* [引き継ぎ元チケット：レビューフロー・クローズ手順・AI 進行案内の UX 改善](../20261124-231830-ticket-workflow-review-and-ux-improvements/index.md)
