from __future__ import annotations

import json
import threading
import unittest
import urllib.error
import urllib.request

from app.server import MAX_WORK_MS, clamp_work_ms, create_server


class PortalApplicationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.server = create_server(host="127.0.0.1", port=0)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base_url = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def get_json(self, path: str) -> tuple[int, dict[str, object]]:
        with urllib.request.urlopen(f"{self.base_url}{path}", timeout=2) as response:
            return response.status, json.loads(response.read())

    def test_root_returns_observable_contract(self) -> None:
        status, payload = self.get_json("/")
        self.assertEqual(status, 200)
        self.assertEqual(payload["service"], "ucab-enrollment-portal")
        self.assertEqual(payload["version"], "week-1")
        self.assertTrue(payload["instance"])
        self.assertTrue(payload["request_id"])

    def test_health_endpoint_is_small_and_stable(self) -> None:
        status, payload = self.get_json("/health")
        self.assertEqual(status, 200)
        self.assertEqual(payload, {"status": "healthy"})

    def test_work_endpoint_reports_clamped_delay(self) -> None:
        status, payload = self.get_json("/work?ms=5")
        self.assertEqual(status, 200)
        self.assertEqual(payload["work_ms"], 5)

    def test_unknown_endpoint_returns_404(self) -> None:
        with self.assertRaises(urllib.error.HTTPError) as raised:
            urllib.request.urlopen(f"{self.base_url}/missing", timeout=2)
        self.assertEqual(raised.exception.code, 404)

    def test_work_value_validation(self) -> None:
        self.assertEqual(clamp_work_ms(None), 0)
        self.assertEqual(clamp_work_ms("invalid"), 0)
        self.assertEqual(clamp_work_ms("-5"), 0)
        self.assertEqual(clamp_work_ms("999999"), MAX_WORK_MS)


if __name__ == "__main__":
    unittest.main()

