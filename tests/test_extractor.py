"""
Unit tests for DocumentExtractor (Phase 3)
"""

import unittest
import os
from src.extractor import DocumentExtractor

class TestDocumentExtractor(unittest.TestCase):

    def test_extract_treaty_raw_file(self):
        doc_path = "data/raw/treaty_TR-2025-PROP-01.txt"
        self.assertTrue(os.path.exists(doc_path))
        with open(doc_path) as f:
            text = f.read()

        extracted = DocumentExtractor.extract_treaty(text)
        self.assertEqual(extracted["treaty_id"], "TR-2025-PROP-01")
        self.assertEqual(extracted["retention_usd"], 2000000.0)
        self.assertEqual(extracted["limit_usd"], 10000000.0)
        self.assertEqual(extracted["citation_page_retention"], 4)
        self.assertIn("Windstorm", extracted["covered_perils"])
        self.assertIn("Flood", extracted["excluded_perils"])
        self.assertEqual(extracted["citation_page_perils"], 7)
        self.assertEqual(extracted["hours_clause"], 72)
        self.assertEqual(extracted["citation_page_hours"], 9)

    def test_extract_claim_report(self):
        rep_path = "data/reports/REP-CLM-2025-001.txt"
        self.assertTrue(os.path.exists(rep_path))
        with open(rep_path) as f:
            text = f.read()

        extracted = DocumentExtractor.extract_claim_report(text)
        self.assertEqual(extracted["report_id"], "REP-CLM-2025-001")
        self.assertEqual(extracted["claim_id"], "CLM-2025-001")
        self.assertEqual(extracted["gross_loss_usd"], 900000.0)
        self.assertEqual(extracted["paid_loss_usd"], 810000.0)
        self.assertEqual(extracted["case_reserves_usd"], 90000.0)
        self.assertEqual(extracted["citation_page_quantification"], 2)

if __name__ == "__main__":
    unittest.main()

