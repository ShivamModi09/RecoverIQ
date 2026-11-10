"""
Unit tests for ReinsuranceCalculationEngine (Phase 2)
"""

import unittest
from src.calculator import ReinsuranceCalculator

class TestReinsuranceCalculator(unittest.TestCase):

    def setUp(self):
        self.cat_treaty = {
            "treaty_id": "TR-2025-PROP-01",
            "inception_date": "2025-01-01",
            "expiration_date": "2025-12-31",
            "retention_usd": 2000000.0,
            "limit_usd": 10000000.0,
            "covered_perils": ["Windstorm", "Hail", "Winter Storm"],
            "excluded_perils": ["Flood", "Cyber"]
        }
        self.per_risk_treaty = {
            "treaty_id": "TR-2025-PROP-02",
            "inception_date": "2025-01-01",
            "expiration_date": "2025-12-31",
            "retention_usd": 1000000.0,
            "limit_usd": 5000000.0,
            "covered_perils": ["Fire", "Lightning", "Explosion"],
            "excluded_perils": ["Terrorism", "Flood"]
        }

    def test_single_claim_under_retention(self):
        claim = {
            "claim_id": "CLM-001",
            "gross_loss_usd": 750000.0,
            "peril": "Fire",
            "loss_date": "2025-04-10"
        }
        res = ReinsuranceCalculator.calculate_single_claim(claim, self.per_risk_treaty)
        self.assertTrue(res.is_covered)
        self.assertEqual(res.recoverable_amount, 0.0)
        self.assertEqual(res.confidence_score, 1.0)

    def test_single_claim_above_retention(self):
        claim = {
            "claim_id": "CLM-002",
            "gross_loss_usd": 2500000.0,
            "peril": "Fire",
            "loss_date": "2025-05-15"
        }
        res = ReinsuranceCalculator.calculate_single_claim(claim, self.per_risk_treaty)
        self.assertTrue(res.is_covered)
        # 2,500,000 - 1,000,000 retention = 1,500,000 recoverable
        self.assertEqual(res.recoverable_amount, 1500000.0)
        self.assertGreaterEqual(res.confidence_score, 0.95)

    def test_catastrophe_event_aggregation_motivating_windstorm(self):
        # The 4 warehouses totaling $2.9M under CAT-2025-02
        claims = [
            {"claim_id": "CLM-01", "event_id": "CAT-02", "gross_loss_usd": 900000.0, "peril": "Windstorm", "loss_date": "2025-03-02"},
            {"claim_id": "CLM-02", "event_id": "CAT-02", "gross_loss_usd": 800000.0, "peril": "Windstorm", "loss_date": "2025-03-03"},
            {"claim_id": "CLM-03", "event_id": "CAT-02", "gross_loss_usd": 700000.0, "peril": "Windstorm", "loss_date": "2025-03-03"},
            {"claim_id": "CLM-04", "event_id": "CAT-02", "gross_loss_usd": 500000.0, "peril": "Windstorm", "loss_date": "2025-03-04"},
        ]
        res = ReinsuranceCalculator.calculate_catastrophe_event("CAT-02", claims, self.cat_treaty)
        self.assertTrue(res.is_covered)
        self.assertEqual(res.incurred_loss, 2900000.0)
        # Retention is $2.0M -> Recoverable = 2.9M - 2.0M = $900,000.0
        self.assertEqual(res.recoverable_amount, 900000.0)

    def test_excluded_peril_flood(self):
        claim = {
            "claim_id": "CLM-005",
            "gross_loss_usd": 3000000.0,
            "peril": "Flood",
            "loss_date": "2025-06-01"
        }
        res = ReinsuranceCalculator.calculate_single_claim(claim, self.cat_treaty)
        self.assertFalse(res.is_covered)
        self.assertEqual(res.recoverable_amount, 0.0)
        self.assertIn("excluded", res.ineligibility_reason.lower())

    def test_remaining_capacity_limit(self):
        # Loss excess is $2.0M, but remaining capacity is only $500,000
        claim = {
            "claim_id": "CLM-006",
            "gross_loss_usd": 3000000.0,
            "peril": "Fire",
            "loss_date": "2025-07-01"
        }
        res = ReinsuranceCalculator.calculate_single_claim(
            claim, self.per_risk_treaty, remaining_capacity=500000.0
        )
        self.assertTrue(res.is_covered)
        self.assertEqual(res.recoverable_amount, 500000.0)

if __name__ == "__main__":
    unittest.main()

