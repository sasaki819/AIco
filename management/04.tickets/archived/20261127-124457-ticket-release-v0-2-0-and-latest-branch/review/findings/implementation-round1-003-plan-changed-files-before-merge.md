---
id: implementation-round1-003-plan-changed-files-before-merge
title: plan.md の 2 段構成手順にマージ前 update_changed_files.py 実行タイミングが欠落
status: done
created: 2026-11-27 14:52:59
updated: 2026-11-27 18:57:00
severity: minor
reviewer: worker-middle（独立レビューワーカー）
---

# plan.md の 2 段構成手順にマージ前 update_changed_files.py 実行タイミングが欠落

## 対象

* `management/04.tickets/20261127-124457-ticket-release-v0-2-0-and-latest-branch/plan.md`（L19-L25, L38-L41）
* 比較基点：`715c9de`

## 指摘内容と根拠

* `plan.md` ではステップ 5 で作業ブランチを `main` へマージし、ステップ 7 で `main` 上にてチケットをクローズする 2 段構成としているが、`index.md` の `## 変更ファイル`（現在は「変更されたプロジェクト資産はない。」）を更新する手順が記載されていない。
* `management/scripts/update_changed_files.py`（現行 `v0.1.0`）および `template/management/scripts/update_changed_files.py`（`v0.2.0`）を実物照合したところ、いずれも比較基点は `<integration_branch>...HEAD` であり、`branch_exists()`（`template/management/scripts/_lib/git_utils.py` L52-L59）はブランチ名（`refs/heads/`・`refs/remotes/origin/`）のみを許容しコミット SHA を受け付けない。さらに現行 `v0.1.0` 版はコミット済み差分のみを参照する。
* そのため、作業ブランチでコミット後に `update_changed_files.py` を実行しないままステップ 5 で `main` へマージすると、ステップ 7 で `main` 上から `update_changed_files.py` を実行しても `main...HEAD` の差分が 0 件となり、本チケットで変更したプロジェクト資産をスクリプト経由で記録できなくなる（誤って `main` 上で再実行すると既存テーブルも空に上書きされる）。
* **推奨修正案**：`plan.md` のステップ 4〜5（作業ブランチから `main` へのマージ前手順）に、「リリース準備変更をコミットしたうえで作業ブランチ上で `management/scripts/update_changed_files.py` を実行して `index.md` の `## 変更ファイル` を反映・コミットしてから `main` へマージする（ステップ 7 の `main` 上クローズ時は `update_changed_files.py` を再実行しない）」旨を追記する。

## 採否判断（人間選別）

* **判断**：採用（`in-progress`）
* **理由**：マージ前に作業ブランチ上で `update_changed_files.py` を実行してコミットしておかないと、`main` 上のクローズ時に変更ファイル一覧を正しく記録できなくなるため、指摘どおり `plan.md` へ手順を明記する。

## 修正内容

* `management/04.tickets/20261127-124457-ticket-release-v0-2-0-and-latest-branch/plan.md` の「合意した仕様（2. 切り分け手順）」「ステップ一覧（ステップ 5・7）」「検証方針」および「判断ログ」に、リリース準備変更を作業ブランチへコミット後、`main` へマージする前に作業ブランチ上で `uv run management/scripts/update_changed_files.py --ticket 20261127-124457-ticket-release-v0-2-0-and-latest-branch` を実行して `index.md` の `## 変更ファイル` を反映・コミットしてからマージする手順、およびステップ 7 の `main` 上クローズ時は `update_changed_files.py` を再実行しない旨を追記した。
* 関連コミット：未コミット（独立再確認完了後にまとめてコミット予定）

## 独立再確認結果

* **判定**：解消（`done`）
* **確認根拠**：`plan.md` の L22・L28・L42・L44・L52・L67 を実物照合し、作業ブランチ上（`main` マージ前）での `update_changed_files.py` 実行・コミット手順、およびステップ 7 の `main` 上クローズ時に再実行しない旨が漏れなく明記されていることを確認した。
* **実行環境**：独立コンテキストの読み取り専用ワーカー（`view_file` による実物ファイル照合・比較基点 `715c9de`）
* **未確認事項**：ワーカー側での動的コマンド実行（親セッションで Linux 38/38 OK・Win11 管理者 38/38 OK・一般権限 36 ok / 2 skipped 確認済み）、段階 3〜4 の本番実行（後続工程で実施予定）
