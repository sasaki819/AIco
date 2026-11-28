# 作業計画

## 合意した仕様

### 1. リポジトリ `.gitattributes` 整備と配布時改行正規化

* AIco リポジトリルートに `.gitattributes` を新規配置し、`*.md`・`*.json`・`*.py`・`*.sh`・`*.toml` を `text eol=lf`、`*.bat` を `text eol=crlf` とする。
* `installer/install.py` および `installer/upgrade.py`（`_mirror_tree` を含む）で配布するテキスト資産（`.md`・`.py`・`.json`・`.sh`・`.toml`・`.txt`・`.yml`・`.yaml` 等）を明示的に LF 正規化して書き出し、配布元が CRLF で展開されている場合でも導入先の `doctor.py` LF 規約を満たすようにする。
* `installer/install.py` および `installer/upgrade.py` が配置・更新する `tools/aico.bat` は明示的に CRLF（`\r\n`）で書き出し、`cmd.exe` でのブロックパース安定性および推奨 `.gitattributes`（`*.bat text eol=crlf`）と整合させる。
* `docs/04.user-guide/01.getting-started.md` および `template/management/01.manual/01.getting-started.md` の推奨 `.gitattributes` 例へ `*.toml text eol=lf` を追記して完全一致同期を保つ。

### 2. テストスイートの Windows ネイティブ対応

* `tests/helpers.py` に OS 切替ヘルパー `run_wrapper` を追加する（POSIX は `bash tools/aico.sh`、Windows は `cmd /d /c call tools/aico.bat`）。
* `tests/test_lifecycle.py`（カスタム `management_root` での `init`・再 `init`・非 TTY `--dry-run`）および `tests/test_daily_scripts.py`（日本語と空白を含むパス・非 TTY メニュー・未知コマンド終了コード `2`・`uv` 不在フォールバック）を `run_wrapper` 経由へ移行し、Windows でも `tools/aico.bat` で等価検証する。
* Windows の `uv` 不在フォールバック検証は `symlink_to()` を使わず、`uv` を除外した `PATH` で `tools/aico.bat doctor --json` を実行し、`uv コマンドが見つかりません` 警告付きで終了コード `0` となることを検証する。
* `tests/` 配下の `write_text()` で `newline="\n"` が未指定の箇所へ `newline="\n"` を明記する。

### 3. シンボリックリンク境界検査テストの分離と一般権限対応

* `tests/test_lifecycle.py`（`init.py` の `pr_template` リポジトリ外シンボリックリンク拒否）および `tests/test_daily_scripts.py`（`doctor.py` の `pr_template` リポジトリ外シンボリックリンク検知）のシンボリックリンク境界検査をそれぞれ独立したテストメソッドへ分離する。
* Windows 一般権限（開発者モード OFF かつ非管理者権限）で `symlink_to()` が `OSError`（`winerror == 1314`）を送出した場合のみ、開発者モード ON または管理者権限での実行案内を添えて `self.skipTest(...)` とする。

### 4. 対象外・制約

* AIco 本体運営領域（`management/scripts/`・`.agents/`・ルート `AGENTS.md` 等）はリリース前の自己適用（`tools/aico.sh update --source .`）で反映する方針のため、本作業ブランチ内で直接改造しない。
* 導入先プロジェクトの `.gitattributes` の自動作成・上書きは行わない（導入先独自設定を侵食しない原則を維持する）。

## ステップ一覧

* [x] ステップ 1：AIco リポジトリルートに `.gitattributes` を作成し、対象ファイル種別の改行規約（LF / `.bat` は CRLF）を定義する。
* [x] ステップ 2：`installer/install.py`・`installer/upgrade.py` の配布処理を改修し、テキスト資産の LF 正規化および `tools/aico.bat` の CRLF 出力と関連テスト（CRLF ソースからの配布正規化・べき等性）を追加する。
* [x] ステップ 3：`tests/helpers.py` に `run_wrapper` を追加し、`tests/test_lifecycle.py`・`tests/test_daily_scripts.py` のラッパー検証および `uv` 不在フォールバックを Windows ネイティブ（`tools/aico.bat`）対応へ改修する。
* [x] ステップ 4：`init.py`・`doctor.py` の `pr_template` シンボリックリンク境界検査を独立テストメソッドへ分離して `WinError 1314` 時の明示 `skipTest` を実装し、`tests/` 内の `write_text` へ `newline="\n"` を統一する。
* [x] ステップ 5：`docs/04.user-guide/01.getting-started.md`・`template/management/01.manual/01.getting-started.md` の推奨 `.gitattributes` 例を同期更新し、必要に応じて `docs/03.spec/` との整合を確認・反映する。
* [x] ステップ 6：Linux 環境で全自動テスト（`python3 -m unittest discover -s tests -v`）および `uv run management/scripts/doctor.py --json` の通過を確認する。
* [x] ステップ 7：Windows PowerShell 実機環境（`core.autocrlf=true`）で自動テスト全件（一般権限での完走および開発者モード ON または管理者権限でのシンボリックリンク境界検査通過）を実機確認する。

## 検証方針

* **Linux 自動検証**：
  * `python3 -m unittest discover -s tests -v` が全件 `ok`（`skipped=0`）で通過すること。
  * CRLF 改行を含む擬似ソースから `install.py`・`upgrade.py` を実行した際に、配布された Markdown・Python・JSON 等が LF 正規化され、`tools/aico.bat` が CRLF で出力され、同版再実行時の `changed_files` が空になることを自動テストで検証すること。
  * `uv run management/scripts/doctor.py --json` が `ERROR=0`・`WARN=0` で通過すること。
* **Windows PowerShell 実機検証（人間環境と照合）**：
  * `core.autocrlf=true` 環境で本ブランチの最新内容を取得し、`uv run -m unittest discover -s tests -v` で `FAIL=0`・`ERROR=0` を確認すること（一般権限ではシンボリックリンク境界検査 2 件のみ理由付き `skipped`、他全件 `ok`）。
  * 開発者モード ON または管理者権限の PowerShell で `uv run -m unittest discover -s tests -v` を実行し、シンボリックリンク境界検査 2 件を含む全件が `ok` で通過することを確認すること。
* **レビュー方針**：
  * 実装および Linux / Windows 検証の完了後に `aico-review` で独立コンテキストによるレビューを実施する。

## 判断ログ

* **2026-11-26（改行正規化の二段構え）**：AIco リポジトリへの `.gitattributes` 追加だけでなく、`installer/install.py`・`installer/upgrade.py` でも配布時改行正規化（テキストは LF、`tools/aico.bat` は CRLF）を行う方針で合意。アーカイブ展開や `.gitattributes` を持たない模擬リモートからの `git clone` 時でも導入先で確実に LF 規約と `cmd.exe` の安定性を維持できるため。
* **2026-11-26（シンボリックリンク境界検査のテスト分離）**：`pr_template` リポジトリ外シンボリックリンク境界検査を独立テストメソッドへ分離し、`WinError 1314` 発生時のみ `skipTest` とする方針で合意。一般権限 Windows 環境で既存の非シンボリックリンク検証まで巻き込んでスキップされる事態を防ぐため。
* **2026-11-26（Windows ラッパー検証範囲）**：`tests/helpers.py` の OS 切替ヘルパーを通じて、カスタム `management_root`・日本語と空白を含むパス・非 TTY・未知コマンド終了コード `2`・`uv` 不在フォールバックの全ケースを Windows でも `tools/aico.bat` で等価検証する方針で合意。
* **2026-11-26（`design` フェーズの省略）**：既存仕様（`docs/03.spec/07.scripts.md`・`08.adoption-and-migration.md`）に沿った互換性修正およびテスト整備であり新規設計書は不要なため、`design` を省略して `implementation / working` へ直接遷移する方針で合意。
