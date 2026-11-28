---
id: 20261128-165205-review-2026-11-28
title: 2026-11-28 worker_models おすすめ設定見直し
status: done
created: 2026-11-28 16:52:05
updated: 2026-11-28 22:01:29
runbook: review-worker-models
followups: []
---

# 2026-11-28 worker_models おすすめ設定見直し

## 概要

[review-worker-models Runbook](../../runbook.md) に従い、2026-11-28 時点における対象 4 ツール（Claude Code・Codex・Antigravity・GitHub Copilot）の最新モデル・`effort` 仕様を確認し、[docs/04.user-guide/05.worker-models.md](../../../../../docs/04.user-guide/05.worker-models.md)・[template/management/01.manual/05.worker-models.md](../../../../../template/management/01.manual/05.worker-models.md) の最終確認日更新および AIco 本体 [management/aico-manifest.json](../../../../aico-manifest.json) への最新おすすめ設定反映を実施した。

## ステップ実施状況

* **完了済み**：手順 1（実施記録作成・現行仕様確認）、手順 2（対象 4 ツール仕様確認）、手順 3（更新方針の人間承認）、手順 4（ガイド 2 ファイルの日付同期更新）、手順 5（自動テスト・`doctor` 検証）、手順 6（`management/aico-manifest.json` 更新・`sync_agents`・`doctor` 検証）、手順 7（公開境界チェック・人間承認・`status: done` 確定・`rebuild_indexes.py`・`doctor --strict` 最終検証）
* **未完了**：なし
* **次に行うこと**：なし（本定期見直しは完了）
* **判断理由**：4 ツールとも現行ガイド（2026-11-24 時点）の推奨設定に廃止予定や仕様変更はなく現行設定維持で妥当であるため、ガイド 2 ファイルは `最終確認日`・見出し日付を `2026-11-28` へ同期更新した。あわせて旧版設定が残存していた AIco 本体 `management/aico-manifest.json` を最新おすすめ設定へ更新し、`sync_agents` で 8 件のワーカー定義を同期した。

## 実行結果と添付

### 対象 4 ツールの仕様確認結果（2026-11-28 時点）

| ツール | 確認手法・実行環境 | 確認結果（モデル・`effort` 仕様） | 判断・反映内容 |
| :--- | :--- | :--- | :--- |
| **Claude Code** | ローカル CLI バージョン確認（`2.1.332`）＋公式ドキュメント照合（セッション内 `/model` は未実施） | 公式エイリアス `opus`（Opus 5.5）・`sonnet`（Sonnet 5.5）・`haiku`（Haiku 5.5）有効。`effort`（`low`・`medium`・`high`・`xhigh`・`max`）は 5.5 系すべて対応。出力キー（`model` / `effort`）変更なし | ガイド現行維持（`opus/high`・`sonnet/high`・`haiku/high`）。`aico-manifest.json` へ反映し `.claude/agents/worker-{high,middle,low}.md` を更新 |
| **Codex** | ローカル実機 `codex debug models` 実行確認 | `vis=list` の最新世代は `gpt-6.2-astra`・`gpt-6.2-sol`、`model_reasoning_effort` は `low`〜`ultra` をサポート。出力キー（`model` / `model_reasoning_effort`）変更なし | ガイド現行維持（`gpt-6.2-astra/high`・`gpt-6.2-sol/medium`・`gpt-6.2-sol/low`）。`aico-manifest.json` へ反映し `.codex/agents/worker-low.toml` を更新 |
| **Antigravity** | 現行 Antigravity サブエージェント仕様確認（`invoke_subagent` `Model` enum）＋公式ドキュメント照合 | 抽象ティア（`pro`・`flash`・`flash_lite`・`inherit`）のみ受理、`effort` 未使用。具体モデル ID 指定不可の仕様に変更なし | ガイド現行維持（`pro/""`・`flash/""`・`flash_lite/""`）。`aico-manifest.json` の旧具体 ID 指定を是正し `.agents/agents/worker-{high,middle}.md` を更新 |
| **GitHub Copilot（VS Code）** | 公式ドキュメント照合（VS Code 上の Ctrl+Space 補完は未実施） | `gemini-4-neon`・`claude-opus-5.5`・`gpt-6.2-sol` いずれも GA 提供中・直近廃止予定なし。`.agent.md` の `model`・`reasoning-effort` 仕様に変更なし | ガイド現行維持（`gemini-4-neon/high`・`claude-opus-5.5/medium`・`gpt-6.2-sol/low`）。`aico-manifest.json` へ反映し `.github/agents/worker-{middle,low}.agent.md` を更新 |

### 変更・検証結果（実行環境：Linux / Python 3.14.4 / `uv` / `main` ブランチ）

* **ガイド更新（バイト単位完全一致）**：[docs/04.user-guide/05.worker-models.md](../../../../../docs/04.user-guide/05.worker-models.md) および [template/management/01.manual/05.worker-models.md](../../../../../template/management/01.manual/05.worker-models.md) の `最終確認日`・見出し日付を `2026-11-28` へ更新（ルート `management/01.manual/05.worker-models.md` は未編集）。
* **AIco 本体同期**：`tools/aico.sh sync_agents` → 作成／更新 8 件、削除 0 件。
* **自動テスト**：`uv run -m unittest discover -s tests -v` → **38/38 OK**（`tests/test_user_guide.py` を含む全件通過）。
* **公開境界チェック**：`git diff` および本実施記録ファイルを目視確認し、非公開リポジトリ URL および再配布不可のベンチマーク生数値が含まれていないことを確認済み。
* **一覧再生成・最終診断**：`uv run management/scripts/rebuild_indexes.py --json`（[management/05.runbooks/index.md](../../../index.md) 更新）→ `tools/aico.sh doctor --strict` → **OK=9 / WARN=0 / ERROR=0**。

### 未確認事項

* Claude Code セッション内 `/model` による対話確認（ローカル CLI `2.1.332` の存在および公式ドキュメント照合のみ実施）。
* GitHub Copilot（VS Code）での `.github/agents/worker-high.agent.md` `model:` 行 Ctrl+Space 補完による実機確認（公式ドキュメント照合のみ実施）。

## 異常と引き継ぎ先

* アダプタコード（`template/management/scripts/_lib/agents_sync.py`・`manifest.py`）の改修を要するツール仕様変更は検知されなかったため、引き継ぎチケット起票は不要。
