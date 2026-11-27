# 作業計画

## 合意した仕様

### 1. 事前調査・リハーサル結果（実物照合済み）

* **マイグレーション要否（不要と確定）**：一時クローン上で `0.2.0` へ更新後に `bash tools/aico.sh update --source . --json` を事前リハーサルした結果、`returncode=0`・`warnings=[]`・`errors=[]`（103 ファイル更新：廃止ガイド削除・新ユーザーガイド 5 冊および `pr-template.md` 配置・`AGENTS.md` マーカー内のみ更新・`aico-manifest.json` 固有設定保持・エージェント同期および一覧再生成）で完了し、続く `bash tools/aico.sh doctor --strict --json` も `OK=9 / WARN=0 / ERROR=0` で通過した。`v0.1.0` → `v0.2.0` は既存記録の構造変換を伴わない後方互換の MINOR 変更であるため、マイグレーションスクリプトは不要とする。
* **テストコードのバージョンハードコード発見（本チケットで解消）**：
  * `tests/helpers.py` の `make_source_copy()` が `AICO_VERSION = "0.1.0"` を固定文字列置換していたため、バージョン更新後も将来にわたり壊れない正規表現置換へ改修する。
  * `tests/test_lifecycle.py` のアップグレード系 3 テスト（`test_broken_and_failing_migrations_and_archive_source`・`test_install_with_init_flag_and_upgrade_removes_obsolete_workflow_reference`・`test_init_pr_template_placement_no_overwrite_and_upgrade_preservation`）が現行 `template/` を導入元とする `setup_installed_repo()` を使って `0.2.0` や `0.1.1` へ更新する前提になっており、`0.2.0` 化で失敗・偽陽性化することが判明した。`setup_installed_repo()` へ任意の `source_dir` 引数を追加し、これら 3 テストを明示的な `version="0.1.0"` 起点へ修正する。

### 2. 作業ブランチと統合ブランチ（`main`）の切り分け手順

`docs/03.spec/08.adoption-and-migration.md`（4.2 節）の 4 段階および `update.py` の事前ガード（統合ブランチ上かつ作業ツリークリーン）を満たすため、以下の 2 段構成で進める。

1. **作業ブランチ（`feature/20261127-124457-ticket-release-v0-2-0-and-latest-branch`）：リリース準備（段階 2 相当）**
   * `template/management/aico-manifest.json`（`aico_version`）・`installer/install.py`・`installer/upgrade.py`（`AICO_VERSION`）を `"0.2.0"` へ更新する。
   * `installer/migrations/README.md` の未配置理由を `v0.2.0` 時点の実態へ更新する。
   * `CHANGELOG.md` へ `## [v0.2.0] - 2026-11-27` エントリを追記する（変更内容・変更意図・移行要否と移行手順・検証済み環境および未確認環境）。
   * `tests/helpers.py`・`tests/test_lifecycle.py` のバージョン依存箇所を恒久修正し、配布原本 3 箇所のバージョン一致を自動検証する単体テストを追加する。
   * Linux・Windows 11 VM（管理者権限＋`gsudo -i Medium` 一般権限）で全テスト通過を確認し、独立レビュー（`aico-review`）および採用指摘修正・独立再確認（`aico-review-recheck`）を完了する（作業ブランチ上ではルート運営領域を一切変更しない）。
   * リリース準備変更をコミットしたうえで、**`main` へマージする前に**作業ブランチ上で `uv run management/scripts/update_changed_files.py --ticket 20261127-124457-ticket-release-v0-2-0-and-latest-branch` を実行してチケット `index.md` の `## 変更ファイル` を反映・コミットし、その状態で `main` へマージする。
2. **統合ブランチ（`main`）：自己適用検証・タグ発行・`latest` 作成・クローズ（段階 3〜4 相当）**
   * `main` 上で `tools/aico.sh update --source .` を実行し、AIco 本体運営領域を `0.1.0` → `0.2.0` へ移行する。
   * `tools/aico.sh doctor --strict --json`（`OK=9 / WARN=0 / ERROR=0`）および Linux・Windows 11 VM（管理者＋`gsudo -i Medium` 一般権限）での全自動テスト通過を確認し、**タグ発行前に段階 3 の実測結果（テスト件数・`doctor --strict` 結果・ランタイムバージョン等）が `CHANGELOG.md` の「検証済み環境」記載と一致し変化がないことを確認**したうえで、自己適用差分を `main` へコミットする（不一致や異常を検知した場合は `08.adoption-and-migration.md` 4.2 節に従い自己適用差分をロールバックして原因を見直す）。
   * 自己適用コミットに対し注釈付きタグ `v0.2.0`（`git tag -a v0.2.0 -m "Release v0.2.0"`）と同一コミットを指す fast-forward 専用ブランチ `latest`（同名タグは作成しない）を作成し、`origin`（GitLab）へ `main`・`latest`・`v0.2.0` をプッシュする。
   * GitLab ミラー設定による GitHub（`https://github.com/sasaki819/AIco.git`）への反映を確認する（`git ls-remote` 等で `v0.2.0` タグおよび `latest` ブランチを確認）。
   * 全 4 AC の実物確認完了後、チケットを `done` へ確定し一覧・ダッシュボードを再生成して `main` へ反映する（この際、`main` 上では `main...HEAD` 差分が 0 件となるため `update_changed_files.py` を再実行しない）。

### 3. 対象外・制約

* 作業ブランチ内でルート運営領域（`management/scripts/`・`.agents/`・ルート `AGENTS.md` 等）を手作業で改造しない（必ず `main` 上の `tools/aico.sh update --source .` で自己適用する）。
* `latest` ブランチと同名のタグは作成しない。
* `git commit`・`git push`・`git tag`・`latest` ブランチ作成は各節目で人間承認を得てから実施する。

## ステップ一覧

* [x] ステップ 1：`tests/helpers.py`（`make_source_copy` の `AICO_VERSION` 正規表現置換化・`setup_installed_repo` への `source_dir` 引数追加）および `tests/test_lifecycle.py`（アップグレード系 3 テストの明示 `0.1.0` 起点化および配布原本 3 箇所のバージョン一致検証テスト追加）を修正する。
* [x] ステップ 2：`template/management/aico-manifest.json`・`installer/install.py`・`installer/upgrade.py` のバージョンを `0.2.0` へ更新し、`installer/migrations/README.md` を実態に合わせて更新する。
* [x] ステップ 3：`CHANGELOG.md` へ `v0.2.0` の変更履歴（変更内容・変更意図・移行要否と手順・検証済み／未確認環境）を追記する。
* [x] ステップ 4：作業ブランチ上で Linux および Windows 11 VM（管理者権限・`gsudo -i Medium` 一般権限）の全自動テストと `doctor.py` を確認し、独立レビュー（`aico-review`）および指摘修正・独立再確認（`aico-review-recheck`）を完了する。
* [ ] ステップ 5：作業ブランチ上でリリース準備変更をコミット後に `management/scripts/update_changed_files.py` を実行して `index.md` の `## 変更ファイル` を反映・コミットしたうえで `main` へマージする。その後 `main` 上で `tools/aico.sh update --source .` を実行し、`tools/aico.sh doctor --strict --json`（`OK=9 / WARN=0 / ERROR=0`）および Linux・Windows 11 VM 全テスト通過・`CHANGELOG.md` の検証済み環境記載との一致（異常・不一致がないこと）を確認して自己適用差分をコミットする。
* [ ] ステップ 6：自己適用コミットに注釈付きタグ `v0.2.0` と `latest` ブランチを作成して `origin` へプッシュし、GitHub 公開ミラーへの `v0.2.0` タグおよび `latest` ブランチ反映を確認する。
* [ ] ステップ 7：全 4 AC・DoD を実物照合してチケットをクローズし、一覧・ダッシュボードを再生成する（`main` 上では `update_changed_files.py` を再実行しない）。

## 検証方針

* **作業ブランチ検証（段階 2）**：
  * Linux：`uv run -m unittest discover -s tests -v` 全件通過、`uv run management/scripts/doctor.py --json` `OK=9 / WARN=0 / ERROR=0`。
  * Windows 11 VM（`ssh win11`）：管理者権限で全件 `ok`、`gsudo -i Medium` 一般権限でシンボリックリンク境界検査 2 件のみ明示 `skipped`・他全件 `ok`。
  * 独立コンテキストによる `aico-review`（必要に応じて修正・再確認）。
  * マージ前に作業ブランチ上で `management/scripts/update_changed_files.py` を実行し、`index.md` の `## 変更ファイル` へ変更対象プロジェクト資産が反映されることを確認する。
* **統合ブランチ自己適用後検証（段階 3）**：
  * `tools/aico.sh update --source .` が例外フラグなしで終了コード `0`・エラー／警告 0 件で完了すること。
  * `tools/aico.sh doctor --strict --json` が `OK=9 / WARN=0 / ERROR=0` で通過すること。
  * Linux および Windows 11 VM（管理者権限・`gsudo -i Medium` 一般権限）で全自動テストが通過すること。
  * タグ発行前に、上記の実測結果（テスト件数・`doctor --strict` 結果・ランタイムバージョン等）が `CHANGELOG.md` の「検証済み環境」記載と一致し変化がないことを確認すること（不一致・異常があればロールバックして原因を見直す）。
* **公開確認（段階 4）**：
  * `git ls-remote` で開発元（GitLab `origin`）および公開ミラー（GitHub `https://github.com/sasaki819/AIco.git`）に `refs/tags/v0.2.0` と `refs/heads/latest` が同一コミットで存在することを確認する。

## 判断ログ

* **2026-11-27（`v0.1.0` → `v0.2.0` マイグレーション不要の確定）**：一時クローン上で `0.2.0` 自己適用と `doctor --strict` を事前リハーサルし、`OK=9 / WARN=0 / ERROR=0` でエラー・警告なしであることを実物確認したため、マイグレーションスクリプトは追加しない方針とした。
* **2026-11-27（テストのバージョン非依存化を本チケットに包含）**：`0.2.0` への版上げに伴い `tests/helpers.py` および `tests/test_lifecycle.py` の `0.1.0` 暗黙依存が顕在化したため、AC3 達成の一環として本チケット内で恒久修正する方針とした。
* **2026-11-27（リリース準備と自己適用・タグ発行の 2 段構成）**：`update.py` の統合ブランチガードと `docs/03.spec/08.adoption-and-migration.md` 4.2 節を厳守するため、リリース準備を作業ブランチでレビュー・マージした後に `main` で自己適用・タグ・`latest` 発行を行い、全 AC 実物確認後にチケットをクローズする方針とした。
* **2026-11-27（`design` フェーズの省略・`v0.2.0` 版番の確定）**：新規設計書の作成はなく既存リリース仕様に沿った実施とテスト修正のみであるため `design` を省略して `implementation / working` へ直接遷移する方針で合意。また `08.adoption-and-migration.md` 4.1 節の MINOR 基準（CLI オプション追加・マニフェスト任意項目追加・テンプレートおよびガイド拡充等）に基づき `v0.2.0` としてリリースすることを合意した。
* **2026-11-27（初回レビュー指摘 001・003 の計画反映）**：マージ前の作業ブランチ上で `update_changed_files.py` を実行して `## 変更ファイル` を反映する手順（`main` 上クローズ時は再実行しない）と、段階 3 の本番自己適用・再テスト完了後かつタグ発行前に実測結果が `CHANGELOG.md` の検証済み環境記載と一致していることを確認するチェックステップ（不一致・異常時はロールバックして見直し）を追記した。
