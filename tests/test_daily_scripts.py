"""CLI / E2E integration tests for all 15 daily scripts, _launcher.py, and tools/aico.sh."""

from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

from tests.helpers import (
    git,
    parse_json_output,
    run_cmd,
    run_script,
    setup_installed_repo,
    snapshot_tree,
)


class TestDailyScriptsEndToEnd(unittest.TestCase):
    def test_full_ticket_discussion_adr_review_archive_workflow(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            repo = setup_installed_repo(Path(td) / "proj", integration_branch="develop")

            # 1. --dry-run creates zero changes
            snap_before = snapshot_tree(repo)
            p_dry = run_script(
                repo,
                "create_discussion.py",
                "--slug",
                "kickoff",
                "--title",
                "キックオフ議事録",
                "--dry-run",
                "--json",
            )
            self.assertEqual(p_dry.returncode, 0, p_dry.stderr)
            d_dry = parse_json_output(p_dry)
            self.assertEqual(d_dry["status"], "ok")
            self.assertEqual(snapshot_tree(repo), snap_before)

            # 2. Invalid slug -> exit 2
            p_bad = run_script(repo, "create_discussion.py", "--slug", "Bad_Slug", "--title", "x")
            self.assertEqual(p_bad.returncode, 2)

            # 3. Create discussion
            p_disc = run_script(
                repo,
                "create_discussion.py",
                "--slug",
                "kickoff",
                "--title",
                "キックオフ議事録",
                "--json",
            )
            self.assertEqual(p_disc.returncode, 0, p_disc.stdout + p_disc.stderr)
            disc = parse_json_output(p_disc)
            disc_id = disc["id"]
            disc_path = repo / disc["path"]
            self.assertTrue(disc_path.is_file())

            # 4. Create ADR #1 (accepted) linked to discussion
            p_adr1 = run_script(
                repo,
                "create_adr.py",
                "--slug",
                "auth-v1",
                "--title",
                "認証方式v1",
                "--status",
                "accepted",
                "--discussion",
                disc_id,
                "--json",
            )
            self.assertEqual(p_adr1.returncode, 0, p_adr1.stdout + p_adr1.stderr)
            adr1 = parse_json_output(p_adr1)
            adr1_id = adr1["id"]
            self.assertIn(adr1_id, disc_path.read_text(encoding="utf-8"))

            # 5. ADR --supersedes with --status open must fail (exit 1)
            p_adr_fail = run_script(
                repo,
                "create_adr.py",
                "--slug",
                "auth-v2-draft",
                "--title",
                "認証方式v2ドラフト",
                "--status",
                "open",
                "--supersedes",
                adr1_id,
                "--json",
            )
            self.assertEqual(p_adr_fail.returncode, 1)

            # 6. Create ADR #2 (accepted) superseding ADR #1
            p_adr2 = run_script(
                repo,
                "create_adr.py",
                "--slug",
                "auth-v2",
                "--title",
                "認証方式v2",
                "--status",
                "accepted",
                "--supersedes",
                adr1_id,
                "--json",
            )
            self.assertEqual(p_adr2.returncode, 0, p_adr2.stdout + p_adr2.stderr)
            adr2 = parse_json_output(p_adr2)
            adr2_id = adr2["id"]
            adr1_text = (repo / adr1["path"]).read_text(encoding="utf-8")
            self.assertIn("status: deprecated", adr1_text)
            self.assertIn(f"superseded_by: {adr2_id}", adr1_text)

            # 7. Create parent ticket & child ticket with bidirectional sync + discussion & ADR link
            p_parent = run_script(
                repo,
                "create_ticket.py",
                "--slug",
                "epic-auth",
                "--title",
                "認証基盤整備",
                "--discussion",
                disc_id,
                "--adr",
                adr2_id,
                "--json",
            )
            self.assertEqual(p_parent.returncode, 0, p_parent.stdout + p_parent.stderr)
            parent_t = parse_json_output(p_parent)
            parent_id = parent_t["id"]

            p_child = run_script(
                repo,
                "create_ticket.py",
                "--slug",
                "oauth-login",
                "--title",
                "OAuth ログイン実装",
                "--parent",
                parent_id,
                "--branch",
                "feat/{id}",
                "--json",
            )
            self.assertEqual(p_child.returncode, 0, p_child.stdout + p_child.stderr)
            child_t = parse_json_output(p_child)
            child_id = child_t["id"]
            child_index = repo / child_t["path"]
            child_dir = child_index.parent
            self.assertIn(f"branch: feat/{child_id}", child_index.read_text(encoding="utf-8"))
            self.assertIn(child_id, (repo / parent_t["path"]).read_text(encoding="utf-8"))

            # Add cross-links in markdown body to test bidirectional link rewrite on archive later
            disc_path.write_text(
                disc_path.read_text(encoding="utf-8")
                + f"\n参照: [子チケット](../04.tickets/{child_id}/index.md)\n",
                encoding="utf-8",
                newline="\n",
            )
            child_index.write_text(
                child_index.read_text(encoding="utf-8")
                + f"\n関連議事録: [キックオフ](../../02.discussions/{disc_id}.md)\n",
                encoding="utf-8",
                newline="\n",
            )

            # 8. Rebuild indexes on integration branch + verify idempotency
            p_idx1 = run_script(repo, "rebuild_indexes.py", "--json")
            self.assertEqual(p_idx1.returncode, 0, p_idx1.stdout + p_idx1.stderr)
            p_idx2 = run_script(repo, "rebuild_indexes.py", "--json")
            self.assertEqual(p_idx2.returncode, 0)
            self.assertEqual(parse_json_output(p_idx2)["changed_files"], [])

            git(repo, "add", ".")
            git(repo, "commit", "-m", "chore: add records")

            # 9. Switch to feature branch for child ticket
            feat_branch = f"feat/{child_id}"
            git(repo, "checkout", "-b", feat_branch)

            # Integration-only script rejected on feature branch, allowed with --allow-non-integration
            p_guard = run_script(repo, "create_discussion.py", "--slug", "blocked", "--title", "Blocked")
            self.assertEqual(p_guard.returncode, 1)
            p_idx_guard = run_script(repo, "rebuild_indexes.py", "--scope", "all")
            self.assertEqual(p_idx_guard.returncode, 1)
            p_idx_allow = run_script(repo, "rebuild_indexes.py", "--scope", "all", "--allow-non-integration", "--dry-run")
            self.assertEqual(p_idx_allow.returncode, 0)

            # 10. Create ticket notes (auto numbering 001, 002)
            p_n1 = run_script(repo, "create_ticket_note.py", "--ticket", child_id, "--slug", "research", "--title", "調査メモ", "--json")
            self.assertEqual(p_n1.returncode, 0, p_n1.stdout + p_n1.stderr)
            self.assertTrue(parse_json_output(p_n1)["path"].endswith("/notes/001-research.md"))
            p_n2 = run_script(repo, "create_ticket_note.py", "--ticket", child_id, "--slug", "design", "--title", "設計メモ", "--json")
            self.assertEqual(p_n2.returncode, 0)
            self.assertTrue(parse_json_output(p_n2)["path"].endswith("/notes/002-design.md"))

            # 11. Progress ticket via update_frontmatter.py
            # Immutable key rejected even with --force
            p_imm = run_script(repo, "update_frontmatter.py", "--file", child_t["path"], "--set", "id=hacked", "--force")
            self.assertEqual(p_imm.returncode, 1)
            # Invalid 3-axis rejected even with --force
            p_3ax = run_script(
                repo,
                "update_frontmatter.py",
                "--file",
                child_t["path"],
                "--set",
                "status=done",
                "--set",
                "phase=planning",
                "--set",
                "phase_status=done",
                "--force",
            )
            self.assertEqual(p_3ax.returncode, 1)
            # Normal transition: open -> in-progress/planning/working -> implementation/reviewing
            self.assertEqual(
                run_script(
                    repo,
                    "update_frontmatter.py",
                    "--file",
                    child_t["path"],
                    "--set",
                    "status=in-progress",
                    "--set",
                    "phase=planning",
                    "--set",
                    "phase_status=working",
                ).returncode,
                0,
            )
            # Design skip (planning -> implementation/working) then -> reviewing allowed without --force
            self.assertEqual(
                run_script(
                    repo,
                    "update_frontmatter.py",
                    "--file",
                    child_t["path"],
                    "--set",
                    "phase=implementation",
                    "--set",
                    "phase_status=working",
                ).returncode,
                0,
            )
            self.assertEqual(
                run_script(
                    repo,
                    "update_frontmatter.py",
                    "--file",
                    child_t["path"],
                    "--set",
                    "phase_status=reviewing",
                ).returncode,
                0,
            )

            # 12. Review findings + record_review_run + scoped rebuild_indexes on feature branch
            p_f1 = run_script(
                repo,
                "create_review_finding.py",
                "--target",
                child_id,
                "--slug",
                "token-expiry",
                "--title",
                "トークン期限検証漏れ",
                "--severity",
                "major",
                "--reviewer",
                "worker-high",
                "--json",
            )
            self.assertEqual(p_f1.returncode, 0, p_f1.stdout + p_f1.stderr)
            f1 = parse_json_output(p_f1)
            self.assertIn("implementation-round1-001-token-expiry.md", f1["path"])

            p_rr1 = run_script(
                repo,
                "record_review_run.py",
                "--target",
                child_id,
                "--kind",
                "initial",
                "--reviewer",
                "worker-high",
                "--base-commit",
                "develop",
                "--env",
                "Linux / Python 3.14",
                "--json",
            )
            self.assertEqual(p_rr1.returncode, 0, p_rr1.stdout + p_rr1.stderr)

            # Next round finding (--next-round -> round2)
            p_f2 = run_script(
                repo,
                "create_review_finding.py",
                "--target",
                child_id,
                "--slug",
                "edge-case",
                "--title",
                "境界値テスト不足",
                "--severity",
                "minor",
                "--reviewer",
                "worker-high",
                "--next-round",
                "--json",
            )
            self.assertEqual(p_f2.returncode, 0, p_f2.stdout + p_f2.stderr)
            f2 = parse_json_output(p_f2)
            self.assertIn("implementation-round2-001-edge-case.md", f2["path"])

            # Scoped rebuild_indexes for reviews IS allowed on feature branch
            p_rev_idx = run_script(
                repo, "rebuild_indexes.py", "--scope", "reviews", "--target", child_id, "--json"
            )
            self.assertEqual(p_rev_idx.returncode, 0, p_rev_idx.stdout + p_rev_idx.stderr)

            # Update plan.md with checklist for ticket_status check
            (child_dir / "plan.md").write_text(
                "# 計画\n\n* [x] タスク1\n* [ ] タスク2\n", encoding="utf-8", newline="\n"
            )

            # 13. ticket_status.py auto-detects ticket from current branch
            p_st = run_script(repo, "ticket_status.py", "--json")
            self.assertEqual(p_st.returncode, 0, p_st.stdout + p_st.stderr)
            st_data = parse_json_output(p_st)["data"]
            self.assertEqual(st_data["ticket"]["id"], child_id)
            self.assertEqual(st_data["plan_progress"], {"done": 1, "total": 2})
            self.assertEqual(st_data["findings"]["counts"]["open"], 2)
            self.assertEqual(st_data["recommended_next_skill"], "aico-review")

            # Cannot close ticket while unresolved findings exist (EVEN with --force!)
            self.assertEqual(
                run_script(
                    repo,
                    "update_frontmatter.py",
                    "--file",
                    child_t["path"],
                    "--set",
                    "phase=closing",
                    "--set",
                    "phase_status=working",
                ).returncode,
                0,
            )
            p_done_blocked = run_script(
                repo,
                "update_frontmatter.py",
                "--file",
                child_t["path"],
                "--set",
                "status=done",
                "--set",
                "phase=closing",
                "--set",
                "phase_status=done",
                "--force",
            )
            self.assertEqual(p_done_blocked.returncode, 1)

            # Resolve both findings (open -> in-progress -> done, and open -> cancelled)
            self.assertEqual(
                run_script(repo, "update_frontmatter.py", "--file", f1["path"], "--set", "status=in-progress").returncode,
                0,
            )
            self.assertEqual(
                run_script(repo, "update_frontmatter.py", "--file", f1["path"], "--set", "status=done").returncode,
                0,
            )
            self.assertEqual(
                run_script(repo, "update_frontmatter.py", "--file", f2["path"], "--set", "status=cancelled").returncode,
                0,
            )
            run_script(repo, "rebuild_indexes.py", "--scope", "reviews", "--target", child_id)

            # 14. Project code changes + update_changed_files.py (including rename + dirty warn + idempotency)
            src_dir = repo / "src"
            src_dir.mkdir()
            (src_dir / "app.py").write_text("print('hello')\n", encoding="utf-8", newline="\n")
            git(repo, "add", "src/app.py")
            git(repo, "commit", "-m", "feat: add app.py")

            # Dirty tree triggers WARN
            (repo / "temp_dirty.txt").write_text("dirty\n", encoding="utf-8")
            p_cf1 = run_script(repo, "update_changed_files.py", "--json")
            self.assertEqual(p_cf1.returncode, 0, p_cf1.stdout + p_cf1.stderr)
            cf1 = parse_json_output(p_cf1)
            self.assertEqual(cf1["status"], "warn")
            self.assertEqual(cf1["data"]["entries"], [{"status": "A", "path": "src/app.py"}])
            (repo / "temp_dirty.txt").unlink()

            # 2nd run is idempotent (0 changed files)
            p_cf2 = run_script(repo, "update_changed_files.py", "--json")
            self.assertEqual(p_cf2.returncode, 0)
            self.assertEqual(parse_json_output(p_cf2)["changed_files"], [])

            # Now ticket can be closed
            p_done_ok = run_script(
                repo,
                "update_frontmatter.py",
                "--file",
                child_t["path"],
                "--set",
                "status=done",
                "--set",
                "phase=closing",
                "--set",
                "phase_status=done",
                "--json",
            )
            self.assertEqual(p_done_ok.returncode, 0, p_done_ok.stdout + p_done_ok.stderr)

            # On feature branch, done ticket recommends aico-ticket-pr
            p_st_pr = run_script(repo, "ticket_status.py", "--json")
            self.assertEqual(parse_json_output(p_st_pr)["data"]["recommended_next_skill"], "aico-ticket-close")

            git(repo, "add", ".")
            git(repo, "commit", "-m", "feat: complete child ticket")

            # Merge back to develop
            git(repo, "checkout", "develop")
            git(repo, "merge", "--no-ff", feat_branch, "-m", "merge feat")

            # Before rebuild_indexes, ticket_status reports rebuild_indexes needed
            p_st_unref = run_script(repo, "ticket_status.py", "--ticket", child_id, "--json")
            self.assertEqual(parse_json_output(p_st_unref)["data"]["recommended_next_skill"], "aico-ticket-close")

            run_script(repo, "rebuild_indexes.py")
            p_st_ref = run_script(repo, "ticket_status.py", "--ticket", child_id, "--json")
            self.assertEqual(parse_json_output(p_st_ref)["data"]["recommended_next_skill"], "none")

            # 15. Archive tests
            # Accepted ADR cannot be archived
            self.assertEqual(run_script(repo, "archive_record.py", "--target", adr2_id).returncode, 1)
            # Active parent ticket cannot be archived
            self.assertEqual(run_script(repo, "archive_record.py", "--target", parent_id).returncode, 1)

            # Dry-run archive does not modify files
            snap_arch = snapshot_tree(repo)
            p_arch_dry = run_script(repo, "archive_record.py", "--target", child_id, "--dry-run", "--json")
            self.assertEqual(p_arch_dry.returncode, 0, p_arch_dry.stdout + p_arch_dry.stderr)
            adry = parse_json_output(p_arch_dry)["data"]
            self.assertGreaterEqual(adry["external_links_rewritten"], 1)
            self.assertGreaterEqual(adry["internal_links_rewritten"], 1)
            self.assertEqual(snapshot_tree(repo), snap_arch)

            # Real archive of done child ticket & deprecated ADR #1
            p_arch = run_script(repo, "archive_record.py", "--target", child_id, "--json")
            self.assertEqual(p_arch.returncode, 0, p_arch.stdout + p_arch.stderr)
            self.assertTrue((repo / "management" / "04.tickets" / "archived" / child_id / "index.md").is_file())
            self.assertIn(f"04.tickets/archived/{child_id}/index.md", disc_path.read_text(encoding="utf-8"))
            self.assertIn(
                f"../../../02.discussions/{disc_id}.md",
                (repo / "management" / "04.tickets" / "archived" / child_id / "index.md").read_text(encoding="utf-8"),
            )

            # Archiving already-archived record fails
            self.assertEqual(run_script(repo, "archive_record.py", "--target", child_id).returncode, 1)

            # Deprecated ADR can be archived
            self.assertEqual(run_script(repo, "archive_record.py", "--target", adr1_id).returncode, 0)

            # Doctor passes with 0 errors (all cross-refs & links valid after archive!)
            p_doc = run_script(repo, "doctor.py", "--json")
            doc_data = parse_json_output(p_doc)
            self.assertEqual(p_doc.returncode, 0, json.dumps(doc_data, ensure_ascii=False, indent=2))
            self.assertEqual(doc_data["errors"], [])

    def test_runbook_and_review_workflow(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            repo = setup_installed_repo(Path(td) / "rbproj", integration_branch="main")

            p_rb = run_script(repo, "create_runbook.py", "--slug", "db-backup", "--title", "DB バックアップ手順", "--json")
            self.assertEqual(p_rb.returncode, 0, p_rb.stdout + p_rb.stderr)

            # Duplicate runbook fails (exit 1)
            self.assertEqual(
                run_script(repo, "create_runbook.py", "--slug", "db-backup", "--title", "重複").returncode,
                1,
            )

            p_rec = run_script(
                repo,
                "create_runbook_record.py",
                "--runbook",
                "db-backup",
                "--slug",
                "monthly",
                "--title",
                "月次バックアップ実施",
                "--json",
            )
            self.assertEqual(p_rec.returncode, 0, p_rec.stdout + p_rec.stderr)
            rec = parse_json_output(p_rec)
            rec_ref = f"db-backup/{rec['id']}"

            # Record review run with 0 findings initializes review/index.md cleanly
            p_rr = run_script(
                repo,
                "record_review_run.py",
                "--target",
                rec_ref,
                "--kind",
                "initial",
                "--reviewer",
                "worker-middle",
                "--base-commit",
                "HEAD",
                "--env",
                "Linux",
                "--json",
            )
            self.assertEqual(p_rr.returncode, 0, p_rr.stdout + p_rr.stderr)
            rev_idx = repo / "management" / "05.runbooks" / "db-backup" / "records" / rec["id"] / "review" / "index.md"
            self.assertTrue(rev_idx.is_file())
            self.assertIn("| - | round1 | 初回レビュー |", rev_idx.read_text(encoding="utf-8"))

            # --phase is rejected on runbook_record finding
            self.assertEqual(
                run_script(
                    repo,
                    "create_review_finding.py",
                    "--target",
                    rec_ref,
                    "--slug",
                    "bad",
                    "--title",
                    "Bad",
                    "--severity",
                    "minor",
                    "--reviewer",
                    "w",
                    "--phase",
                    "planning",
                ).returncode,
                2,
            )

            # Finding on runbook_record succeeds without --phase
            p_rf = run_script(
                repo,
                "create_review_finding.py",
                "--target",
                rec_ref,
                "--slug",
                "log-check",
                "--title",
                "ログ確認追記",
                "--severity",
                "minor",
                "--reviewer",
                "worker-middle",
                "--json",
            )
            self.assertEqual(p_rf.returncode, 0, p_rf.stdout + p_rf.stderr)
            self.assertIn("round1-001-log-check.md", parse_json_output(p_rf)["path"])

            # Followup discussion linked from runbook_record
            p_fu = run_script(
                repo,
                "create_discussion.py",
                "--slug",
                "backup-improve",
                "--title",
                "バックアップ改善",
                "--followup-from",
                rec_ref,
                "--json",
            )
            self.assertEqual(p_fu.returncode, 0, p_fu.stdout + p_fu.stderr)
            fu_id = parse_json_output(p_fu)["id"]
            self.assertIn(fu_id, (repo / rec["path"]).read_text(encoding="utf-8"))

            # Cannot archive runbook while in-progress record exists
            self.assertEqual(run_script(repo, "archive_record.py", "--target", "db-backup").returncode, 1)

            # Complete runbook_record -> archive runbook_record -> archive runbook
            self.assertEqual(
                run_script(repo, "update_frontmatter.py", "--file", rec["path"], "--set", "status=done").returncode,
                0,
            )
            self.assertEqual(run_script(repo, "archive_record.py", "--target", rec_ref).returncode, 0)
            self.assertEqual(run_script(repo, "archive_record.py", "--target", "db-backup").returncode, 0)

            p_doc = run_script(repo, "doctor.py", "--json")
            self.assertEqual(p_doc.returncode, 0, p_doc.stdout)

    def test_sync_agents_and_doctor_all_categories(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            repo = setup_installed_repo(Path(td) / "syncproj", integration_branch="main")

            # Add custom skill and custom agent
            custom_skill = repo / ".agents" / "skills" / "my-custom" / "SKILL.md"
            custom_skill.parent.mkdir(parents=True)
            custom_skill.write_text(
                "---\nname: my-custom\ndescription: Custom skill\n---\n\n# my-custom\n",
                encoding="utf-8",
                newline="\n",
            )
            custom_agent = repo / ".claude" / "agents" / "my-reviewer.md"
            custom_agent.write_text("# Custom Agent\n", encoding="utf-8", newline="\n")

            # --check detects drift without modifying files
            p_chk = run_script(repo, "sync_agents.py", "--check", "--json")
            self.assertEqual(p_chk.returncode, 1)
            self.assertFalse((repo / ".claude" / "skills" / "my-custom" / "SKILL.md").exists())

            # Apply sync -> mirrors custom skill and keeps custom agent
            p_sync1 = run_script(repo, "sync_agents.py", "--json")
            self.assertEqual(p_sync1.returncode, 0, p_sync1.stdout + p_sync1.stderr)
            self.assertTrue((repo / ".claude" / "skills" / "my-custom" / "SKILL.md").is_file())
            self.assertTrue((repo / ".github" / "skills" / "my-custom" / "SKILL.md").is_file())
            self.assertTrue(custom_agent.is_file())

            # Idempotent 2nd run + --check returns 0
            p_sync2 = run_script(repo, "sync_agents.py", "--json")
            self.assertEqual(parse_json_output(p_sync2)["changed_files"], [])
            self.assertEqual(run_script(repo, "sync_agents.py", "--check").returncode, 0)

            # Doctor --strict fails because worker_models are empty (WARN)
            p_strict1 = run_script(repo, "doctor.py", "--strict", "--json")
            self.assertEqual(p_strict1.returncode, 1)
            self.assertEqual(parse_json_output(p_strict1)["status"], "warn")

            # Populate worker_models -> sync -> doctor --strict passes!
            m_path = repo / "management" / "aico-manifest.json"
            m = json.loads(m_path.read_text(encoding="utf-8"))
            for t in m["tools"]:
                for lvl in ("high", "middle", "low"):
                    m["worker_models"][t][lvl]["model"] = f"{t}-{lvl}"
                    m["worker_models"][t][lvl]["effort"] = lvl
            m_path.write_text(json.dumps(m, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
            run_script(repo, "sync_agents.py")

            p_strict_ok = run_script(repo, "doctor.py", "--strict", "--json")
            doc_ok = parse_json_output(p_strict_ok)
            if shutil.which("uv") is not None:
                self.assertEqual(p_strict_ok.returncode, 0, json.dumps(doc_ok, ensure_ascii=False, indent=2))

            # Introduce faults across categories and verify doctor detects them
            (repo / "GEMINI.md").write_text("# forbidden\n", encoding="utf-8")
            (repo / "management" / "archived").mkdir()
            (repo / ".agents" / "skills" / "my-custom" / "bad.py").write_text("print(1)\n", encoding="utf-8")
            (repo / "management" / "01.manual" / "01.getting-started.md").write_text(
                "# Title\n\n[broken](./does-not-exist.md)\n", encoding="utf-8", newline="\n"
            )
            p_bad_doc = run_script(repo, "doctor.py", "--json")
            self.assertEqual(p_bad_doc.returncode, 1)
            bad_d = parse_json_output(p_bad_doc)
            all_err = "\n".join(bad_d["errors"])
            all_warn = "\n".join(bad_d["warnings"])
            self.assertIn("GEMINI.md", all_warn)
            self.assertIn("archived/", all_err)
            self.assertIn("bad.py", all_err)
            self.assertIn("リンク先が存在しません", all_err)

    def test_wrapper_japanese_space_path_nontty_and_no_uv_fallback(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            repo = setup_installed_repo(Path(td) / "テスト repo スペース", integration_branch="main")
            wrapper = repo / "tools" / "aico.sh"

            # Non-TTY no-args returns exit 0 with menu (no hang)
            p_menu = run_cmd(["bash", str(wrapper)], repo, stdin_text="")
            self.assertEqual(p_menu.returncode, 0, p_menu.stderr)
            self.assertIn("doctor", p_menu.stdout)

            # Unknown command returns exit 2
            p_unk = run_cmd(["bash", str(wrapper), "unknown_cmd"], repo)
            self.assertEqual(p_unk.returncode, 2)

            # Run doctor via wrapper with Japanese/space path & without uv on PATH (Python fallback)
            no_uv_bin = Path(td) / "bin_no_uv"
            no_uv_bin.mkdir()
            for tool_name in ("python3", "git", "bash", "dirname", "pwd"):
                found = shutil.which(tool_name)
                if found:
                    (no_uv_bin / tool_name).symlink_to(found)
            p_fb = run_cmd(
                ["bash", str(wrapper), "doctor", "--json"],
                repo,
                env={"PATH": str(no_uv_bin)},
            )
            self.assertEqual(p_fb.returncode, 0, p_fb.stdout + p_fb.stderr)
            d_fb = parse_json_output(p_fb)
            self.assertTrue(any("uv コマンドが見つかりません" in w for w in d_fb["warnings"]))


if __name__ == "__main__":
    unittest.main()
