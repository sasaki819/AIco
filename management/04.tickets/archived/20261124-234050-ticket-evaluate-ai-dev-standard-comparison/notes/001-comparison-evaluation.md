---
id: 001-comparison-evaluation
title: ai-dev-standard・jotline と AIco の比較評価レポート
created: 2026-11-24 23:47:00
updated: 2026-11-24 23:47:00
---

# ai-dev-standard・jotline と AIco の比較評価レポート

## 概要

`ai-dev-standard`（`main` コミット `2d2c6eb`）および同フレームワーク導入済みプロジェクト `jotline`（`main` コミット `81c7e0b`）の実ファイルを読み取り専用で調査し、現行 AIco（`main` コミット `d0165a0`）と比較評価した。  
結論として、**`ai-dev-standard` は構造・拡張性・並列運用耐性の全面で AIco に包含・凌駕されており安全に廃止可能**である。一方で、実運用で培われた **8 件の有効な実践知（うち高優先 4 件・中優先 4 件）** が確認できたため、AIco の設計思想と整合する形で選別取り込みすることを推奨する。

## 内容

### 1. 全体構造の比較（AIco が明確に優れている領域）

| 観点 | `ai-dev-standard` | AIco | 評価 |
| :--- | :--- | :--- | :--- |
| **管理領域の分離** | `BACKLOG.md`・`backlog/`・`specs/`・`discussions/`・`templates/`・`docs/adr/`・`ci/`・`tools/ai-standard/`・`.ai-standard-version` がルート直下に分散 | 単一の `<management_root>/`（既定 `management/`）へ完全集約し、プロジェクト固有資産と明確に分離 | **AIco が圧勝** |
| **ID 採番と並列衝突耐性** | 4 桁連番（`0001`）のため並列起票で衝突リスクあり。作業ブランチで `BACKLOG.md` を都度再生成するためマージ競合が頻発（ガイド §13 ルール 1・2） | タイムスタンプ ID（`YYYYMMDD-HHMMSS-...`）＋全体一覧は統合ブランチ限定再生成で構造的に衝突回避 | **AIco が圧勝** |
| **チケット文書構造** | `backlog/items/`（Item）と `specs/<ID>/`（`requirements`/`design`/`tasks`/`progress` 4 ファイル）に 2 層分散 | チケットフォルダ単一集約（`index.md`・`plan.md`・必要時 `notes/`・`review/`） | **AIco が優位** |
| **対応 AI ツールとワーカー** | Claude Code / Copilot / Antigravity（`.claude/skills` と `.agents/skills` の二重コピー、Codex 非対応、ワーカー階層なし） | 4 ツール対応（Claude Code / Codex / Copilot / Antigravity）、`.agents/skills/` 単一原本、3 段階ワーカー（`high`/`middle`/`low`）同期 | **AIco が圧勝** |
| **スクリプト・ライフサイクル** | `.sh` と `.ps1` の二重実装（`backlog-index` と `check-docs` のみ）。導入はローカル clone 後の `init.sh`/`sync.sh` | Python (`uv run`) 単一実装で 15 スクリプト＋統一 JSON スキーマ＋URL ワンライナー `install.py`・`init.py`・`update.py`・`upgrade.py` | **AIco が圧勝** |
| **レビュー記録・再確認** | 1 レビュー 1 Markdown 表（`jotline` 実例では表セルが長文化し、`by: ""`・`重大度: 確認待ち` が残存）。独立再確認工程なし | 1 指摘 1 ファイル＋独立コンテキストでのレビューおよび再確認（`aico-review-recheck`） | **AIco が優位** |
| **定常作業（Runbook）** | 未対応 | Runbook 手順書・実施記録・異常引き継ぎ・レビューに対応 | **AIco が優位** |
| **既存プロジェクト共存** | `AGENTS.md` の `{{PROJECT_NAME}}` プレースホルダ置換方式＋`--host` による CI/PR テンプレート強制配置 | `AICO:BEGIN`〜`END` マーカー保護方式で既存 `AGENTS.md` と自然共存、ホスト非依存 | **AIco が優位** |

### 2. `ai-dev-standard`・`jotline` に見られた優位要素・実践知（取り込み候補）

#### 優先度高（AIco の思想と美しく調和し、実務効果が高い 4 件）

| 候補 ID | 要素 | `ai-dev-standard` / `jotline` 側の実物根拠 | AIco の現状ギャップ | AIco への推奨取り込み形と反映先 |
| :--- | :--- | :--- | :--- | :--- |
| **A-1** | **人間レビュー指摘の記録＆即採用フロー** | `payload/skills/apply-review/SKILL.md` `(b)` で、人間指摘を AI が記録する際は最初から `accepted` で起票して即対応する規定あり。`jotline/specs/0010-.../reviews/2026-11-04-impl-human.md` で実運用実績あり | AIco の `aico-review` は AI 独立ワーカー専用想定で、人間指摘の途中差し込み時に冗長な `open` → `triaging` → `in-progress` 往復が発生 | 既存チケット [20261124-231830-ticket-workflow-review-and-ux-improvements](../../20261124-231830-ticket-workflow-review-and-ux-improvements/index.md) のレビューフロー整備へそのまま取り込む |
| **A-2** | **CI 連携スニペット案内と `aico-ticket-pr` の既存テンプレート尊重** | `payload/ci/ai-standard.gitlab-ci.yml`・`.github/workflows/ai-standard.yml` で `check-docs` を CI 化（`jotline/.gitlab-ci.yml` で稼働実績あり）。`pr-draft/SKILL.md` が導入先の既存 PR/MR テンプレートを優先読込 | AIco は `doctor.py` の CI 組込ガイド・スニペットがなく、`aico-ticket-pr` も導入先リポジトリの既存 PR/MR テンプレートを参照しない | **強制ファイル配置はせず**、①ユーザーガイドへ GitHub Actions / GitLab CI のコピペ用 `doctor.py` スニペットを掲載、②`aico-ticket-pr` に「既存 PR/MR テンプレートがあれば準拠して出力する」指針を追加 |
| **A-3** | **AI 行動ガードレール（禁止事項）の明文化** | `payload/AGENTS.md`「AIへの行動規則」・`implement-task/SKILL.md`「禁止事項」に、①スコープ外課題はその場で直さず起票提案、②検証コマンド成功前の完了扱い・テスト無効化禁止、③作業開始時は必要最小限の記録だけ読む（コンテキスト汚染防止）を明記 | 理念としては共有されているが、`template/AGENTS.md`・`aico-ticket-implement/SKILL.md` に具体的禁止事項として明文化されていない項目がある | [20261124-231830-ticket-workflow-review-and-ux-improvements](../../20261124-231830-ticket-workflow-review-and-ux-improvements/index.md) の `template/AGENTS.md`・スキル改訂と合わせて組み込む |
| **A-4** | **`doctor.py` による `done` チケット・見送り指摘の機械検査強化** | `payload/tools/ai-standard/check-docs.sh` #4・#6 で、①`status: done` なのに未チェックタスク（`- [ ]`）が残っていれば ERROR、②見送り（`wontfix`）指摘の理由欄が空なら ERROR を機械検知 | AIco の `doctor.py` は未解決指摘（`open`/`in-progress`）残存は検査するが、`status: done` 時の未チェック AC（`- [ ]`）および見送り指摘（`status: cancelled`）の理由空欄は機械検査していない | `doctor.py` へ「`done` チケットの未チェック AC 検査（または未検証理由との整合）」と「`cancelled` 指摘の採否判断欄空チェック」を追加 |

#### 優先度中（ガイド・テンプレート・開発運用をさらに盤石にする 4 件）

| 候補 ID | 要素 | `ai-dev-standard` / `jotline` 側の実物根拠 | AIco の現状ギャップ | AIco への推奨取り込み形と反映先 |
| :--- | :--- | :--- | :--- | :--- |
| **B-1** | **Windows 混在環境向け `.gitattributes`（LF 固定）推奨案内** | `payload/.gitattributes` で `*.md` 等を `text eol=lf` 固定し、CRLF 混入による機械検査失敗を防止 | AIco の `doctor.py` も LF 改行を厳格検査するが、ユーザーガイドに Windows チーム向けの `.gitattributes` 任意推奨案内がない | `docs/04.user-guide/01.getting-started.md` または `04.user-guide.md` に任意の推奨設定例として数行追記（強制配置はしない） |
| **B-2** | **並列運用ルールと `git worktree` 実践ノウハウ** | `ai-dev-standard-guide.md` §7・§13 に「1 チケット = 1 worktree」「並列数は人間のレビュー能力に合わせる」「設計書同時更新時のマージ統合」など実践的な注意点が整理されている | AIco は `worktree` 対応のフックはあるが、ユーザーガイドに並列運用・レビューボトルネック対策の実践ガイドが薄い | `docs/04.user-guide/04.user-guide.md` に「複数チケットを並行で進めるコツ」節として簡潔に追記 |
| **B-3** | **DoD における「システム設計書反映・ADR 要否判断」の明示化** | `payload/templates/spec/tasks.md` 末尾に 2 つの固定タスクを置くことで、`jotline` では `docs/architecture/` 6 ファイル・`docs/adr/` 3 本が漏れなく維持された | AIco の `ticket-index.md` DoD 欄は「関連記録・ADR への導線確認」のみで、プロジェクト側システム設計書の更新要否判断（不要なら理由明記）がやや目立ちにくい | `template/management/templates/ticket-index.md`・`aico-ticket-close` の DoD 確認観点を「設計書更新・ADR 要否判断（不要理由含む）」へ明確化 |
| **B-4** | **リリース前 4 ツール実機スモーク確認チェックリスト** | `ai-dev-standard/README.md` に Claude Code / Copilot（`chat.useAgentsMdFile` 注意点含む）/ Antigravity ごとの手動実機確認手順を記載 | AIco は自動テストは充実しているが、リリース前の 4 ツール実機確認手順（Runbook）がない | AIco 本体開発用の Runbook 候補として将来整備（急ぎではない） |

#### 取り込み見送り（AIco の設計の方が明確に優れているため採用しない項目）

* **4 桁連番 ID と作業ブランチでの `BACKLOG.md` 再生成**：AIco のタイムスタンプ ID＋統合ブランチ限定再生成の方が並列衝突がなく優秀。
* **Item と Spec（4 ファイル）の 2 層分割**：AIco のチケットフォルダ単一集約の方が簡潔で迷わない。
* **`.sh` / `.ps1` 二重実装**：AIco の Python (`uv run`) 単一実装の方が保守性・表現力ともに圧倒的に優秀。
* **`--host gitlab|github` による CI・PR テンプレートファイルの強制配置**：導入先ルート直下の汚染を避けるため、AIco ではガイド上の任意スニペット提供にとどめる。
* **1 ファイル表形式の Review 記録**：AIco の 1 指摘 1 ファイル＋独立再確認の方が大規模・長文指摘に強い。
* **`AGENTS.md` の `{{...}}` プレースホルダ方式**：AIco のマーカー外自由記述方式の方が既存プロジェクトとの共存性が高い。
* **1 タスクごとの自動コミット**：AIco の「人間の明示指示でコミット・push する」方針の方が安全。

### 3. `jotline` の AIco 移行に向けた実務観点（確認結果）

`jotline`（`81c7e0b`）の実構成を確認した結果、AIco への切り替えは非常にスムーズに行える見通しである。

1. **そのまま維持・活用できる資産**：
   * `docs/architecture/`（6 ファイル）：プロジェクト固有のシステム設計書としてそのまま維持し、AIco の `AGENTS.md` マーカー外に「システム設計書は `docs/architecture/` を更新対象とする」と明記する。
   * `AGENTS.md` のマーカー外（プロジェクト概要・技術スタック・コマンド・ブランチ運用ルール）：そのまま AIco の `AGENTS.md` マーカー外へ引き継ぐ。
2. **既存記録の移行コストが極めて小さい**：
   * 未完了 Item は `0007`・`0009`・`0011` の 3 件のみ（すべて `status: backlog`、Spec 未着手）のため、AIco 導入後に `aico-create-ticket` で 3 件再起票するだけでクリーンに移行できる。
   * `docs/adr/0001`〜`0003` は重要な設計判断のため、AIco 導入時に `management/03.adr/` へ引き継ぐ（または `docs/adr/` を歴史資料として参照リンクを残す）。
   * 完了済みの `backlog/archive/`（8 件）・`specs/`（6 件）は履歴として Git に残るため、AIco 形式への変換は不要で撤去または歴史アーカイブ扱いとすればよい。
3. **移行時の注意点（重要）**：
   * **旧スキルの事前削除**：`jotline` には `.agents/skills/` と `.claude/skills/` に旧 7 スキル（`new-item` 等）が存在する。AIco の `install.py` 実行前にこれら旧スキルと `tools/ai-standard/manifest.txt` 記載の `ai-dev-standard` 由来ファイル一式を撤去しないと、旧スキルが混在して AI が誤動作する恐れがある。
   * **`.gitlab-ci.yml` の差し替え**：`jotline/.gitlab-ci.yml` の `include: - local: ci/ai-standard.gitlab-ci.yml` を外し、代わりに AIco の `uv run management/scripts/doctor.py` を実行するジョブへ差し替える必要がある（`A-2` の CI スニペットを整備しておくとそのまま転用できる）。

## 結論・残件

* **`ai-dev-standard` の廃止判断（人間合意済み：2026-11-25）**：AIco へ移行し、`ai-dev-standard` は廃止して問題ない（アーキテクチャ上の優位性はすべて AIco 側にある）。
* **取り込み候補の最終採否と引き継ぎ先（人間合意済み：2026-11-25）**：
  * **採用（既存 UX 改善チケット [20261124-231830-ticket-workflow-review-and-ux-improvements](../../20261124-231830-ticket-workflow-review-and-ux-improvements/index.md) へ統合）**：
    * **A-1**：人間レビュー指摘の記録＆即採用（`in-progress`）フローおよび同一フェーズ内複数ラウンド遷移の正規化
    * **A-2**：`aico-manifest.json` への任意キー `pr_template`（相対パス文字列・既定 `""`、後方互換維持）追加、`init.py` による未存在時のみ推奨雛形配置（既存時は上書き禁止・配置後は導入先所有）、`aico-ticket-pr` の既存テンプレート尊重および非利用プロジェクトでも完全運用可能なオプショナル位置づけ、ならびにユーザーガイドへの任意 CI スニペット（GitHub Actions / GitLab CI 向け `doctor.py` 実行例と導入判断基準）掲載
    * **A-3**：`template/AGENTS.md`・主要スキルへの具体的 AI 行動ガードレール明文化
    * **A-4**：`doctor.py` の品質ゲート強化（`status: done` チケットの未チェック AC 検知・`cancelled` 指摘の理由空欄検知）
    * **B-1**：Windows 混在環境向け `.gitattributes`（`eol=lf` 固定）の任意推奨設定をユーザーガイドへ追記
    * **B-2**：並列運用・`git worktree` 実践ノウハウをユーザーガイドへ追記
    * **B-3**：DoD チェック項目におけるプロジェクト側システム設計書更新確認・ADR 要否判断（不要理由含む）の明示化
  * **将来検討（別 Runbook 候補として記録）**：
    * **B-4**：リリース前 4 ツール実機スモーク確認チェックリスト（AIco 本体開発用 Runbook 候補）
  * **見送り**：4 桁連番 ID、Item/Spec 2 層分割、`.sh/.ps1` 二重実装、ホスティング区分による CI・PR ファイル強制配置、1 ファイル表形式レビュー、`{{...}}` プレースホルダ、1 タスクごとの自動コミット。
