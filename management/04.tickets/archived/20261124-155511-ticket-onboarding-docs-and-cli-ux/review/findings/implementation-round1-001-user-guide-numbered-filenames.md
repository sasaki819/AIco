---
id: implementation-round1-001-user-guide-numbered-filenames
title: 04.user-guide 配下のファイル名に連番を付与する
status: done
created: 2026-11-24 21:38:54
updated: 2026-11-24 22:22:37
severity: minor
reviewer: human
---

# 04.user-guide 配下のファイル名に連番を付与する

## 対象

* `docs/04.user-guide/` 配下の全ガイドファイルおよび `template/management/01.manual/` 配下の同期コピー
* これらを参照する `README.md`・`template/AGENTS.md`・`docs/03.spec/08.adoption-and-migration.md`・`installer/install.py`・`template/management/scripts/init.py`・`tests/`
* 比較基点：`c4c20d2`（作業ツリー未コミット差分）

## 指摘内容と根拠

`docs/02.policy/` や `docs/03.spec/` と同様に、`docs/04.user-guide/` 配下のファイル名にも `01.`・`02.`・… と連番を振り、初見ユーザーがフォルダを開いただけで読む順番を一目で把握できるようにしたい。  
`template/management/01.manual/` へは `docs/04.user-guide/` と完全同一の構成・ファイル名でコピーするため、コピー時の連番調整は不要である。

## 採否判断（人間選別）

* **判断**：採用（`in-progress`）
* **理由**：人間レビューによる直接指摘であり、`01.getting-started.md`〜`05.worker-models.md` の連番構成とすることで読む順序の視認性と他ディレクトリ（`02.policy` / `03.spec`）との命名統一性を高める。

## 修正内容

* `docs/04.user-guide/` 配下の 5 ファイルを連番ファイル名へリネームし、H1 見出しも `01.`〜`05.` 付きへ統一した（`index.md` は目次として無番維持）。
  * `01.getting-started.md`、`02.tutorial.md`、`03.cheatsheet.md`、`04.user-guide.md`、`05.worker-models.md`
* `template/management/01.manual/` を `docs/04.user-guide/` から完全同一コピーへ再同期した。
* 全参照箇所（`README.md`・`template/AGENTS.md`・`docs/03.spec/08.adoption-and-migration.md`・`installer/install.py`・`template/management/scripts/init.py`・`tests/test_user_guide.py`・`tests/test_lifecycle.py`・`tests/test_daily_scripts.py`・チケット記録）を新ファイル名へ更新し、無番名の残存参照がないことを確認した。
* 関連コミット：未コミット（作業ツリー上で検証済み。テスト 30/30 OK、`doctor.py` ERROR 0 / WARN 0）

## 独立再確認結果

* **結果**：解消確認（`done`）
* **確認者**：human（指摘者本人による確認完了）
* **実行環境**：作業ツリー上の実物確認および自動テスト 30/30 OK
* **未確認事項**：なし（独立 AI ワーカーによるチケット全体レビューは round2 で別途実施）
