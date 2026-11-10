from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1]


class ScriptSafetyTests(unittest.TestCase):
    def test_all_shell_scripts_use_strict_mode(self) -> None:
        scripts = sorted((ROOT / "scripts").glob("*.sh"))
        self.assertTrue(scripts)
        for script in scripts:
            content = script.read_text(encoding="utf-8")
            self.assertIn("set -Eeuo pipefail", content, script.name)

    def test_random_identifier_is_64_bits_and_validated(self) -> None:
        deploy = (ROOT / "scripts" / "deploy-lab.sh").read_text(encoding="utf-8")
        common = (ROOT / "scripts" / "common.sh").read_text(encoding="utf-8")
        self.assertIn("secrets.token_hex(8)", deploy)
        self.assertIn("cloudformation create-stack", deploy)
        self.assertIn("Siguiente paso: ./scripts/status.sh", deploy)
        self.assertNotIn("Siguiente paso: ./scripts/verify-lab.sh", deploy)
        self.assertRegex(common, re.compile(r"ucab-lab-6-\[a-f0-9\]\{16\}"))

    def test_cleanup_uses_recorded_stack_and_output_bucket(self) -> None:
        cleanup = (ROOT / "scripts" / "cleanup-lab.sh").read_text(encoding="utf-8")
        self.assertIn("load_stack_name", cleanup)
        self.assertIn("stack_output AccessLogBucketName", cleanup)
        self.assertIn('--stack-name "$LAB_STACK"', cleanup)
        self.assertIn('stack_status" == "DELETE_FAILED', cleanup)
        self.assertIn("delete_retries", cleanup)
        self.assertNotIn("list-stacks", cleanup)


if __name__ == "__main__":
    unittest.main()
