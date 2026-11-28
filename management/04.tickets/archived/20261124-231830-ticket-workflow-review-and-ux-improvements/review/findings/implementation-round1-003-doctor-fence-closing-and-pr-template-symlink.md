---
id: implementation-round1-003-doctor-fence-closing-and-pr-template-symlink
title: doctor.py のコードフェンス終端判定および pr_template シンボリックリンク境界検査の抜け
status: done
created: 2026-11-25 10:03:21
updated: 2026-11-25 20:37:04
severity: minor
reviewer: worker-middle
---

# doctor.py のコードフェンス終端判定および pr_template シンボリックリンク境界検査の抜け

## 対象

* `template/management/scripts/doctor.py`（L52-L61, L90-L99, L225-L236）
* 比較基点：`d3a54b4`

## 指摘内容と根拠

1. **コードフェンス終端の誤判定**：`_extract_h2_section`（L58-L59）および `_find_unchecked_acs`（L96-L97）の閉じフェンス判定が `elif marker[0] == fence_char and len(marker) >= fence_len:` のみとなっており、CommonMark で閉じフェンスとならない末尾テキスト付き行（例：ネストしたフェンス内の ```` ```bash ````）を閉じフェンスと誤認する。
2. **`pr_template` シンボリックリンク境界検査の欠落**：L225-L236 は `(ctx.repo_root / pr_tpl_norm).is_file()` のみを確認しており、`init.py` と同様に `.resolve().relative_to(ctx.repo_root.resolve())` でシンボリックリンク経由のリポジトリ外参照を検査していない（`07.scripts.md` 第5章の検査要件「相対パス・リポジトリ外参照禁止・設定時ファイル実在」と不整合）。

**推奨修正案**：
* フェンス終端判定に `and not line[fm.end():].strip()` を追加する。
* `doctor.py` の `pr_template` 検査で `.resolve().relative_to(ctx.repo_root.resolve())` による境界検証を行い、リポジトリ外を指す場合は `ERROR` を報告する。

## 採否判断（人間選別）

採用（in-progress）：2026-11-25 人間トリアージにより全 4 件採用確定。エッジケース防御・仕様とスキルの整合性・CI ガイドの正確性を確保するため修正を実施する。

## 修正内容

* `template/management/scripts/doctor.py` の `_extract_h2_section` および `_find_unchecked_acs` の閉じフェンス判定に `and not line[fm.end():].strip()` を追加し、ネストしたフェンス内の末尾情報文字列付き行を閉じフェンスと誤認しないよう修正した。
* `template/management/scripts/doctor.py` Category 2 の `pr_template` 検査へ `.resolve().relative_to(ctx.repo_root.resolve())` による境界検証を追加し、シンボリックリンク経由でリポジトリ外を指す場合に `ERROR` を報告するよう修正した。
* `tests/test_daily_scripts.py`（`test_human_review_status_and_doctor_quality_gates`）へネストフェンス内の未チェック風テキスト無視テストおよび外部シンボリックリンク `ERROR` 検知テストを追加し、`python3 -m unittest discover -s tests -v`（33/33 OK）を確認した。
* 関連コミット：未コミット（作業ツリー上）

## 独立再確認結果

* **判定**：解消（`done`）（※関連する回帰テストの条件網羅について `implementation-round1-005` を新規登録）
* **確認根拠**：`template/management/scripts/doctor.py`（L58, L97）の閉じフェンス判定へ `and not line[fm.end():].strip()` が追加され、Category 2（L217-L246）へリポジトリ外シンボリックリンク `ERROR`・存在しない／非ファイル `WARN` 検査が実装されていること、および `tests/test_daily_scripts.py`（L904-L914）の外部シンボリックリンク検証を確認。
* **実行環境**：Linux / 読み取り専用独立ワーカー（親セッションにて `unittest` 33/33 OK・`doctor.py` OK=9/WARN=0/ERROR=0 確認済み）
* **未確認事項**：Windows 実機でのシンボリックリンク挙動
