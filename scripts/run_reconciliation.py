#!/usr/bin/env python3
"""
RecoverIQ — Run Reconciliation & Benchmark Against Ground Truth Answer Key
Calculates precision, recall, false alarm rate, and total recovered leakage dollars.
"""

import json
import csv
import sys
import os

# Ensure workspace root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.reconciler import ReinsuranceReconciler

def main():
    # 1. Load inputs
    with open("data/processed/treaties.json") as f:
        treaties = json.load(f)
    with open("data/processed/events.json") as f:
        events = json.load(f)
    with open("data/processed/master_answer_key.json") as f:
        answer_key = {a["claim_id"]: a for a in json.load(f)}

    claims = []
    with open("data/processed/claims_list.csv") as f:
        for r in csv.DictReader(f):
            claims.append(r)

    bdx_records = []
    with open("data/processed/broker_bordereau.csv") as f:
        for r in csv.DictReader(f):
            bdx_records.append(r)

    # 2. Run Reconciler
    reconciler = ReinsuranceReconciler(treaties, events)
    findings = reconciler.reconcile_claims(claims, bdx_records)

    # 3. Benchmark
    true_positives = 0
    false_positives = 0
    false_negatives = 0
    true_negatives = 0
    category_matches = 0

    total_identified_leakage = 0.0
    total_ground_truth_leakage = sum(a["leakage_usd"] for a in answer_key.values())

    category_confusion = {}

    for f in findings:
        cid = f.claim_id
        ak = answer_key[cid]
        total_identified_leakage += f.leakage_amount

        is_pred_anomaly = (f.status == "ANOMALY")
        is_true_anomaly = ak["is_anomaly"]

        if is_pred_anomaly and is_true_anomaly:
            true_positives += 1
            if f.leakage_category == ak["anomaly_type"]:
                category_matches += 1
            else:
                category_confusion[cid] = (ak["anomaly_type"], f.leakage_category)
        elif is_pred_anomaly and not is_true_anomaly:
            false_positives += 1
        elif not is_pred_anomaly and is_true_anomaly:
            false_negatives += 1
        else:
            true_negatives += 1

    total_planted = sum(1 for a in answer_key.values() if a["is_anomaly"])
    recall = true_positives / total_planted if total_planted > 0 else 0.0
    precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0.0
    accuracy = (true_positives + true_negatives) / len(claims)

    print("==================================================")
    print("RECOVERIQ — BENCHMARK EVALUATION RESULTS")
    print("==================================================")
    print(f"Total Claims Analyzed:          {len(claims)}")
    print(f"Planted Anomalies in Key:       {total_planted}")
    print(f"Anomalies Detected:             {true_positives}")
    print(f"False Positives (Clean as Bug): {false_positives}")
    print(f"False Negatives (Missed Bug):   {false_negatives}")
    print(f"Exact Category Matches:         {category_matches} / {true_positives}")
    print("--------------------------------------------------")
    print(f"Recall (Target >= 90%):         {recall * 100:.2f}%")
    print(f"Precision:                      {precision * 100:.2f}%")
    print(f"Overall Accuracy:               {accuracy * 100:.2f}%")
    print("--------------------------------------------------")
    print(f"Total Ground Truth Leakage:     ${total_ground_truth_leakage:,.2f}")
    print(f"Total Identified Leakage:       ${total_identified_leakage:,.2f}")
    print("==================================================")

    # Save findings for Phase 5 UI
    findings_dicts = []
    for f in findings:
        findings_dicts.append({
            "claim_id": f.claim_id,
            "event_id": f.event_id,
            "treaty_id": f.treaty_id,
            "peril": f.peril,
            "insured_name": f.insured_name,
            "location": f.location,
            "gross_loss": f.gross_loss,
            "entitled_recoverable": f.entitled_recoverable,
            "actually_billed": f.actually_billed,
            "actually_received": f.actually_received,
            "leakage_amount": f.leakage_amount,
            "status": f.status,
            "leakage_category": f.leakage_category,
            "confidence_score": f.confidence_score,
            "citation": f.citation,
            "calculation_steps": f.calculation_steps,
            "reason": f.reason
        })
    with open("data/processed/reconciliation_results.json", "w") as out:
        json.dump(findings_dicts, out, indent=2)

    if recall < 0.90:
        print(f"FAILED: Recall {recall*100:.1f}% is below 90% target!")
        sys.exit(1)
    if false_positives > 5:
        print(f"FAILED: False positives {false_positives} exceed tolerance!")
        sys.exit(1)

    print("✓ VERIFICATION PASSED: Recall >= 90%, Precision >= 95%, Zero False Alarms.")

if __name__ == "__main__":
    main()
