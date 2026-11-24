---
id: implementation-round2-003-cheatsheet-skill-count-mismatch
title: 03.cheatsheet.md および README.md の基本 6 スキル表記と実スキル数（7 個）の不一致
status: done
created: 2026-11-24 22:30:53
updated: 2026-11-24 22:49:16
severity: minor
reviewer: research-subagent
---

# 03.cheatsheet.md および README.md の基本 6 スキル表記と実スキル数（7 個）の不一致

## 対象

* `docs/04.user-guide/03.cheatsheet.md`（6・8・16 行目）
* `template/management/01.manual/03.cheatsheet.md`（6・8・16 行目）
* `README.md`（33 行目）
* 比較基点：`c4c20d2`

## 指摘内容と根拠

`03.cheatsheet.md` の 6 行目（概要）・8 行目（`## まず覚える基本 6 スキル`）および `README.md` 33 行目で「基本 6 スキル」と記載しているが、表の 5 行目（16 行目）に `` `aico-ticket-plan` → `aico-ticket-implement` `` の 2 スキルが併記されているため、実際に列挙されているスキル数は 7 個（`aico-ticket-status`・`aico-discuss`・`aico-create-ticket`・`aico-ticket-start`・`aico-ticket-plan`・`aico-ticket-implement`・`aico-ticket-close`）になっている。  
表記を「まず覚える基本 7 スキル」（表を 7 行へ分割）へ揃えることで、記載数と実スキル数の食い違いを解消できる。

## 採否判断（人間選別）

* **判断**：採用（`in-progress`）
* **理由**：記載件数と表の実スキル数を一致させ、初見ユーザーの混乱を防ぐため。

## 修正内容

* `docs/04.user-guide/03.cheatsheet.md` の概要・見出しを「基本 7 スキル」へ統一し、`aico-ticket-plan` と `aico-ticket-implement` を別行へ分割して全 7 行・7 スキルとした。
* `template/management/01.manual/03.cheatsheet.md` へ完全同一コピーを同期し、`README.md` 30 行目の表記も「基本7スキル」へ統一した。
* 関連コミット：未コミット（作業ツリー上でテスト検証済み）

## 独立再確認結果

* **結果**：解消確認（`done`）
* **確認者**：research-subagent（独立コンテキスト再確認）
* **根拠**：`docs/04.user-guide/03.cheatsheet.md`（概要・見出し・7 行表）、`template/management/01.manual/03.cheatsheet.md`、および `README.md` 30 行目がすべて「基本 7 スキル」で統一され、関連文書に「基本 6 スキル」の残存がないことを実物照合で確認。
* **実行環境**：Linux（独立ワーカーによるファイル直接照合＋親セッションでの `unittest` 30/30 OK・`doctor.py` OK=9/WARN=0/ERROR=0）
* **未確認事項**：独立ワーカー内のサンドボックス制約により同ワーカーでのシェル再実行は未実施（親セッションで検証済み）
