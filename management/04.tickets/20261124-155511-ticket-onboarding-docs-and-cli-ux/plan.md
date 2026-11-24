# 作業計画

## 合意した仕様

### 1. 想定読者と位置づけ

* **想定読者**：AI エージェントを最近プロジェクトで使い始めた若手エンジニア。
* **役割分担**：`docs/04.user-guide/` は `docs/03.spec/` と二重管理せず、「最初の使いこなしガイド」にとどめる。詳しい仕様は AIco リポジトリの `docs/03.spec/` へ委ねる。

### 2. `docs/04.user-guide/`（原本）と `template/management/01.manual/`（配布コピー）

* 既存の `template/management/01.manual/workflow-reference.md` は廃止し、以下 6 ファイルを `docs/04.user-guide/` に整備して `template/management/01.manual/` へ完全同一コピーを配置する。
  1. `index.md`：目次と「まずここから」3 ステップの読み順案内
  2. `01.getting-started.md`：前提環境 → Step 0 導入（`install.py`）→ Step 1 初期設定（`tools/aico.sh init`）→ Step 2 `AGENTS.md` 記入例と `worker_models`（`05.worker-models.md` へのリンク）→ Step 3 動作確認（`doctor`）→ アップデート。`install.py --init` は 1 文の補足にとどめる
  3. `02.tutorial.md`：小さな変更を題材にした最初の 1 チケット完走ハンズオン（相談 → 起票 → 開始 → 計画 → 実装 → レビュー → クローズ）と具体的な AI への声かけ例
  4. `03.cheatsheet.md`：「こんな時はこれ！」逆引き表、まず覚える基本 6 スキルとその他スキルのひとこと一覧、よく使う `tools/aico.sh` コマンド
  5. `04.user-guide.md`：4 種の管理情報の使い分け、ブランチとレビューの基本感覚、よくある疑問・トラブルシュート（FAQ）
  6. `05.worker-models.md`：最終確認日、空欄のまま既定モデルで開始できる旨、4 ツール別おすすめ `worker_models` JSON 例、反映手順（`tools/aico.sh sync_agents`）
* **リンク自己完結ルール**：`docs/04.user-guide/` 内の相対リンクは同ディレクトリ内の 6 ファイル間のみに閉じる（`docs/02.policy/` 等への相対リンクは張らない）。
* **同期保証**：`tests/` に `docs/04.user-guide/` と `template/management/01.manual/` のファイル一覧および内容の完全一致を検証する自動テストを追加する。

### 3. `README.md`・`docs/03.spec/08`・`template/AGENTS.md` の更新

* **`README.md`**：初見ユーザー向けに「AIco で何が変わるか」「対応ツール・前提」「3 ステップ クイックスタート（コピペ可）」「導入後にまずやること（`docs/04.user-guide/` への導線）」「目的別ドキュメント案内（利用者向け／思想・仕様向け）」を整備し、リポジトリ構成の説明へ `docs/04.user-guide/` を反映する。
* **`docs/03.spec/08.adoption-and-migration.md`**：
  * 1.1 節のリポジトリ構成図へ `docs/04.user-guide/` を追記し、`template/management/01.manual/` がその同期コピーである旨を明記する。
  * 2.1 節の `install.py` オプション表へ `--init` を追加し、「既定の 2 段階導入（配置→`init`）を置換するものではなく、慣れた利用者向けの非必須ショートカット（配置済み `init.py` を呼ぶ薄いラッパー）であり、保守上の不都合が生じた際は廃止可能」という設計意図を明記する。
* **`template/AGENTS.md`**：`## 4. 詳細マニュアルへの参照` を新しい 6 ファイル構成（`index.md`・`01.getting-started.md`・`02.tutorial.md`・`03.cheatsheet.md`・`04.user-guide.md`・`05.worker-models.md`）へ更新し、初見ユーザーが AI に使い方を尋ねた際にも適切なガイドを案内できるようにする。

### 4. 導入・初期設定ツール UX 改善（`installer/install.py`・`init.py`・`upgrade.py`）

* **`installer/install.py`**：
  * 完了メッセージに次ステップ（`tools/aico.sh init`）と `management/01.manual/01.getting-started.md` への導線を追加する。
  * 未コミット変更・既存 `CLAUDE.md` 衝突等のエラーメッセージに対処の具体例を添える。
  * 任意オプション `--init` を追加する（配置完了後に配置済み `<management_root>/scripts/init.py --root <management_root>` を `subprocess` で呼び出すだけの薄いラッパー。`--dry-run` 併用時は実行せず予定のみ表示、`--json` 併用時は `init.py --json` の結果を統合して単一 JSON で出力する）。
* **`template/management/scripts/init.py`**：
  * 対話ウィザードの各ステップに簡潔な補足を加え、`worker_models` 質問前に「空欄のままでも各ツールの既定モデルで動作する」「おすすめ設定例は `management/01.manual/05.worker-models.md` を参照」の案内を表示する。
  * 完了メッセージに次の 3 ステップ（① 必要に応じ `AGENTS.md` マーカー外を追記 ② 初回コミット ③ `management/01.manual/02.tutorial.md` を見て最初の 1 チケットを試す）を表示し、`worker_models` 未設定の `WARN` に対して「エラーではなくそのまま利用開始できる」旨を補足する。
* **`installer/upgrade.py`**：
  * 既存の `_mirror_tree` により `management/01.manual/` の廃止ファイル（旧 `workflow-reference.md`）が自動削除されることを確認済み。アップグレード時に旧 `workflow-reference.md` がクリーンに削除され新 6 ファイルへ置換されることを自動テストで保証する。

### 4.2. `05.worker-models.md` 初版おすすめ設定とアダプター整合修正

* **初版おすすめ設定（2026-11-24 時点・合意済み）**：
  * **Claude Code**：`opus` / `high`、`sonnet` / `high`、`haiku` / `high`
  * **Codex**：`gpt-6.2-astra` / `high`、`gpt-6.2-sol` / `medium`、`gpt-6.2-sol` / `low`
  * **Antigravity**：`pro` / `""`、`flash` / `""`、`flash_lite` / `""`
  * **GitHub Copilot（VS Code）**：`gemini-4-neon` / `high`、`claude-opus-5.5` / `medium`、`gpt-6.2-sol` / `low`
* **アダプター整合修正**：
  * `template/management/scripts/_lib/manifest.py`：`EFFORT_SUPPORTED_TOOLS` を `("claude", "codex", "copilot")` とし、Antigravity を `effort` 未設定警告対象外とする。
  * `template/management/scripts/_lib/agents_sync.py`：Antigravity は `effort` キーを出力しない（`effort` 省略）、GitHub Copilot は `reasoning-effort` キーで出力する（`key_order=["name", "description", "model", "reasoning-effort"]`）。
  * `docs/03.spec/05.agent-config.md`：4.3 節のツール別マッピング表を上記公式仕様へ整合更新する。

### 5. 対象外（本チケットでは行わないこと）

* `worker_models` 定期見直し用 Runbook の作成（別チケット `20261124-155511-ticket-worker-models-review-runbook` で対応）。
* AIco 本体運営領域（ルート直下の `AGENTS.md`・`management/01.manual/` 等）への直接改造（リリース前手順の `tools/aico.sh update --source .` で自己適用する）。
* `AICO_VERSION` の版上げ・`CHANGELOG.md` リリース確定・Git タグ発行（リリース作業時に実施）。

## ステップ一覧

* [x] Step 1：`docs/04.user-guide/` 配下の 6 ファイル（`index.md`・`01.getting-started.md`・`02.tutorial.md`・`03.cheatsheet.md`・`04.user-guide.md`・`05.worker-models.md`）を `aico-markdown-write` 規約に沿って執筆する
* [x] Step 2：`template/management/01.manual/` から旧 `workflow-reference.md` を削除し、`docs/04.user-guide/` の 6 ファイルを完全同一コピーとして配置する
* [x] Step 3：`README.md` を初見ユーザー向けに刷新し、`docs/03.spec/08.adoption-and-migration.md` に `docs/04.user-guide/` 構成と `install.py --init` 仕様・設計意図を追記する
* [x] Step 4：`template/AGENTS.md` のマニュアル参照節を新しい 6 ファイル構成へ更新する
* [x] Step 5：`installer/install.py`（完了・エラー案内強化および `--init` 薄いラッパー実装）と `template/management/scripts/init.py`（対話案内・完了後ステップ案内・`WARN` 補足）を実装する
* [x] Step 5b：ワーカー同期アダプター（`template/management/scripts/_lib/manifest.py`・`agents_sync.py`）および `docs/03.spec/05.agent-config.md` を公式仕様（Antigravity `effort` 省略・Copilot `reasoning-effort` 出力）へ整合修正する
* [x] Step 6：`tests/` にテストを追加する（`docs/04.user-guide/` と `template/management/01.manual/` の完全一致・自己完結相対リンク検証、`install.py --init` の正常・dry-run・json 動作、`init.py` 案内表示、`upgrade.py` による旧 `workflow-reference.md` 削除検証）
* [x] Step 7：全自動テスト（`python3 -m unittest discover -s tests -v`）、Markdown 品質・ソフト改行チェック、および `doctor.py` を実行して全件通過を確認する
* [x] Step 8：独立レビュー（`aico-review`）を実施し、採用指摘の修正・再確認を経てクローズ準備を行う

## 検証方針

* **自動テスト**：`python3 -m unittest discover -s tests -v` で既存 25 件＋新規追加テストすべてが通過すること。
* **同期・リンク・Markdown 品質検証**：
  * `docs/04.user-guide/` と `template/management/01.manual/` のバイト単位完全一致。
  * 追加・変更した全 Markdown の UTF-8（BOM なし）・LF・強制改行の行末半角スペース 2 個・見出し飛びなし・禁止語なし・相対リンク切れなしを確認。
* **診断**：`uv run management/scripts/doctor.py --json` で `error: 0` を確認する。
* **独立レビュー**：実装完了後に `aico-review` で独立コンテキストのワーカーへ成果物レビューを委譲する。

## 判断ログ

* **2026-11-24｜`install.py --init` の実装方式**：`init.py` のロジックを複製せず、配置済み `<management_root>/scripts/init.py` を `subprocess` で呼び出す薄いラッパーとする。保守負荷を最小化し、将来不都合が生じた場合に安全に廃止できるようにするため。
* **2026-11-24｜旧 `workflow-reference.md` のアップグレード時整理**：`installer/upgrade.py` の `_mirror_tree` が `management/01.manual/` の未存在ファイルを自動削除する仕様であることを実コードで確認したため、専用マイグレーションは追加せず、自動テストで削除挙動を保証する。
* **2026-11-24｜設計フェーズの扱い**：新規外部アーキテクチャやデータスキーマ変更を伴わず、仕様変更箇所（`docs/03.spec/08`）も本チケット内で整合更新する範囲のため、計画承認後は `design` をスキップして `implementation`（または必要に応じ `planning / reviewing`）へ進める案とする。
* **2026-11-24｜アダプター整合修正の同梱**：公式仕様調査で Antigravity（抽象ティアのみ・`effort` 非対応）および Copilot（`reasoning-effort` キー・`claude-opus-5.5` ドット記法）を確認したため、おすすめ設定例が警告ゼロかつ仕様どおりに機能するよう本チケットへ同梱する。
* **2026-11-24｜人間レビュー（round1）の記録と `latest` ブランチ運用採用**：実装確認時に人間から出た 2 件の指摘（`04.user-guide/` 連番付与、`01.getting-started.md` 等の導入コマンドを `latest` 基本化）を `review/` 配下へ `reviewer: human`（round1）として記録し、導入用 `latest` は移動タグではなく最新安定版へ fast-forward のみで進める専用ブランチ＋`uv run --refresh` で運用する方針（案 A）を採用した。
* **2026-11-24｜自動生成マーカー（`AICO:AUTO`）および管理マーカー（`AICO:BEGIN/END`）の前後空行修正**：`review/index.md` 等で表定義直後に `<!-- AICO:AUTO:END:... -->` が続くと一部 Markdown ビューワーで表の最終行としてレンダリングされる問題を確認したため、`template/management/scripts/_lib/markers.py`（`replace_auto_block` で前後 1 空行を保証）・`template/management/` 配下の全初期テンプレート・`template/AGENTS.md`・`tests/test_lib.py` 回帰テストを本チケットへ同梱修正した（ドッグフーディング中の `management/` 側には次リリース自己適用時に反映）。
* **2026-11-24｜レビューフロー整備の後続チケット起票予定**：人間レビューの試験運用で判明した 3 点のギャップ（人間レビュー登録手順の明文化・同一フェーズ内 `re-reviewing -> reviewing` 遷移の扱い・人間指摘のトリアージ簡略化）は、本チケット統合後に統合ブランチ（`main`）上で新規チケットとして起票する。
