# Getting Started（初期設定と最初の運用）

## 概要

AIco の資材配置（`install.py`）完了後に、プロジェクト固有設定を行い運用を開始するまでの手順を示す。  
本マニュアルでは以下の流れを扱う。

* 初期設定とツール同期（`init`）
* `AGENTS.md` へのプロジェクト固有規約の追記
* 導入診断と日常運用の開始
* アップデート方法

## 1. 初期設定とツール同期

プロジェクトルートで以下を実行し、統合ブランチ・利用ツール・配布元リポジトリ・ワーカーモデルを設定する。

```bash
tools/aico.sh init
```

Windows 環境では `tools/aico.bat init` を使用する。  
非対話で設定する場合はオプションを指定できる。

```bash
tools/aico.sh init --integration-branch main --tools claude,codex
```

`worker_models`（`high` / `middle` / `low` ごとの `model` と `effort`）は `management/aico-manifest.json` を直接編集したうえで `tools/aico.sh sync_agents` を実行して反映してもよい。

## 2. プロジェクト固有規約の追記

プロジェクトルートの `AGENTS.md` において、`<!-- AICO:BEGIN -->` 〜 `<!-- AICO:END -->` の**外側**へ、以下のプロジェクト固有情報を追記する。

* ビルド・テスト・リントの実行方法
* 作業ブランチ命名規約（未記載時の参考例：`feature/<チケットID>`）
* Git worktree 等の並列実行方針（利用する場合）
* レビューを実施するフェーズ基準や承認ルール

AIco 由来領域（マーカー内・`aico-*` スキル・`management/scripts/` 等）は直接改造せず、標準方針を上書きしたい場合もマーカー外へ理由とともに明記すること。

## 3. 導入診断と運用開始

設定完了後に診断コマンドを実行し、`ERROR` が 0 件であることを確認する。

```bash
tools/aico.sh doctor
```

利用する AI ツールで `AGENTS.md` と `aico-*` スキルが読み込まれることを確認してから初回コミットを行う。  
日常運用では、相談から始める場合は `aico-discuss`、タスクを起票する場合は `aico-create-ticket`、現在地の確認には `aico-ticket-status` を使用する。

## 4. アップデート

AIco 本体の新版を取り込む際は、統合ブランチ上のクリーンな作業ツリーで以下を実行する。

```bash
tools/aico.sh update --check
tools/aico.sh update
```

事前に変更内容を確認したい場合は `--dry-run` を併用する。
