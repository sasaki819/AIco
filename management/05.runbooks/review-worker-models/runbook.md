---
id: review-worker-models
title: worker_models おすすめ設定見直し手順
created: 2026-11-28 01:21:16
updated: 2026-11-28 01:21:16
---

# worker_models おすすめ設定見直し手順

## 概要

[docs/04.user-guide/05.worker-models.md](../../../docs/04.user-guide/05.worker-models.md) および配布コピー [template/management/01.manual/05.worker-models.md](../../../template/management/01.manual/05.worker-models.md) に掲載する 4 ツール別おすすめ `worker_models` 設定例が陳腐化しないよう、定期的に見直し・更新するための手順書である。

主要 AI ツールの新モデル公開時、現行推奨モデルの廃止・名称変更時、または四半期ごとなどの定期見直し時に `aico-runbook-run` で実施する。

## 前提条件

* 現在の Git ブランチが統合ブランチ（`main`）であり、作業ツリーがクリーンであること。
* `uv`（または Python 3.11 以上）および `git` が実行可能であること。
* 対象 4 ツール（Claude Code・Codex・Antigravity・GitHub Copilot）のモデル・`effort` 仕様を確認できること（実機環境または公式ドキュメント参照環境）。
* **公開リポジトリ・GitHub ミラーの境界ルール（必守）**：
  * 本リポジトリは GitHub 公開リポジトリへミラーされるため、手元のベンチマーク比較資料（個人管理リポジトリや再配布不可の外部ベンチマーク生データ等）は、メンテナ内部の選定判断の参考にとどめる。
  * 本手順書・実施記録（`management/05.runbooks/review-worker-models/records/<実施記録ID>/` 配下の本文および添付物）・公開ドキュメントには、**非公開リポジトリ URL および再配布不可のベンチマーク生数値（スコア表・生データ等）を一切記載・添付しない**。
  * 記録および公開してよい情報は、推奨モデル ID、`effort` 値、定性的な選定理由（推論力優先・速度とコストのバランス等）、および各ツール公式確認手段による動作確認結果に限定する。

## 入力

* **実施日**（`YYYY-MM-DD`）：ガイドの `最終確認日` および見出し日付に反映する基準日。
* **現行のおすすめ設定ガイド**：[docs/04.user-guide/05.worker-models.md](../../../docs/04.user-guide/05.worker-models.md) および [template/management/01.manual/05.worker-models.md](../../../template/management/01.manual/05.worker-models.md)。
* **現行のワーカー同期実装（配布原本）**：[template/management/scripts/_lib/agents_sync.py](../../../template/management/scripts/_lib/agents_sync.py) および `EFFORT_SUPPORTED_TOOLS` を定義する [template/management/scripts/_lib/manifest.py](../../../template/management/scripts/_lib/manifest.py)（各ツールの出力キー・`effort` 対応仕様の照合用）。
* **現行の AIco 本体マニフェスト**：[management/aico-manifest.json](../../aico-manifest.json)（任意反映の判断用）。
* **見直し参考情報**：各ツール公式ドキュメント・実機確認結果、および必要に応じたメンテナ手元の内部比較資料（公開境界ルールに従い記録へは転記しない）。

## 手順

※ Windows 環境で実施する場合は、以降の手順および完了条件に記載の `tools/aico.sh` を `tools\aico.bat` に読み替えて実行する。

### 1. 実施記録の作成と現行仕様の確認

* `aico-runbook-run` に従い、`create_runbook_record.py` で実施記録フォルダを作成する（初期状態は `status: in-progress`）。
* [docs/04.user-guide/05.worker-models.md](../../../docs/04.user-guide/05.worker-models.md)、[template/management/scripts/_lib/agents_sync.py](../../../template/management/scripts/_lib/agents_sync.py)、および [template/management/scripts/_lib/manifest.py](../../../template/management/scripts/_lib/manifest.py) を確認し、現行の 4 ツール別モデル設定・`effort`・出力キー仕様を把握する。

### 2. 対象 4 ツールの最新モデル・`effort` 仕様の確認

* 下表の観点に従い、対象 4 ツールすべての利用可能モデル ID・エイリアス・`effort`（推論強度）仕様および非推奨・廃止予定の有無を確認する。実機確認できないツールがある場合は、公式ドキュメント確認にとどまった旨を未確認事項として実施記録へ明記する。

| ツール | 出力先・キー仕様 | 確認方法 | 確認時の注意点 |
| :--- | :--- | :--- | :--- |
| **Claude Code** | `.claude/agents/worker-{level}.md`<br>・`model`<br>・`effort` | セッション内の `/model` および公式ドキュメント | 公式エイリアス（`opus`・`sonnet`・`haiku`）の有効性と最新世代との対応を確認する（特定版固定が必要な場合のみ明示 ID を検討する） |
| **Codex** | `.codex/agents/worker-{level}.toml`<br>・`model`<br>・`model_reasoning_effort` | ターミナルで `codex debug models` および公式ドキュメント | 利用可能なモデル ID と `model_reasoning_effort` の有効値（`high`・`medium`・`low` 等）を確認する |
| **Antigravity** | `.agents/agents/worker-{level}.md`<br>・`model`<br>・`effort` は未使用（`""`） | 公式ドキュメントおよび現行アダプタ仕様 | サブエージェントは抽象ティア（`pro`・`flash`・`flash_lite`・`inherit`）のみ受理し、具体モデル ID は指定不可であることを確認する |
| **GitHub Copilot（VS Code）** | `.github/agents/worker-{level}.agent.md`<br>・`model`<br>・`reasoning-effort` | VS Code で `.github/agents/worker-high.agent.md` の `model:` 行にて入力補完（Ctrl+Space）および公式ドキュメント | ランタイムモデル ID の表記ゆれ（ドット区切り等）と `reasoning-effort` の対応状況を確認する |

* ツール側の仕様変更により `template/management/scripts/_lib/agents_sync.py` 等のコード改修が必要と判明した場合は、本 Runbook 内でコードを直接変更せず、`異常時の対応` に従って別チケットを起票して引き継ぐ。

### 3. 3 段階ワーカー別おすすめ設定案の策定と人間合意

* 3 段階ワーカーの役割（`worker-high`：精度と推論力を最優先、`worker-middle`：精度・速度・コストのバランス、`worker-low`：速度とコストを優先）に基づき、4 ツール × 3 段階の更新案（または現行維持案）を策定する。
* 現行設定との差分一覧および定性的な選定理由を人間へ提示し、採用内容の承認を得る。
* 見直しの結果「現行維持」と判断した場合は、ガイドの `最終確認日`・見出し日付のみ実施日へ更新するか、ガイドは変更せず実施記録のみに確認済み根拠を残すかを人間へ確認する。
* あわせて、AIco 本体自身の [management/aico-manifest.json](../../aico-manifest.json) の `worker_models` も今回のおすすめ設定へ反映するか（または据え置くか）を人間へ確認する。

### 4. ガイド 2 ファイルの更新と完全一致同期（ガイド更新または日付更新を行う場合）

* [docs/04.user-guide/05.worker-models.md](../../../docs/04.user-guide/05.worker-models.md) を更新する。
  * `最終確認日：YYYY-MM-DD` および見出し `## ツール別おすすめ設定（YYYY-MM-DD 時点）` を実施日へ更新する。
  * ツール別おすすめ設定表・`management/aico-manifest.json` 記入例（JSON コピペ用）・補足説明・確認ヒントのすべてを整合させる。
  * ユーザーガイドの文体は既存の**敬体（です・ます調）**を維持し、常体と混在させない。
  * UTF-8（BOM なし）・LF・強制改行の行末半角スペース 2 個・禁止語不使用など `aico-markdown-write`（文体以外の共通品質規約）および `tests/test_user_guide.py` の品質条件を満たすことを確認する。
* 更新後の内容を配布コピー [template/management/01.manual/05.worker-models.md](../../../template/management/01.manual/05.worker-models.md) へバイト単位で完全一致するよう反映する。
* AIco 本体ルートの `management/01.manual/05.worker-models.md` はリリース時の自己適用（`tools/aico.sh update --source .`、内部で `upgrade.py` へ委譲）で更新される領域であり、本 Runbook では直接手動編集しない。

### 5. 自動テストおよび `doctor` 検証

* 以下のコマンドを実行し、全テスト通過（特に `tests/test_user_guide.py` による完全一致同期・文字コード/LF・禁止語・Markdown 構造・リンク自己完結の検証）を確認する。あわせて `tools/aico.sh doctor` で `ERROR=0` であること、および警告が出る場合は手順 7 の一覧再生成前による `management/05.runbooks/index.md` の鮮度ドリフトのみであることを確認する。

```bash
uv run -m unittest discover -s tests -v
tools/aico.sh doctor
```

### 6. AIco 本体 `management/aico-manifest.json` への任意反映（手順 3 で更新合意した場合のみ）

* [management/aico-manifest.json](../../aico-manifest.json) の `worker_models` を承認済みの設定へ更新する。
* 以下のコマンドを実行し、AIco 本体リポジトリ内の各ツール用ワーカー定義へ反映したうえで、`ERROR=0` および手順 7 前の一覧鮮度ドリフト以外の警告がないことを検証する。

```bash
tools/aico.sh sync_agents
tools/aico.sh doctor
```

* 反映を見送る（据え置く）判断とした場合は、その判断理由を実施記録へ明記する。

### 7. 公開境界チェック・実施記録の確定と一覧再生成

* `git diff` および実施記録フォルダ配下の全ファイルを目視確認し、非公開リポジトリ URL および再配布不可のベンチマーク生数値が一切含まれていないことを検証する。
* 実施記録へ確認した実行環境・未確認事項・定性的な選定理由・テストおよび `doctor` の結果・`aico-manifest.json` 反映有無を記録し、人間承認後に `update_frontmatter.py` で実施記録の `status` を `done` へ更新する。
* 以下のコマンドで一覧を再生成し、`tools/aico.sh doctor --strict` で `ERROR=0 / WARN=0` を最終確認したうえで人間承認を得てコミットする。

```bash
uv run management/scripts/rebuild_indexes.py --json
tools/aico.sh doctor --strict
```

## 完了条件

* 対象 4 ツール（Claude Code・Codex・Antigravity・GitHub Copilot）のモデル・`effort` 仕様の確認結果（確認した実行環境と未確認事項を区別した記録）が実施記録へ記載されていること。
* ガイド更新を行った場合、[docs/04.user-guide/05.worker-models.md](../../../docs/04.user-guide/05.worker-models.md) と [template/management/01.manual/05.worker-models.md](../../../template/management/01.manual/05.worker-models.md) がバイト単位で完全一致し、`最終確認日`・見出し日付・設定表・JSON 記入例が整合していること。
* `uv run -m unittest discover -s tests -v` が全件通過していること。
* AIco 本体 [management/aico-manifest.json](../../aico-manifest.json) への反映要否について人間合意があり、反映した場合は `tools/aico.sh sync_agents` まで完了していること。
* 変更差分および実施記録（添付物を含む）に、非公開リポジトリ URL および再配布不可のベンチマーク生数値が含まれていないこと。
* 実施記録の `status` が更新され、`rebuild_indexes.py` による一覧再生成後の `tools/aico.sh doctor --strict` がエラー・警告 0 件であること。

## 異常時の対応

* **ツール仕様変更によりアダプタコード改修が必要な場合**：
  * 新規ツール追加、フロントマターキー名の変更、Antigravity での `effort` 対応開始など、`template/management/scripts/_lib/agents_sync.py`・テスト・システム設計書（`docs/03.spec/`）の改修を要する事象を検知した場合は、本 Runbook 内でコードを直接改造しない。
  * 現行仕様で安全に扱える範囲のみ整理したうえで、`aico-create-ticket`（`--followup-from <実施記録ID>` 指定）により改修チケットを起票し、実施記録の `followups` へ記録して引き継ぐ。
* **一部ツールの実機確認ができない場合**：
  * 実機確認できたツールと未確認ツールを明確に分離し、未確認ツールは「公式ドキュメント確認のみ」または「現行設定維持（要実機確認）」として人間へ判断を仰ぐ。未確認のモデル ID を動作確認済みとして記載しない。
* **自動テストまたは `doctor` / `doctor --strict` が失敗した場合**：
  * `docs/04.user-guide/05.worker-models.md` と `template/management/01.manual/05.worker-models.md` の差分、改行コード（CRLF 混入）、強制改行の行末半角スペース 2 個漏れ、禁止語、相対リンク切れ、`sync_agents` 未実行、一覧鮮度ドリフト（`rebuild_indexes.py` 未実行）を確認し、すべて解消してから完了とする。
* **公開境界違反（非公開 URL・再配布不可ベンチマーク生数値の混入）を検知した場合**：
  * コミット前であれば直ちに該当箇所・添付物を削除して再確認する。
  * コミット済みかつ未 push の場合は履歴から除去する。すでにリモートへ push 済みの場合はメンテナへ即座に報告し、履歴削除および GitHub ミラー側の対処を協議する。

## 改訂履歴

| 日付 | 内容 |
| :--- | :--- |
| 2026-11-28 | 初版作成（チケット `20261124-155511-ticket-worker-models-review-runbook`） |
