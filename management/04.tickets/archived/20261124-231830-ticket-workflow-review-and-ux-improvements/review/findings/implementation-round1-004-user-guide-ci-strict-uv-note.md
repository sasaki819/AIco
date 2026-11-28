---
id: implementation-round1-004-user-guide-ci-strict-uv-note
title: ユーザーガイド CI 構成例における --strict 併用時の uv 不在 WARN 注意不足
status: done
created: 2026-11-25 10:03:21
updated: 2026-11-25 20:37:04
severity: minor
reviewer: worker-middle
---

# ユーザーガイド CI 構成例における --strict 併用時の uv 不在 WARN 注意不足

## 対象

* `docs/04.user-guide/04.user-guide.md`（L92-L122）
* `template/management/01.manual/04.user-guide.md`（L92-L122）
* 比較基点：`d3a54b4`

## 指摘内容と根拠

第6節「CI への `doctor.py` 組み込み（任意）」では「警告も失敗扱いにしたい場合は `--strict` を追加します」と記載し、GitHub Actions（`setup-python@v5` のみ）および GitLab CI（`python:3.11-slim` + `git` のみ）の最小 YAML 例を提示している。しかし `doctor.py`（L161-L168）は `uv` 不在時に `WARN` を出力するため、`uv` 未導入の記載 YAML へそのまま `--strict` を追加すると正常リポジトリでも常に終了コード `1` で失敗する（`worker_models` 未設定時も同様）。

**推奨修正案**：
* `--strict` を CI で有効化する場合は CI 環境への `uv` 導入および `worker_models` 設定が必要になる旨を 1 文補足し、`docs/04.user-guide/04.user-guide.md` と `template/management/01.manual/04.user-guide.md` の双方を同期更新する。

## 採否判断（人間選別）

採用（in-progress）：2026-11-25 人間トリアージにより全 4 件採用確定。エッジケース防御・仕様とスキルの整合性・CI ガイドの正確性を確保するため修正を実施する。

## 修正内容

* `docs/04.user-guide/04.user-guide.md` 第6節の最小構成例直下へ、`--strict` 併用時は `WARN` も失敗扱いとなるため CI 環境への `uv` 導入と `worker_models`（および利用時は `pr_template` 実ファイル）設定が必要である旨の注記を敬体で追記した。
* `template/management/01.manual/04.user-guide.md` へ完全一致で同期し、`tests/test_user_guide.py` を含む全 33 件のテスト通過を確認した。
* 関連コミット：未コミット（作業ツリー上）

## 独立再確認結果

* **判定**：解消（`done`）
* **確認根拠**：`docs/04.user-guide/04.user-guide.md`（L116）へ敬体で `--strict` 併用時の `uv` 導入・`worker_models` 設定注記が追記され、`doctor.py`（L161-L168, L199-L209, L239-L246）の `WARN` 条件と整合し、`template/management/01.manual/04.user-guide.md` と完全一致していることを確認。
* **実行環境**：Linux / 読み取り専用独立ワーカー
* **未確認事項**：なし
