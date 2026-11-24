---
id: implementation-round1-002-install-use-latest-branch
title: 初回導入コマンドを latest ブランチ基本へ改める
status: done
created: 2026-11-24 21:38:54
updated: 2026-11-24 22:22:37
severity: minor
reviewer: human
---

# 初回導入コマンドを latest ブランチ基本へ改める

## 対象

* `docs/04.user-guide/01.getting-started.md`（Step 1）および同期先 `template/management/01.manual/01.getting-started.md`
* `README.md`（クイックスタート）
* `docs/03.spec/08.adoption-and-migration.md`（2.1 節・4.2 節）
* 比較基点：`c4c20d2`（作業ツリー未コミット差分）

## 指摘内容と根拠

新規導入時に古いバージョンを指定する場面は少なく、`v0.1.0` のような固定タグ例示に対して毎回「最新タグへ読み替えて」と求めるのは初見ユーザーのハードルおよびドキュメント陳腐化の要因となる。  
初回導入は `latest` を基本コマンドとし、特定バージョンを固定したい場合のみバージョンタグ（`vX.Y.Z`）を指定できる案内へ改めたい。

## 採否判断（人間選別）

* **判断**：採用（`in-progress`）
* **理由**：人間レビュー指摘および運用方式の検討結果として、移動タグ（force-update）による `git fetch` 衝突やミラー強制更新制限を避けるため、**案 A：`latest` を最新安定版リリースタグへ fast-forward のみで進める専用ブランチとして運用し、導入コマンドには `uv run --refresh` を付与する方式** を採用する。

## 修正内容

* `docs/04.user-guide/01.getting-started.md`（Step 1）および `template/management/01.manual/01.getting-started.md` の導入コマンドを `uv run --refresh https://raw.githubusercontent.com/sasaki819/AIco/latest/installer/install.py` へ更新し、特定バージョン固定時は `latest` を `v0.1.0` 等のリリースタグへ置換する注記へ改めた。
* `README.md` のクイックスタートも同様に `uv run --refresh .../latest/installer/install.py` へ更新した。
* `docs/03.spec/08.adoption-and-migration.md` の 2.1 節（実行方法・キャッシュ注記）および 4.2 節（段階 4 のリリース時系列と `latest` ブランチ運用規約：fast-forward 専用ブランチとし同名の `latest` タグは作成しない旨）を整合更新した。
* 関連コミット：未コミット（作業ツリー上で検証済み）

## 独立再確認結果

* **結果**：解消確認（`done`）
* **確認者**：human（指摘者本人による確認完了。`docs/04.user-guide/01.getting-started.md` の注記表現を人間側で微調整し、`template/management/01.manual/01.getting-started.md` へ同期済み）
* **実行環境**：作業ツリー上の実物確認および自動テスト 30/30 OK
* **未確認事項**：なし（独立 AI ワーカーによるチケット全体レビューは round2 で別途実施）
