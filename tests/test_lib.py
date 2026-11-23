"""Unit tests for template/management/scripts/_lib/ modules."""

from __future__ import annotations

import os
import sys
import tempfile
import tomllib
import unittest
from pathlib import Path
from unittest import mock

from tests.helpers import SCRIPTS_LIB_ROOT

if str(SCRIPTS_LIB_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_LIB_ROOT))

from _lib import (  # noqa: E402
    agents_sync,
    frontmatter,
    fs,
    indexes,
    markdown_links,
    markers,
    naming,
    validation,
)
from _lib.cli import AicoError  # noqa: E402


class TestNaming(unittest.TestCase):
    def test_slug_validation(self) -> None:
        for ok in ("a", "auth-flow", "v2-api-1", "01-test"):
            self.assertTrue(naming.is_valid_slug(ok), ok)
        for bad in ("", "Auth", "-lead", "trail-", "a--b", "a_b", "日本語", "a b"):
            self.assertFalse(naming.is_valid_slug(bad), bad)

    def test_title_validation(self) -> None:
        self.assertTrue(naming.is_valid_title("認証フロー設計"))
        self.assertFalse(naming.is_valid_title(""))
        self.assertFalse(naming.is_valid_title("   "))
        self.assertFalse(naming.is_valid_title("line1\nline2"))
        self.assertFalse(naming.is_valid_title("# heading"))
        self.assertFalse(naming.is_valid_title("tab\tchar"))

    def test_semver(self) -> None:
        self.assertEqual(naming.parse_semver("0.1.0"), (0, 1, 0))
        self.assertEqual(naming.parse_semver("10.2.3"), (10, 2, 3))
        self.assertEqual(naming.parse_semver("v0.1.0"), (0, 1, 0))
        self.assertIsNone(naming.parse_semver("0.1"))
        self.assertIsNone(naming.parse_semver("0.1.0-alpha"))


class TestFrontmatter(unittest.TestCase):
    def test_roundtrip_scalars_lists_nulls(self) -> None:
        data = {
            "id": "20261124-010000-ticket-auth-flow",
            "title": "認証: OAuth2 \"導入\" 検討",
            "status": "open",
            "parent": None,
            "children": [],
            "discussions": ["20261124-005000-discussion-kickoff"],
        }
        body = "# 認証\n\n本文です。\n"
        dumped = frontmatter.dump_frontmatter(data, body, list(data.keys()))
        parsed, parsed_body = frontmatter.parse_frontmatter(dumped)
        self.assertEqual(parsed, data)
        self.assertEqual(parsed_body, body)

    def test_block_list_parsing(self) -> None:
        text = "---\nid: test\nitems:\n  - one\n  - \"two: 2\"\n---\n\nBody\n"
        data, body = frontmatter.parse_frontmatter(text)
        self.assertEqual(data, {"id": "test", "items": ["one", "two: 2"]})
        self.assertEqual(body, "\nBody\n")

    def test_missing_frontmatter(self) -> None:
        data, body = frontmatter.parse_frontmatter("# Just a heading\n")
        self.assertIsNone(data)
        self.assertEqual(body, "# Just a heading\n")


class TestMarkers(unittest.TestCase):
    def test_multiple_unique_auto_markers(self) -> None:
        text = (
            "# Dashboard\n\n"
            "<!-- AICO:AUTO:BEGIN:summary -->\nold1\n<!-- AICO:AUTO:END:summary -->\n\n"
            "<!-- AICO:AUTO:BEGIN:active-tickets -->\nold2\n<!-- AICO:AUTO:END:active-tickets -->\n"
        )
        blocks, errs = markers.validate_markers(text)
        self.assertEqual(errs, [])
        self.assertEqual([b.label for b in blocks], ["summary", "active-tickets"])
        updated = markers.replace_auto_block(text, "summary", "new1")
        updated = markers.replace_auto_block(updated, "active-tickets", "new2")
        self.assertIn("new1", updated)
        self.assertIn("new2", updated)

    def test_detects_duplicate_nested_unclosed_reversed(self) -> None:
        dup = (
            "<!-- AICO:AUTO:BEGIN:list -->\na\n<!-- AICO:AUTO:END:list -->\n"
            "<!-- AICO:AUTO:BEGIN:list -->\nb\n<!-- AICO:AUTO:END:list -->\n"
        )
        _, errs = markers.validate_markers(dup)
        self.assertTrue(any("重複" in e for e in errs))

        nested = (
            "<!-- AICO:AUTO:BEGIN:a -->\n"
            "<!-- AICO:AUTO:BEGIN:b -->\n"
            "<!-- AICO:AUTO:END:b -->\n"
            "<!-- AICO:AUTO:END:a -->\n"
        )
        _, errs2 = markers.validate_markers(nested)
        self.assertTrue(any("入れ子" in e for e in errs2))

        reversed_m = "<!-- AICO:END -->\n<!-- AICO:BEGIN -->\n"
        _, errs3 = markers.validate_markers(reversed_m)
        self.assertTrue(len(errs3) >= 1)

        unclosed = "<!-- AICO:BEGIN -->\nhello\n"
        _, errs4 = markers.validate_markers(unclosed)
        self.assertTrue(len(errs4) >= 1)


class TestFs(unittest.TestCase):
    def test_utf8_lf_checks(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            p = Path(td)
            ok_f = p / "ok.md"
            ok_f.write_bytes("日本語\n".encode("utf-8"))
            self.assertEqual(fs.check_utf8_lf(ok_f), [])

            bom_f = p / "bom.md"
            bom_f.write_bytes(b"\xef\xbb\xbfhello\n")
            self.assertTrue(any("BOM" in e for e in fs.check_utf8_lf(bom_f)))

            crlf_f = p / "crlf.md"
            crlf_f.write_bytes(b"hello\r\nworld\r\n")
            self.assertTrue(any("CRLF" in e for e in fs.check_utf8_lf(crlf_f)))

    def test_atomic_write_idempotency_and_failure_safety(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / "file.txt"
            self.assertTrue(fs.write_text_atomic(target, "v1\n"))
            mtime1 = target.stat().st_mtime_ns
            # Identical content skips write
            self.assertFalse(fs.write_text_atomic(target, "v1\n"))
            self.assertEqual(target.stat().st_mtime_ns, mtime1)

            # Simulated failure during os.replace leaves original intact and cleans up temp file
            with mock.patch("os.replace", side_effect=OSError("disk full")):
                with self.assertRaises(AicoError):
                    fs.write_text_atomic(target, "v2\n")
            self.assertEqual(target.read_text(encoding="utf-8"), "v1\n")
            leftovers = [x.name for x in Path(td).iterdir() if x.name.startswith(".aico-tmp-")]
            self.assertEqual(leftovers, [])


class TestMarkdownLinks(unittest.TestCase):
    def test_extract_links_ignores_code_and_external(self) -> None:
        md = (
            "# Title\n\n"
            "[ok](./other.md#sec)\n"
            "[ext](https://example.com)\n"
            "[anchor](#sec)\n"
            "`[inline](./ignored.md)`\n"
            "```markdown\n[fenced](./also-ignored.md)\n```\n"
        )
        links = markdown_links.extract_relative_links(md)
        self.assertEqual(len(links), 1)
        self.assertEqual(links[0].path_part, "./other.md")
        self.assertEqual(links[0].suffix, "#sec")

    def test_structure_warnings(self) -> None:
        md = "# H1\n\n# Duplicate H1\n\n#### Skipped H4\n\n```\nno lang\n```\n"
        warns = markdown_links.check_markdown_structure(md)
        self.assertTrue(any("H1" in w for w in warns))
        self.assertTrue(any("飛んで" in w for w in warns))
        self.assertTrue(any("言語識別子" in w for w in warns))

    def test_plan_link_rewrites_bidirectional(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            mgmt = Path(td) / "management"
            disc = mgmt / "02.discussions" / "d1.md"
            tkt = mgmt / "04.tickets" / "t1" / "index.md"
            disc.parent.mkdir(parents=True)
            tkt.parent.mkdir(parents=True)
            disc.write_text("# D1\n\nSee [ticket](../04.tickets/t1/index.md)\n", encoding="utf-8")
            tkt.write_text("# T1\n\nSee [disc](../../02.discussions/d1.md)\n", encoding="utf-8")

            new_tkt_dir = mgmt / "04.tickets" / "archived" / "t1"
            plans = markdown_links.plan_link_rewrites_for_move(mgmt, tkt.parent, new_tkt_dir)
            self.assertEqual(len(plans), 2)
            by_internal = {p.is_internal_to_moved: p for p in plans}
            self.assertIn("../04.tickets/archived/t1/index.md", by_internal[False].new_content)
            self.assertIn("../../../02.discussions/d1.md", by_internal[True].new_content)


class TestValidation(unittest.TestCase):
    def test_3axis_validation(self) -> None:
        self.assertEqual(validation.validate_ticket_3axis("open", "drafting", "working"), [])
        self.assertEqual(validation.validate_ticket_3axis("in-progress", "planning", "reviewing"), [])
        self.assertEqual(validation.validate_ticket_3axis("done", "closing", "done"), [])
        self.assertEqual(validation.validate_ticket_3axis("cancelled", "design", "fixing"), [])

        self.assertTrue(validation.validate_ticket_3axis("open", "planning", "working"))
        self.assertTrue(validation.validate_ticket_3axis("done", "implementation", "done"))
        self.assertTrue(validation.validate_ticket_3axis("in-progress", "closing", "done"))

    def test_transitions_and_force(self) -> None:
        old = {
            "id": "20261124-010000-ticket-a",
            "created": "2026-11-24 01:00:00",
            "status": "in-progress",
            "phase": "implementation",
            "phase_status": "working",
        }
        # Normal forward -> closing
        ok_next = {**old, "phase": "closing", "phase_status": "working"}
        self.assertEqual(validation.validate_transition("ticket", old, ok_next, force=False), [])

        # Backwards -> planning rejected without force, allowed with force
        back = {**old, "phase": "planning", "phase_status": "working"}
        self.assertTrue(validation.validate_transition("ticket", old, back, force=False))
        self.assertEqual(validation.validate_transition("ticket", old, back, force=True), [])

        # Immutable key rejected even with force
        bad_id = {**old, "id": "changed"}
        self.assertTrue(validation.validate_transition("ticket", old, bad_id, force=True))

    def test_determine_next_skill_table(self) -> None:
        t_open = {"status": "open", "phase": "drafting", "phase_status": "working"}
        self.assertEqual(
            validation.determine_next_skill(t_open, current_branch="develop", integration_branch="develop")[0],
            "aico-ticket-start",
        )
        t_plan = {"status": "in-progress", "phase": "planning", "phase_status": "working"}
        self.assertEqual(
            validation.determine_next_skill(t_plan, current_branch="feature/x", integration_branch="develop")[0],
            "aico-ticket-plan",
        )
        t_rev = {"status": "in-progress", "phase": "implementation", "phase_status": "reviewing"}
        self.assertEqual(
            validation.determine_next_skill(t_rev, current_branch="feature/x", integration_branch="develop")[0],
            "aico-review",
        )
        t_done = {"status": "done", "phase": "closing", "phase_status": "done"}
        # On feature branch -> aico-ticket-close (post-merge step remaining)
        self.assertEqual(
            validation.determine_next_skill(t_done, current_branch="feature/x", integration_branch="develop")[0],
            "aico-ticket-close",
        )
        # On integration branch but unreflected -> aico-ticket-close
        self.assertEqual(
            validation.determine_next_skill(
                t_done, current_branch="develop", integration_branch="develop", index_reflected=False
            )[0],
            "aico-ticket-close",
        )
        # On integration branch and reflected -> none
        self.assertEqual(
            validation.determine_next_skill(
                t_done, current_branch="develop", integration_branch="develop", index_reflected=True
            )[0],
            "none",
        )


class TestAgentsSyncRenderers(unittest.TestCase):
    def test_codex_toml_valid_with_and_without_model_effort(self) -> None:
        toml1 = agents_sync._render_codex_worker_toml(
            "worker-high", "高精度ワーカー", "本文テスト\n\"quoted\"\n", "", ""
        )
        parsed1 = tomllib.loads(toml1)
        self.assertEqual(parsed1["name"], "worker-high")
        self.assertNotIn("model", parsed1)
        self.assertNotIn("model_reasoning_effort", parsed1)

        toml2 = agents_sync._render_codex_worker_toml(
            "worker-high", "高精度ワーカー", "本文テスト\n", "gpt-5.3-codex", "high"
        )
        parsed2 = tomllib.loads(toml2)
        self.assertEqual(parsed2["model"], "gpt-5.3-codex")
        self.assertEqual(parsed2["model_reasoning_effort"], "high")


if __name__ == "__main__":
    unittest.main()
