from __future__ import annotations

import importlib.util
import contextlib
import io
import sys
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).parents[1] / "scripts" / "load_test.py"
SPEC = importlib.util.spec_from_file_location("load_test", MODULE_PATH)
assert SPEC and SPEC.loader
load_test = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = load_test
SPEC.loader.exec_module(load_test)


class LoadTestUnitTests(unittest.TestCase):
    def test_percentile_interpolates_and_handles_empty_input(self) -> None:
        self.assertEqual(load_test.percentile([], 95), 0.0)
        self.assertEqual(load_test.percentile([10], 95), 10)
        self.assertEqual(load_test.percentile([10, 20, 30, 40], 50), 25)

    def test_summary_counts_success_errors_and_instances(self) -> None:
        samples = [
            load_test.Sample(10, 200, "host-b"),
            load_test.Sample(20, 200, "host-a"),
            load_test.Sample(30, 503, None),
        ]
        result = load_test.summarize(samples, 2)
        self.assertEqual(result["requests"], 3)
        self.assertEqual(result["successful"], 2)
        self.assertEqual(result["errors"], 1)
        self.assertEqual(result["success_rate_pct"], 66.67)
        self.assertEqual(result["throughput_rps"], 1.5)
        self.assertEqual(result["instances_observed"], ["host-a", "host-b"])

    def test_cli_limits_reject_excessive_values(self) -> None:
        parser = load_test.build_parser()
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                parser.parse_args(["--url", "http://example", "--duration", "181"])
            with self.assertRaises(SystemExit):
                parser.parse_args(["--url", "http://example", "--concurrency", "51"])


if __name__ == "__main__":
    unittest.main()
