---
id: implementation-round1-005-doctor-fence-test-does-not-exercise-info-string-check
title: doctor.py 閉じフェンス回帰テストが末尾情報文字列チェック分岐を通過していない
status: done
created: 2026-11-25 20:37:04
updated: 2026-11-25 21:58:58
severity: minor
reviewer: worker-middle
---

# doctor.py 閉じフェンス回帰テストが末尾情報文字列チェック分岐を通過していない

## 対象

* `tests/test_daily_scripts.py`（L874-L881：`test_human_review_status_and_doctor_quality_gates`）
* 比較基点：`d3a54b4`

## 指摘内容と根拠

`implementation-round1-003` 対応で追加した `nested_fence_block` は外側フェンスが 4 バッククォート（````` ````markdown `````：`fence_len = 4`）、内側行が 3 バッククォート（```` ```bash ````：`len(marker) = 3`）となっている。  
`doctor.py`（L58, L97）の判定式 `elif marker[0] == fence_char and len(marker) >= fence_len and not line[fm.end():].strip():` では `3 >= 4` の時点で短絡評価により `False` となるため、今回追加した `and not line[fm.end():].strip()` 分岐が一度も評価されていない。

**推奨修正案**：
* 外側フェンスと内側行を同じ 3 バッククォート（例：外側 ```` ```markdown ````、内側 ```` ```bash ````）にし、さらに内部へダミー H2 見出し（`## Fake H2 inside fence`）も含めることで、`_extract_h2_section`（L58）と `_find_unchecked_acs`（L97）双方の `and not line[fm.end():].strip()` 分岐を確実に検証する。

## 採否判断（人間選別）

採用（in-progress）：2026-11-25 人間トリアージにより採用確定。
doctor.py の閉じフェンス末尾情報文字列チェック分岐を確実に回帰検証できるようテストを修正する。

## 修正内容

* `tests/test_daily_scripts.py`（`test_human_review_status_and_doctor_quality_gates`）の閉じフェンス回帰テストを、外側・内側とも同じ 3 バッククォート（```` ```markdown ```` 内の ```` ```bash ````）に揃えて修正した。
* `p_doc_bad` 実行前に既存未チェック AC より前へダミー H2 見出し（`## Fake H2 inside fence`）付き 3 バッククォートブロックを挿入し、`_extract_h2_section`（`doctor.py` L58）の末尾情報文字列チェック分岐が壊れた場合に未チェック AC 検知漏れで失敗するよう強化した。
* `p_doc_ok` 実行前に同じ 3 バッククォートブロック内の ```` ```bash ```` 直後へ未チェック風行（`- [ ] code example inside fence with info-string should be ignored`）を追加し、`_find_unchecked_acs`（`doctor.py` L97）の末尾情報文字列チェック分岐が壊れた場合に誤検知で失敗するよう強化した。
* `python3 -m unittest discover -s tests -v`（33/33 OK）および `uv run management/scripts/doctor.py --json`（OK=9 / WARN=0 / ERROR=0）の通過を確認した。
* 関連コミット：未コミット（作業ツリー上）

## 独立再確認結果

* **判定**：解消（`done`）
* **確認根拠**：`tests/test_daily_scripts.py`（L856-L915：`test_human_review_status_and_doctor_quality_gates`）にて外側・内側とも 3 バッククォートへ統一され、`p_doc_bad` 前のダミー H2 挿入により `doctor.py` の `_extract_h2_section`（L62）の `and not line[fm.end():].strip()` 分岐が、`p_doc_ok` 前の `- [ ]` 挿入により `_find_unchecked_acs`（L102）の同分岐がそれぞれ確実に評価・回帰検証される構造であることを実物照合で確認した。全行通読および親側 `git diff --stat d3a54b4` にて意図しない破損・回帰・新規問題がないことも確認した。
* **実行環境**：Linux / 読み取り専用独立ワーカー（親セッションにて `unittest` 33/33 OK・`doctor.py` OK=9/WARN=0/ERROR=0 確認済み）
* **未確認事項**：サブエージェント内でのコマンド直接再実行（サンドボックス制約のため親側実績前提）、Windows 実機でのシンボリックリンク挙動
