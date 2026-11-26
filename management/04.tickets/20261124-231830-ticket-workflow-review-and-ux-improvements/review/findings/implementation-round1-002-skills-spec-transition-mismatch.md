---
id: implementation-round1-002-skills-spec-transition-mismatch
title: 06.skills.md と SKILL.md・validation.py 間の状態遷移記載の不整合
status: done
created: 2026-11-25 10:03:21
updated: 2026-11-25 20:37:04
severity: minor
reviewer: worker-middle
---

# 06.skills.md と SKILL.md・validation.py 間の状態遷移記載の不整合

## 対象

* `docs/03.spec/06.skills.md`（L85, L97, L100, L254-L255, L374）
* `template/.agents/skills/aico-review/SKILL.md`（L23, L56）
* 比較基点：`d3a54b4`

## 指摘内容と根拠

1. **`aico-ticket-plan` の `planning → closing` スキップ記載漏れ**：`validation.py` L435、`03.workflow.md`、`07.scripts.md`、`aico-ticket-plan/SKILL.md` は `planning → closing / working` を正規遷移としているが、`06.skills.md` 2.1節一覧表（L85）および 3.3節 `aico-ticket-plan`（L254-L255）に反映されていない。
2. **`06.skills.md` 2.1節一覧表のレビュー遷移記載漏れ**：3.4節本文には人間レビュー即採用（`<phase>/fixing`）および同一フェーズ追加ラウンド（`<phase>/reviewing`）が追記されているが、2.1節一覧表の `aico-review`（L97）・`aico-review-recheck`（L100）の「完了時の状態更新」列が旧記載のまま残っている。
3. **`aico-review` 人間レビュー記録モードの開始可能状態不一致**：`06.skills.md` L374 と `validation.py` L421-L427 は `re-reviewing` からの遷移も許可しているが、`template/.agents/skills/aico-review/SKILL.md` L23・L56 には `working` と `reviewing` のみ記載されており `re-reviewing` が抜けている。

**推奨修正案**：
* `docs/03.spec/06.skills.md` の 2.1節一覧表（`aico-ticket-plan`・`aico-review`・`aico-review-recheck`）および 3.3節 `aico-ticket-plan` を最新遷移仕様へ揃える。
* `template/.agents/skills/aico-review/SKILL.md` L23・L56 へ `re-reviewing` からの開始可否を `06.skills.md` と揃えて明記する。

## 採否判断（人間選別）

採用（in-progress）：2026-11-25 人間トリアージにより全 4 件採用確定。エッジケース防御・仕様とスキルの整合性・CI ガイドの正確性を確保するため修正を実施する。

## 修正内容

* `docs/03.spec/06.skills.md` 2.1節一覧表の `aico-ticket-plan`（`closing/working` 追加）・`aico-review`（人間レビュー記録モードの前提条件 `working / reviewing / re-reviewing` および即採用 `<phase>/fixing` 追加）・`aico-review-recheck`（同一フェーズ追加ラウンド `<phase>/reviewing` 追加）、および 3.3節 `aico-ticket-plan` の手順3・状態更新へ `closing / working` を反映した。
* `template/.agents/skills/aico-review/SKILL.md` の前提条件および手順2-4へ `re-reviewing` からの開始・`fixing` 直接遷移（`--force` 不要）を追記し、`06.skills.md` および `validation.py` と完全整合させた。
* 関連コミット：未コミット（作業ツリー上）

## 独立再確認結果

* **判定**：解消（`done`）
* **確認根拠**：`docs/03.spec/06.skills.md` 2.1節一覧表（L99, L112, L115）・3.3節 `aico-ticket-plan`（L273-L274）および `template/.agents/skills/aico-review/SKILL.md`（L23, L56-L58）が `validation.py`（L420-L426, L435）・`03.workflow.md`（L65）と完全整合していることを確認。
* **実行環境**：Linux / 読み取り専用独立ワーカー
* **未確認事項**：なし
