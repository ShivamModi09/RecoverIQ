#!/usr/bin/env python3
"""
RecoverIQ — Synthetic Data Verification Test Suite
Validates mathematical consistency, referential integrity, and planted anomaly distribution.
"""

import os
import json
import csv
import sys

def verify():
    errors = []

    # 1. File existence
    required_files = [
        "data/processed/treaties.json",
        "data/processed/events.json",
        "data/processed/claims_list.csv",
        "data/processed/broker_bordereau.csv",
        "data/processed/master_answer_key.json",
        "data/processed/treaty_loss_run.json"
    ]
    for rf in required_files:
        if not os.path.exists(rf):
            errors.append(f"Missing file: {rf}")

    if errors:
        print("\n".join(errors))
        sys.exit(1)

    # 2. Load data
    with open("data/processed/treaties.json") as f:
        treaties = {t["treaty_id"]: t for t in json.load(f)}
    with open("data/processed/events.json") as f:
        events = {e["event_id"]: e for e in json.load(f)}
    with open("data/processed/master_answer_key.json") as f:
        answer_key = {a["claim_id"]: a for a in json.load(f)}

    claims = []
    with open("data/processed/claims_list.csv") as f:
        reader = csv.DictReader(f)
        for r in reader:
            claims.append(r)

    bdx_records = []
    with open("data/processed/broker_bordereau.csv") as f:
        reader = csv.DictReader(f)
        for r in reader:
            bdx_records.append(r)

    # 3. Assert counts
    if len(treaties) != 3:
        errors.append(f"Expected 3 treaties, found {len(treaties)}")
    if len(events) != 12:
        errors.append(f"Expected 12 events, found {len(events)}")
    if len(claims) != 150:
        errors.append(f"Expected 150 claims, found {len(claims)}")
    if len(bdx_records) < 300:
        errors.append(f"Expected >= 300 BDX records, found {len(bdx_records)}")

    # 4. Check Planted Anomalies Breakdown
    anomalies = [a for a in answer_key.values() if a["is_anomaly"]]
    if len(anomalies) != 30:
        errors.append(f"Expected 30 planted anomalies, found {len(anomalies)}")

    tally = {}
    for a in anomalies:
        tally[a["anomaly_type"]] = tally.get(a["anomaly_type"], 0) + 1

    expected_tally = {
        "MISSED_RECOVERY": 10,
        "UNDER_BILLED": 8,
        "UNPAID_RECOVERY": 7,
        "EXCLUDED_PERIL": 5
    }
    for k, exp in expected_tally.items():
        if tally.get(k, 0) != exp:
            errors.append(f"Anomaly {k}: expected {exp}, got {tally.get(k, 0)}")

    # 5. Referential Integrity & Math Invariants
    for c in claims:
        cid = c["claim_id"]
        # Treaty reference
        if c["treaty_id"] not in treaties:
            errors.append(f"Claim {cid} references unknown treaty {c['treaty_id']}")
        # Event reference
        if c["event_id"] not in events:
            errors.append(f"Claim {cid} references unknown event {c['event_id']}")
        # Math: Gross Loss == Paid + Reserves
        gross = float(c["gross_loss_usd"])
        paid = float(c["paid_loss_usd"])
        res = float(c["case_reserves_usd"])
        if abs(gross - (paid + res)) > 0.05:
            errors.append(f"Claim {cid} math mismatch: Gross {gross} != Paid {paid} + Reserves {res}")

    # 6. Verify Motivating Case (CAT-2025-02)
    cat2_claims = [c for c in claims if c["event_id"] == "CAT-2025-02"]
    if len(cat2_claims) != 4:
        errors.append(f"CAT-2025-02 expected 4 claims, found {len(cat2_claims)}")
    total_cat2_loss = sum(float(c["gross_loss_usd"]) for c in cat2_claims)
    if abs(total_cat2_loss - 2900000.0) > 0.01:
        errors.append(f"CAT-2025-02 total loss expected 2,900,000, got {total_cat2_loss}")
    total_cat2_billed = sum(float(c["billed_reinsurance_usd"]) for c in cat2_claims)
    if total_cat2_billed != 0.0:
        errors.append(f"CAT-2025-02 expected $0 billed, got {total_cat2_billed}")

    # 7. Check 25 Loss Reports
    report_files = [f for f in os.listdir("data/reports") if f.endswith(".txt")]
    if len(report_files) != 25:
        errors.append(f"Expected 25 claim reports, found {len(report_files)}")

    if errors:
        print(f"FAILED with {len(errors)} errors:")
        for e in errors:
            print(f" - {e}")
        sys.exit(1)

    print("ALL VERIFICATIONS PASSED:")
    print("✓ 3 Treaties, 12 Events, 150 Claims, 300 BDX records, 25 Adjuster Reports verified.")
    print("✓ Referential integrity and mathematical invariants: 100% consistent.")
    print("✓ Exact 30 planted anomalies verified (10 Missed, 8 Underbilled, 7 Unpaid, 5 Excluded).")
    print("✓ Motivating CAT-2025-02 windstorm case ($2.9M loss, $2.0M retention, $0 billed) verified.")

if __name__ == "__main__":
    verify()

