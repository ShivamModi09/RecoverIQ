"""
Unit tests for ReconciliationExplainerAgent (Agent B)
"""

import unittest
from src.agents.explainer_agent import ReconciliationExplainerAgent

class TestReconciliationExplainerAgent(unittest.TestCase):

    def setUp(self):
        self.agent = ReconciliationExplainerAgent()
        self.sample_finding = {
            "claim_id": "CLM-2025-001",
            "insured_name": "Apex Logistics Hub 1",
            "location": "Dallas, TX",
            "event_id": "CAT-2025-02",
            "peril": "Windstorm",
            "treaty_id": "TR-2025-PROP-01",
            "gross_loss": 900000.0,
            "entitled_recoverable": 279310.34,
            "actually_billed": 0.0,
            "actually_received": 0.0,
            "leakage_amount": 279310.34,
            "leakage_category": "MISSED_RECOVERY",
            "citation": {"retention_page": 4, "limit_page": 4, "perils_page": 7},
            "calculation_steps": [
                "CAT-2025-02 storm total ($2.9M) breached $2.0M retention.",
                "Event recovery of $900k allocated proportionally.",
                "Entitled recoverable = $279,310.34. Billed = $0.00."
            ]
        }

    def test_generate_audit_brief_structure(self):
        brief = self.agent.generate_audit_brief(self.sample_finding)
        self.assertIn("subject_claim_id", brief)
        self.assertEqual(brief["subject_claim_id"], "CLM-2025-001")
        self.assertIn("formal_recovery_demand", brief)
        self.assertIn("contract_legal_basis", brief)
        self.assertIn("calculation_audit_trail", brief)

if __name__ == "__main__":
    unittest.main()

