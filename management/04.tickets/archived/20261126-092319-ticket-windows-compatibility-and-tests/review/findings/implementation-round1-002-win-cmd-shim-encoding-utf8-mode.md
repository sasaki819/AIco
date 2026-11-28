---
id: implementation-round1-002-win-cmd-shim-encoding-utf8-mode
title: Windows no_uv_fallback テストの cmd シム生成で UTF-8 モード時に非 ASCII パスが文字化けする恐れ
status: done
created: 2026-11-27 03:04:47
updated: 2026-11-27 10:56:42
severity: minor
reviewer: Independent Implementation Reviewer (subagent)
---

# Windows no_uv_fallback テストの cmd シム生成で UTF-8 モード時に非 ASCII パスが文字化けする恐れ

## 対象

* **対象ファイル**：`tests/test_daily_scripts.py`（L721–732 および L740–747 付近）
* **比較基点**：`738c7a8`（`main`）〜 `b0be0a3`

## 指摘内容と根拠

* `cmd_enc = locale.getpreferredencoding(False)` を用いて `python.cmd` 等のシムを書き出しているが、Python の UTF-8 モード（`PYTHONUTF8=1` または PEP 686 により UTF-8 モードが既定有効となる Python 3.15 以降）では OS のコンソールコードページ（CP932 等）ではなく `"UTF-8"` が返る。
* `cmd.exe` は既定のコンソールコードページで `.cmd` を解釈するため、`py_exe` のパスに日本語ユーザー名等の非 ASCII 文字が含まれて `python.cmd` 生成分岐へ入った場合、UTF-8 出力されたパスが文字化けして起動失敗する恐れがある。
* **推奨修正案**：`.cmd` シムを生成する際は先頭に `chcp 65001 >nul` を入れ、`encoding="utf-8"`（BOM なし）で書き出す（`@echo off\r\nchcp 65001 >nul\r\n"{py_exe}" %*\r\n`）。

## 採否判断（人間選別）

* **判断**：採用（`in-progress`）
* **判断日**：2026-11-27
* **理由**：Python 3.15 以降や `PYTHONUTF8=1` 環境下での非 ASCII パス文字化けを予防するため、`chcp 65001 >nul` + UTF-8 出力へ修正する。

## 修正内容

* **修正概要**：`tests/test_daily_scripts.py` から未使用となった `import locale` と `locale.getpreferredencoding(False)` 参照を削除し、`python.cmd` シム生成を `@echo off\r\nchcp 65001 >nul\r\n"{py_exe}" %*\r\n`（`encoding="utf-8"`・BOM なし）へ変更した。
* **関連コミット**：`e35f726`
* **検証結果**：Linux 37/37 OK、Windows 11 VM 37/37 OK。加えて Windows 11 VM で非 ASCII・空白含むパス（`日本語フォルダ スペース`）を呼び出す `chcp 65001 >nul` + UTF-8 `.cmd` シムが正常終了（`UTF8_SHIM_OK`）することを確認した。

## 独立再確認結果

* **判定**：解消（`done`）
* **確認日**：2026-11-27
* **確認根拠**：`tests/test_daily_scripts.py` 全量で未使用の `import locale` と `locale.getpreferredencoding(False)` が除去され、`python.cmd`（L765–769）が `chcp 65001 >nul` 先頭付き・`encoding="utf-8"`（BOM なし）・明示 CRLF で生成され、`system32` が `PATH` に含まれていることを実物照合で確認した。
* **実行環境**：読み取り専用独立ワーカー（Linux / 実物コード照合）
* **未確認事項**：ワーカー内での動的実行（サンドボックス接続制約のため未実施。親セッションの Windows 11 VM 非 ASCII パス `.cmd` シム実行結果 `UTF8_SHIM_OK` と矛盾なし）
