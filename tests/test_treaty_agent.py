"""
Unit tests for TreatyPolicyIntelligenceAgent (Agent A)
"""

import unittest
import os
from src.agents.treaty_agent import TreatyIntelligenceAgent

class TestTreatyIntelligenceAgent(unittest.TestCase):

    def setUp(self):
        self.agent = TreatyIntelligenceAgent()
        with open("data/raw/treaty_TR-2025-PROP-01.txt") as f:
            self.treaty_text = f.read()

    def test_treaty_extraction_structure(self):
        result = self.agent.analyze_treaty(self.treaty_text)
        self.assertIn("treaty_id", result)
        self.assertEqual(result["treaty_id"], "TR-2025-PROP-01")
        self.assertEqual(result["retention_usd"], 2000000.0)
        self.assertEqual(result["limit_usd"], 10000000.0)
        self.assertIn("Windstorm", result["covered_perils"])
        self.assertIn("Flood", result["excluded_perils"])
        self.assertIn("extracted_by", result)

if __name__ == "__main__":
    unittest.main()

