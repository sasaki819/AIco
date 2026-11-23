# Changelog

AIco のバージョン履歴を記録する。バージョニングはセマンティックバージョニング（`MAJOR.MINOR.PATCH`、Git タグ `vMAJOR.MINOR.PATCH`）に従う。

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
