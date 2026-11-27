# Changelog

AIco のバージョン履歴を記録する。バージョニングはセマンティックバージョニング（`MAJOR.MINOR.PATCH`、Git タグ `vMAJOR.MINOR.PATCH`）に従う。

## [v0.2.0] - 2026-11-27

### 変更内容

* **初見ユーザー向けガイド整備とマニュアル構成刷新**
  * `docs/04.user-guide/` および `template/management/01.manual/` を 5 冊構成（`01.getting-started.md`・`02.tutorial.md`・`03.cheatsheet.md`・`04.user-guide.md`・`05.worker-models.md`）へ拡充・完全一致同期し、旧 `getting-started.md`・`workflow-reference.md` を廃止した。
  * `README.md` および `template/AGENTS.md` の導入・ユーザーガイド導線を刷新した。
* **導入・初期設定ツールとエージェント同期の UX 改善**
  * `installer/install.py` に導入から初期設定まで連続実行できる `--init` ショートカットオプションを追加した。
  * `template/management/scripts/init.py` に `--pr-template` オプションを追加し、`aico-manifest.json` の任意項目 `pr_template`・PR/MR テンプレート雛形（`template/management/templates/pr-template.md`）・`aico-ticket-pr` スキルの `pr_template` 参照対応を整備した。あわせてテキストモード出力時の WARN 重複および標準出力／標準エラー出力の分離を修正した。
  * Antigravity および GitHub Copilot 向けのワーカー定義出力仕様（`template/management/scripts/_lib/agents_sync.py`）を最新ツール仕様へ整合した。
* **レビューフロー・クローズ手順・品質ゲート・AI 進行案内の改善**
  * `aico-review` スキルおよび `create_review_finding.py` で、独立ワーカーレビューに加えて人間レビュー指摘の記録にも対応した。
  * `template/AGENTS.md` および各スキルに進行案内・番号付き選択肢提示・行動ガードレール（スコープ外修正禁止、検証前チェック禁止、最小コンテキスト読み込み）を追加した。
  * `template/management/scripts/doctor.py` に完了チケットの未チェック AC 検知、見送り指摘（`status: cancelled`）の理由空欄検知、`pr_template` のリポジトリ外参照・シンボリックリンク境界検査などの品質ゲートを追加した。
  * `update_changed_files.py` を既定で未コミット／未追跡変更も取り込む仕様（`--committed-only` オプション追加）へ改善し、状態遷移ルールの正規化（同一フェーズ複数ラウンドの `re-reviewing` → `reviewing`、調査専用 `planning` → `closing` 等）、自動生成マーカー前後の空行規約および Markdown 強制改行（末尾半角スペース 2 個）を整備した。
* **Windows ネイティブ環境の改行・テスト・シンボリックリンク互換性対応**
  * リポジトリルートへ `.gitattributes` を新設し、Markdown・Python・JSON・シェルスクリプト・TOML 等を LF、`.bat` を CRLF に統一した。
  * `installer/install.py`・`installer/upgrade.py` のファイル配布処理に改行正規化（テキスト資産は LF、`tools/aico.bat` は CRLF）を導入した。
  * 自動テストスイート（`tests/`、計 38 テスト）を Windows ネイティブ環境（`tools/aico.bat`、`WinError 1314` 時の明示スキップ、`git`・`uv` 同居環境耐性、UTF-8 `.cmd` シム）、将来の版上げに依存しない構成、および配布原本 3 箇所のバージョン一致検証へ拡充した。

### 変更意図（なぜ変更したか）

* 初見ユーザーが迷わず導入から最初の 1 チケット完走まで到達できるよう、導入手順・ガイド構成・AI の進行案内を一貫して分かりやすくするためである。
* 人間レビュー指摘の受け皿や完了前品質ゲートを仕組みとして組み込み、協業ワークフローの抜け漏れ防止と使いやすさを両立するためである。
* Windows PowerShell および Git for Windows 既定設定（`core.autocrlf=true`）環境でも、Linux と同様に導入・初期設定・診断・自動テストが一貫して動作するクロスプラットフォーム互換性を確保するためである。

### 移行要否と具体的な移行手順

* **移行要否**：マイグレーションスクリプト不要（既存記録や設定ファイルの構造変換を伴わない後方互換の MINOR アップデート。新規任意項目 `pr_template` は未設定時に `""` として扱われる）。
* **`v0.1.0` からのアップデート手順**：導入先プロジェクトの統合ブランチ（作業ツリーがクリーンな状態）で以下を実行する。
  1. `tools/aico.sh update`（Windows は `tools\aico.bat update`）を実行し、AIco 由来領域（`AGENTS.md` マーカー内・スキル・スクリプト・マニュアル・テンプレート）を `v0.2.0` へ更新する。
  2. `tools/aico.sh doctor`（または `tools/aico.sh doctor --strict`）で `ERROR` 0 件を確認し、更新差分をコミットする。
  3. 任意で PR/MR テンプレートを利用する場合は `tools/aico.sh init --pr-template .github/pull_request_template.md` 等を実行する。
* **新規導入手順**：導入先プロジェクトの Git リポジトリルートで以下を実行する。
  1. `uv run --refresh https://raw.githubusercontent.com/sasaki819/AIco/latest/installer/install.py`（特定版固定時は `latest` を `v0.2.0` へ置換）を実行する。
  2. `tools/aico.sh init`（Windows は `tools\aico.bat init`）で初期設定・ツール同期・診断を実施し、初回コミットを行う。

### 検証済み環境および未確認環境

* **検証済み環境**
  * **Linux**：Python 3.14.4 / `uv` 0.13.8 / Git 2.53.0（自動テスト 38/38 OK、AIco 本体への `v0.1.0` → `v0.2.0` ドッグフーディング自己適用および `doctor --strict` `OK=9 / WARN=0 / ERROR=0`）
  * **Windows 11（PowerShell / `core.autocrlf=true`）**：Python 3.15.2 / `uv` 0.13.10 / Git 2.56.1.windows.1（管理者権限：自動テスト 38/38 OK、通常ユーザー権限 `gsudo -i Medium`・開発者モード OFF：36 ok / 2 skipped、`tools\aico.bat` および CRLF 配布正規化・フレッシュクローン検証を含む）
* **未確認環境**
  * macOS 実機での動作確認
  * 各 AI ツール実機（Claude Code / Codex / Antigravity / GitHub Copilot）すべてを横断したワーカー委譲・同期資産の網羅的実機確認

## [v0.1.0] - 2026-11-24

### 変更内容

* **配布テンプレート（`template/`）の新規整備**
  * ルートコンテキスト雛形（`AGENTS.md`・`CLAUDE.md`）および人用ラッパー（`tools/aico.sh`・`tools/aico.bat`）を実装した。
  * 初期マニフェスト（`management/aico-manifest.json`）、ダッシュボード／各区分 `index.md`、利用マニュアル（`01.manual/`）、記録・ワーカーテンプレート（`templates/`）を整備した。
* **標準21スキル（`template/.agents/skills/aico-*/SKILL.md`）の新規実装**
  * 共通・運用系4スキル、記録・手順系4スキル、チケット系9スキル、レビュー系4スキルの計21スキルを整備した。
* **運用スクリプト群（`template/management/scripts/`）の新規実装**
  * Python 標準ライブラリのみで動作する共通ライブラリ（`_lib/` 13モジュール）、ランチャー（`_launcher.py`）、日常運用15スクリプト（記録作成7本・レビュー履歴・frontmatter検証更新・変更ファイル一覧・一覧再生成・チケット照会・アーカイブ＆双方向リンク追従・エージェント同期・7カテゴリ総合診断 `doctor.py`）、および設定／更新入口（`init.py`・`update.py`）を実装した。
* **導入・アップデート・マイグレーション基盤（`installer/`）の新規実装**
  * スタンドアロン導入スクリプト（`installer/install.py`）、段階的アップデート・連鎖マイグレーションエンジン（`installer/upgrade.py`）、およびマイグレーション規約（`installer/migrations/README.md`）を実装した。
* **自動テストスイート（`tests/`）の新規実装**
  * `_lib/` 単体テスト、日常運用15スクリプト＋ラッパーの結合テスト、および導入・設定・アップデート・複数版連鎖マイグレーションの結合テスト（計25テスト）を整備した。

### 変更意図（なぜ変更したか）

* AI エージェントと人間が協働するプロジェクトにおいて、議論・意思決定（ADR）・タスク実行（チケット）・定型手順（Runbook）・独立レビューを一貫した規約で継続運用し、複数 AI ツール（Claude Code / Codex / Antigravity / GitHub Copilot）間で迷わず再現可能にするための初版実装を行うためである。
* 導入先リポジトリの既存資産を破壊せず安全に導入・カスタマイズ・バージョンアップできるよう、配布原本（`template/`）・導入移行エンジン（`installer/`）・運営領域を分離した構成とした。

### 移行要否と具体的な移行手順

* **移行要否**：不要（初版リリースのため移行元バージョンは存在しない）。
* **新規導入手順**：導入先プロジェクトの Git リポジトリルートで以下を実行する。
  1. `uv run https://raw.githubusercontent.com/sasaki819/AIco/v0.1.0/installer/install.py`（またはローカルクローンから `python3 /path/to/aico/installer/install.py`）を実行して初期資材を配置する。
  2. `tools/aico.sh init`（Windows は `tools\aico.bat init`）を実行し、統合ブランチ・利用ツール・配布元 URL・`worker_models` を設定・同期する。
  3. `tools/aico.sh doctor` で `ERROR` 0件を確認して初回コミットを行う。

### 検証済み環境および未確認環境

* **検証済み環境**
  * OS / ランタイム：Linux / Python 3.14.4 / `uv` 0.13.8 / Git 2.53.0
  * 検証範囲：自動テスト25件全通過（`uv` なし Python 直接フォールバック・日本語および空白を含むパス・ローカル clone／`.git` なしアーカイブ／模擬リモート Git の3系統・複数版連鎖マイグレーションを含む）、および AIco 本体への初回ドッグフーディング自己適用＋`doctor` 診断
* **未確認環境**
  * Windows 実機での `tools/aico.bat` 実行および改行・文字コード動作確認
  * 各 AI ツール実機（Claude Code / Codex / Antigravity / GitHub Copilot）での `AGENTS.md`・スキル・ワーカー定義の実際の読込・委譲動作確認
