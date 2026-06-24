from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path


SCRIPTS_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import recover_session_skills
import session_state


def transcript(*entries: tuple[str, str]) -> str:
    lines = []
    for role, text in entries:
        lines.append(json.dumps({"role": role, "content": text}))
    return "\n".join(lines)


class PairingStateTests(unittest.TestCase):
    def test_extract_pairing_mode_uses_latest_assistant_marker(self) -> None:
        data = transcript(
            ("assistant", "Pairing mode: active"),
            ("assistant", "Pairing mode: bail-current-chunk"),
            ("assistant", "Pairing mode: active"),
        )
        self.assertEqual(session_state.extract_pairing_mode(data), "active")

    def test_extract_pairing_mode_ignores_user_mentions(self) -> None:
        data = transcript(
            ("user", "Pairing mode: active"),
            ("assistant", "No marker here"),
        )
        self.assertEqual(session_state.extract_pairing_mode(data), "none")

    def test_extract_pairing_mode_respects_exit_marker(self) -> None:
        data = transcript(
            ("assistant", "Pairing mode: active"),
            ("assistant", "Pairing mode: exited"),
        )
        self.assertEqual(session_state.extract_pairing_mode(data), "exited")

    def test_pairing_exit_prompt_detection(self) -> None:
        self.assertTrue(session_state.prompt_requests_pairing_exit("stop pairing now"))
        self.assertFalse(session_state.prompt_requests_pairing_exit("Implement the plan."))

    def test_pairing_bail_prompt_detection(self) -> None:
        self.assertTrue(session_state.prompt_requests_pairing_bail("bail and implement this chunk"))
        self.assertFalse(session_state.prompt_requests_pairing_bail("Implement the plan."))


class RecoverSessionSkillsTests(unittest.TestCase):
    def test_build_user_prompt_context_for_active_pairing(self) -> None:
        data = transcript(("assistant", "Pairing mode: active"))
        context = recover_session_skills.build_user_prompt_context("Implement the plan.", data)
        self.assertIn("Sticky pairing mode is active", context)
        self.assertIn("do not edit files", context)

    def test_build_user_prompt_context_skips_exit_request(self) -> None:
        data = transcript(("assistant", "Pairing mode: active"))
        context = recover_session_skills.build_user_prompt_context("stop pairing", data)
        self.assertEqual(context, "")

    def test_build_user_prompt_context_handles_bail(self) -> None:
        data = transcript(("assistant", "Pairing mode: active"))
        context = recover_session_skills.build_user_prompt_context("bail and implement this chunk", data)
        self.assertIn("chunk-level bail", context)
        self.assertIn("emit `Pairing mode: active`", context)

    def test_build_clear_plan_context_reenters_pairing(self) -> None:
        plan = textwrap.dedent(
            """
            <proposed_plan>
            ## Implementation Handoff
            - Selected skills: $code:pair
            - TDD: not selected
            - TDD slices: none
            - Pairing: selected
            - Accepted plan path: ./.local/docs/code-plan/main/0001_PLAN.md
            </proposed_plan>
            """
        ).strip()
        context = recover_session_skills.build_clear_plan_context(plan)
        self.assertIn("Pairing: selected", context)
        self.assertIn("emit `Pairing mode: active`", context)


class DryRunScriptTests(unittest.TestCase):
    def run_hook(self, payload: dict[str, object], transcript_text: str) -> str:
        with tempfile.NamedTemporaryFile("w", delete=False) as handle:
            handle.write(transcript_text)
            transcript_path = handle.name
        try:
            payload = dict(payload)
            payload["transcript_path"] = transcript_path
            result = subprocess.run(
                [sys.executable, str(SCRIPTS_DIR / "recover_session_skills.py"), "--dry-run"],
                input=json.dumps(payload),
                text=True,
                capture_output=True,
                check=True,
            )
            return result.stdout.strip()
        finally:
            Path(transcript_path).unlink(missing_ok=True)

    def test_user_prompt_submit_injects_pairing_context(self) -> None:
        output = self.run_hook(
            {
                "hook_event_name": "UserPromptSubmit",
                "prompt": "Implement the plan.",
            },
            transcript(("assistant", "Pairing mode: active")),
        )
        self.assertIn("Sticky pairing mode is active", output)

    def test_user_prompt_submit_skips_after_exit(self) -> None:
        output = self.run_hook(
            {
                "hook_event_name": "UserPromptSubmit",
                "prompt": "Implement the plan.",
            },
            transcript(("assistant", "Pairing mode: exited")),
        )
        self.assertEqual(output, "")

    def test_user_prompt_submit_skips_explicit_pairing_exit_prompt(self) -> None:
        output = self.run_hook(
            {
                "hook_event_name": "UserPromptSubmit",
                "prompt": "exit pairing",
            },
            transcript(("assistant", "Pairing mode: active")),
        )
        self.assertEqual(output, "")


if __name__ == "__main__":
    unittest.main()
