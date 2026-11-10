"""
Unit tests for RecoverIQ Backend Server (Phase 5 + Agent A/B Endpoints)
"""

import unittest
import json
import io
from unittest.mock import MagicMock
from server import RecoverIQHandler

class TestRecoverIQServer(unittest.TestCase):

    def setUp(self):
        self.handler = RecoverIQHandler.__new__(RecoverIQHandler)
        self.handler.send_response = MagicMock()
        self.handler.send_header = MagicMock()
        self.handler.end_headers = MagicMock()
        self.handler.wfile = MagicMock()
        self.handler.rfile = io.BytesIO()
        self.handler.headers = {}

    def test_get_root_serves_html(self):
        self.handler.path = "/"
        self.handler.do_GET()
        self.handler.send_response.assert_called_with(200)
        self.handler.send_header.assert_called_with("Content-type", "text/html; charset=utf-8")
        self.assertTrue(self.handler.wfile.write.called)

    def test_get_api_findings(self):
        self.handler.path = "/api/findings"
        self.handler.do_GET()
        self.handler.send_response.assert_called_with(200)
        written_bytes = self.handler.wfile.write.call_args[0][0]
        data = json.loads(written_bytes.decode("utf-8"))
        self.assertEqual(len(data), 150)
        anomalies = [d for d in data if d["status"] == "ANOMALY"]
        self.assertEqual(len(anomalies), 30)

    def test_post_extract_treaty_agent(self):
        payload = json.dumps({"treaty_id": "TR-2025-PROP-01"}).encode("utf-8")
        self.handler.path = "/api/agent/extract-treaty"
        self.handler.headers = {"Content-Length": str(len(payload))}
        self.handler.rfile = io.BytesIO(payload)

        self.handler.do_POST()
        self.handler.send_response.assert_called_with(200)
        written_bytes = self.handler.wfile.write.call_args[0][0]
        res = json.loads(written_bytes.decode("utf-8"))
        self.assertEqual(res["treaty_id"], "TR-2025-PROP-01")
        self.assertEqual(res["retention_usd"], 2000000.0)

    def test_post_generate_notice_agent(self):
        payload = json.dumps({"claim_id": "CLM-2025-001"}).encode("utf-8")
        self.handler.path = "/api/agent/generate-notice"
        self.handler.headers = {"Content-Length": str(len(payload))}
        self.handler.rfile = io.BytesIO(payload)

        self.handler.do_POST()
        self.handler.send_response.assert_called_with(200)
        written_bytes = self.handler.wfile.write.call_args[0][0]
        res = json.loads(written_bytes.decode("utf-8"))
        self.assertEqual(res["subject_claim_id"], "CLM-2025-001")
        self.assertIn("formal_recovery_demand", res)

if __name__ == "__main__":
    unittest.main()
