# マイグレーション定義（`installer/migrations/`）

## 概要

`installer/migrations/` には、AIco のバージョンアップに伴う既存記録・設定ファイルの構造変換を行うマイグレーションスクリプトを配置する。  
`v0.1.0`（初版）時点では移行元バージョンが存在しないため、マイグレーションスクリプトは未配置である。

本ドキュメントでは以下を定める。

* ファイル命名規則
* モジュール契約（必須定数・必須関数）
* 実行順序と安全原則

## 1. ファイル命名規則

* ファイル名は `v<FROM>_to_v<TO>.py` 形式とする（例：`v0.1.0_to_v0.2.0.py`）。
* アンダースコア始まり（`_*.py`）のファイルは補助モジュールとして扱い、マイグレーション探索対象から除外する。
* Python 3.11 以上・標準ライブラリのみで動作させること。

## 2. モジュール契約

各マイグレーションスクリプトは、以下の定数および4つの関数を必ず定義する。

| 識別子 | 種別 | 役割 |
| :--- | :--- | :--- |
| `FROM_VERSION` | `str` | 移行元 SemVer 文字列（例：`"0.1.0"`） |
| `TO_VERSION` | `str` | 移行先 SemVer 文字列（例：`"0.2.0"`、`FROM_VERSION < TO_VERSION`） |
| `check(ctx)` | 関数 | 適用前の前提条件・対象構造の妥当性を検証する。問題があれば例外送出、`False`、`(False, 理由)`、または非空エラーリストを返す |
| `plan(ctx)` | 関数 | `--dry-run` 向けの変更予定リスト（`list[str]`）を返す。実ファイルは変更しない |
| `apply(ctx)` | 関数 | 既存記録・`aico-manifest.json` 等の安全な変換を原子的に適用し、変更したパス一覧を返す |
| `verify(ctx)` | 関数 | 変換後のスキーマ・リンク整合を検証する。問題があれば例外送出、`False`、`(False, 理由)`、または非空エラーリストを返す |

`ctx` 辞書には以下のキーが渡される。

```python
{
    "repo_root": Path,        # 導入先 Git リポジトリルート
    "management_root": Path,  # 導入先の管理ルート絶対パス
    "manifest_path": Path,    # aico-manifest.json の絶対パス
    "source_dir": Path,       # 目標版 AIco 配布元ルート
    "current_version": str,   # 更新前の aico_version
    "target_version": str,    # 更新先の aico_version
    "dry_run": bool,          # --dry-run 指定有無
}
```

## 3. 実行順序と安全原則

* `installer/upgrade.py` は `FROM_VERSION` → `TO_VERSION` の有向グラフから現在版〜目標版の経路を解決し、複数バージョン跨ぎでも中間版を飛ばさず古い順に逐次実行する。
* すべての `apply(ctx)` は原子的なファイル更新かつべき等（同一状態への再適用で破損しない）であること。
* `check(ctx)`・`apply(ctx)`・`verify(ctx)` のいずれかが失敗した場合、`upgrade.py` は後続ステップを即座に停止し終了コード `1` で終了する。
