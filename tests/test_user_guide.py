"""Tests ensuring docs/04.user-guide/ and template/management/01.manual/ stay identical and self-contained."""

from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

from tests.helpers import REPO_ROOT

SCRIPTS_DIR = REPO_ROOT / "template" / "management" / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from _lib.fs import check_utf8_lf
from _lib.markdown_links import check_markdown_structure, extract_relative_links

EXPECTED_GUIDES = [
    "01.getting-started.md",
    "02.tutorial.md",
    "03.cheatsheet.md",
    "04.user-guide.md",
    "05.worker-models.md",
    "index.md",
]
FORBIDDEN_TERMS = ("正本", "非侵襲")


def _find_untrailed_soft_breaks(text: str) -> list[int]:
    lines = text.splitlines()
    in_fence = False
    bad_lines: list[int] = []
    block_start_re = re.compile(r"^(#{1,6}\s|```|~~~|\||>|\s*[-*+]\s|\s*\d+\.\s|<!--|---+$)")
    for i in range(len(lines) - 1):
        line = lines[i]
        nxt = lines[i + 1]
        stripped = line.strip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if not stripped or not nxt.strip():
            continue
        if block_start_re.match(stripped) and not re.match(r"^(\s*[-*+]\s|\s*\d+\.\s)", line):
            continue
        if block_start_re.match(nxt.strip()):
            continue
        if not line.endswith("  "):
            bad_lines.append(i + 1)
    return bad_lines


class TestUserGuideSyncAndQuality(unittest.TestCase):
    def test_user_guide_and_template_manual_exact_sync(self) -> None:
        ug_dir = REPO_ROOT / "docs" / "04.user-guide"
        manual_dir = REPO_ROOT / "template" / "management" / "01.manual"

        ug_files = sorted(p.relative_to(ug_dir).as_posix() for p in ug_dir.rglob("*") if p.is_file())
        manual_files = sorted(p.relative_to(manual_dir).as_posix() for p in manual_dir.rglob("*") if p.is_file())

        self.assertEqual(ug_files, EXPECTED_GUIDES)
        self.assertEqual(manual_files, EXPECTED_GUIDES)
        self.assertNotIn("workflow-reference.md", manual_files)

        for rel in EXPECTED_GUIDES:
            ug_bytes = (ug_dir / rel).read_bytes()
            manual_bytes = (manual_dir / rel).read_bytes()
            self.assertEqual(ug_bytes, manual_bytes, f"Mismatch between docs/04.user-guide/{rel} and template/management/01.manual/{rel}")

    def test_user_guide_links_self_contained_and_markdown_clean(self) -> None:
        ug_dir = (REPO_ROOT / "docs" / "04.user-guide").resolve()
        for rel in EXPECTED_GUIDES:
            p = ug_dir / rel
            self.assertEqual(check_utf8_lf(p), [], f"UTF-8/LF issue in {rel}")
            text = p.read_text(encoding="utf-8")

            # No ASCII control chars other than newline/tab
            bad_ctrl = [ch for ch in text if ord(ch) < 32 and ch not in ("\n", "\t")]
            self.assertEqual(bad_ctrl, [], f"Control characters found in {rel}")

            # No forbidden terms
            for term in FORBIDDEN_TERMS:
                self.assertNotIn(term, text, f"Forbidden term {term!r} found in {rel}")

            # Markdown structure & soft breaks
            self.assertEqual(check_markdown_structure(text), [], f"Structure warnings in {rel}")
            self.assertEqual(_find_untrailed_soft_breaks(text), [], f"Soft breaks without trailing two spaces in {rel}")

            # All relative links must resolve inside docs/04.user-guide/
            for link in extract_relative_links(text):
                target_str = link.path_part
                resolved = (p.parent / target_str).resolve()
                self.assertTrue(
                    resolved.is_relative_to(ug_dir),
                    f"Relative link {target_str!r} in {rel} escapes docs/04.user-guide/",
                )
                self.assertTrue(
                    resolved.is_file(),
                    f"Broken relative link {target_str!r} in {rel}",
                )

    def test_template_agents_md_links_exist_in_manual(self) -> None:
        tpl_agents = REPO_ROOT / "template" / "AGENTS.md"
        text = tpl_agents.read_text(encoding="utf-8")
        links = extract_relative_links(text)
        manual_links = [lk.path_part for lk in links if lk.path_part.startswith("management/01.manual/")]
        self.assertGreaterEqual(len(manual_links), len(EXPECTED_GUIDES))
        for lk in manual_links:
            target = REPO_ROOT / "template" / lk
            self.assertTrue(target.is_file(), f"template/AGENTS.md link missing: {lk}")


if __name__ == "__main__":
    unittest.main()
