---
id: implementation-round2-001-getting-started-step-number-mismatch
title: 01.getting-started.md の既存プロジェクト参加者向け案内ステップ番号誤記
status: done
created: 2026-11-24 22:30:53
updated: 2026-11-24 22:49:16
severity: major
reviewer: research-subagent
---

# 01.getting-started.md の既存プロジェクト参加者向け案内ステップ番号誤記

## 対象

* `docs/04.user-guide/01.getting-started.md`（6 行目）
* `template/management/01.manual/01.getting-started.md`（6 行目）
* 比較基点：`c4c20d2`

## 指摘内容と根拠

6 行目に「すでに導入済みのプロジェクトへ参加した方は、Step 2（`AGENTS.md` の確認）以降からご覧ください。」と記載されているが、実際の見出し構成は Step 1（資材配置）・Step 2（`init` 初期設定）・Step 3（`AGENTS.md` 追記）・Step 4（動作確認と初回コミット）であり、`AGENTS.md` に該当するのは Step 3 である。  
既存導入済みプロジェクトへ途中参加した初見ユーザーが案内に従うと、不要な `tools/aico.sh init`（`aico-manifest.json` 書き換え・再同期）を実行してしまうおそれがある。  
なお、既存プロジェクト参加者には初回コミットも不要であるため、「すでに導入済みのプロジェクトへ参加した方は、プロジェクトの `AGENTS.md` を確認したうえで `[チュートリアル](02.tutorial.md)` からご覧ください。」等へ見直すのが自然である。

## 採否判断（人間選別）

* **判断**：採用（`in-progress`）
* **理由**：既存導入済みプロジェクトの参加者が誤って Step 2（`init`）を実行してしまう誤誘導を防ぐため。

## 修正内容

* `docs/04.user-guide/01.getting-started.md`（6 行目）を「すでに導入済みのプロジェクトへ参加した方は、プロジェクトルートの `AGENTS.md` を確認したうえで `[チュートリアル](02.tutorial.md)` からご覧ください。」へ修正した。
* `template/management/01.manual/01.getting-started.md` を完全同一コピーへ同期した。
* 関連コミット：未コミット（作業ツリー上でテスト検証済み）

## 独立再確認結果

* **結果**：解消確認（`done`）
* **確認者**：research-subagent（独立コンテキスト再確認）
* **根拠**：`docs/04.user-guide/01.getting-started.md` 6 行目が既存プロジェクト参加者向けに `AGENTS.md` 確認→チュートリアル導線へ修正され、`template/management/01.manual/01.getting-started.md` と完全一致かつ Markdown 規約違反なしであることを実物照合で確認。
* **実行環境**：Linux（独立ワーカーによるファイル直接照合＋親セッションでの `unittest` 30/30 OK・`doctor.py` OK=9/WARN=0/ERROR=0）
* **未確認事項**：独立ワーカー内のサンドボックス制約により同ワーカーでのシェル再実行は未実施（親セッションで検証済み）
