---
id: implementation-round2-002-init-text-duplicate-warn-and-stderr
title: init.py テキストモードで WARN が二重出力され正常出力が stderr へ送出される
status: done
created: 2026-11-24 22:30:53
updated: 2026-11-24 22:49:16
severity: minor
reviewer: research-subagent
---

# init.py テキストモードで WARN が二重出力され正常出力が stderr へ送出される

## 対象

* `template/management/scripts/init.py`（268〜308 行目）
* `template/management/scripts/_lib/cli.py`（127〜132 行目）
* 比較基点：`c4c20d2`

## 指摘内容と根拠

`init.py` のテキストモード出力では、`lines`（`text`）内に「警告（エラーではないため…おすすめ設定例: `.../05.worker-models.md`）:」ヘッダー、`warnings[:10]` の省略表示、および末尾の `次のステップ:` ブロックを組み立てている。  
しかし `emit_result()` へ `status="warn"` と `warnings=warnings` をそのまま渡しているため、`worker_models` 未設定の標準初回導入（最大 21 件の警告が発生する最頻ケース）で以下の 2 点が発生する。

1. `_lib/cli.py:129-131` が `text` 出力直後に `for w in warnings: sys.stderr.write(f"WARN: {w}\n")` を全件出力するため、`次のステップ:` の直下に生の `WARN:` 行が最大 21 行二重出力され、10 件省略・警告補足・末尾の次ステップ案内が押し流されてしまう。
2. `_lib/cli.py:127` が `stream = sys.stdout if status == "ok" else sys.stderr` となっているため、`status="warn"` の正常完了出力全体が `stdout` ではなく `stderr` に送出される（`docs/03.spec/07.scripts.md` 2.2 節の「正常結果・変更予定・診断結果は `stdout` へ」とも不整合）。

`_lib/cli.py:emit_result()` で `status != "error"` の `text` を `sys.stdout` へ出力するとともに、テキスト内に警告を展開済みの場合に重複出力を抑止できるオプション（例：`emit_warnings_in_text: bool = True`）を追加して `init.py` から `False` を渡し、`tests/test_lifecycle.py` で `stdout` 出力と `WARN:` 非重複を検証するのが望ましい。

## 採否判断（人間選別）

* **判断**：採用（`in-progress`）
* **理由**：初見ユーザーが最も高確率で遭遇する `worker_models` 未設定初回実行時に、`WARN:` 二重出力で `次のステップ:` 案内が埋もれる問題および `stdout`/`stderr` 仕様不整合を解消するため。

## 修正内容

* `template/management/scripts/_lib/cli.py` の `emit_result()` にて、① `status != "error"` のテキスト出力を `sys.stdout` へ送出するよう修正（`docs/03.spec/07.scripts.md` 2.2 節準拠）、② `emit_warnings_in_text: bool = True` 引数を追加してテキスト内展開済み警告の重複出力を抑止可能とした。
* `template/management/scripts/init.py` から `emit_warnings_in_text=False` を渡すよう更新した（JSON 出力の `warnings` 配列は維持）。
* `tests/test_lifecycle.py` の `--init` テキストモードテストで、`02.tutorial.md`・`05.worker-models.md`・`次のステップ:` が `stdout` に出力され、`stderr` に `WARN:` が二重出力されないことを検証するよう強化した。
* 関連コミット：未コミット（作業ツリー上で実プロセス出力および全テスト検証済み）

## 独立再確認結果

* **結果**：解消確認（`done`）
* **確認者**：research-subagent（独立コンテキスト再確認）
* **根拠**：`template/management/scripts/_lib/cli.py` の `emit_result()`（`status != "error"` の `stdout` 送出および `emit_warnings_in_text: bool = True`）、`init.py` の `emit_warnings_in_text=False` 指定、`tests/test_lifecycle.py` の `stdout`/`stderr` アサーションがいずれも仕様（Spec 07 2.2 節）および他スクリプトの後方互換性と整合していることを実物照合で確認。
* **実行環境**：Linux（独立ワーカーによるファイル直接照合＋親セッションでの `unittest` 30/30 OK・`install.py --init` 実プロセス出力確認 `STDERR=''`）
* **未確認事項**：独立ワーカー内のサンドボックス制約により同ワーカーでのシェル再実行は未実施（親セッションで検証済み）
