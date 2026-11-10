#!/usr/bin/env python3
"""
RecoverIQ — Synthetic Data Generation Engine (Refined)
Generates 100% mathematically and structurally consistent reinsurance datasets:
- 3 Treaties
- 12 Catastrophe Events
- 150 Claims (CSV)
- 25 Claim Loss Adjuster Reports
- Broker Bordereau (BDX) statement (~300 records)
- Treaty Loss Run ledger
- Master Answer Key (exactly 30 planted anomalies)
"""

import os
import json
import csv
import random
from datetime import datetime, timedelta

random.seed(42)

OUT_RAW = "data/raw"
OUT_PROC = "data/processed"
OUT_REP = "data/reports"

os.makedirs(OUT_RAW, exist_ok=True)
os.makedirs(OUT_PROC, exist_ok=True)
os.makedirs(OUT_REP, exist_ok=True)

# -------------------------------------------------------------
# 1. TREATIES
# -------------------------------------------------------------
TREATIES = [
    {
        "treaty_id": "TR-2025-PROP-01",
        "treaty_name": "Commercial Property Catastrophe Excess of Loss Treaty",
        "type": "Per Occurrence Excess of Loss (CAT XOL)",
        "reinsurer": "Munich Re Syndicate",
        "broker": "Aon Reinsurance Solutions",
        "inception_date": "2025-01-01",
        "expiration_date": "2025-12-31",
        "retention_usd": 2000000.0,  # $2.0M
        "limit_usd": 10000000.0,     # $10.0M
        "covered_perils": ["Windstorm", "Tornado", "Hail", "Winter Storm", "Freezing", "Wildfire"],
        "excluded_perils": ["Flood", "Earthquake", "Cyber", "War", "Nuclear"],
        "hours_clause": 72,
        "citation_page_retention": 4,
        "citation_page_limit": 4,
        "citation_page_perils": 7,
        "citation_page_hours": 9,
    },
    {
        "treaty_id": "TR-2025-PROP-02",
        "treaty_name": "Commercial Property Per Risk Excess of Loss Treaty",
        "type": "Per Risk Excess of Loss",
        "reinsurer": "Swiss Re Corporate Solutions",
        "broker": "Guy Carpenter",
        "inception_date": "2025-01-01",
        "expiration_date": "2025-12-31",
        "retention_usd": 1000000.0,  # $1.0M
        "limit_usd": 5000000.0,      # $5.0M
        "covered_perils": ["Fire", "Lightning", "Explosion"],
        "excluded_perils": ["Flood", "Earthquake", "Terrorism"],
        "hours_clause": 24,
        "citation_page_retention": 3,
        "citation_page_limit": 3,
        "citation_page_perils": 5,
        "citation_page_hours": 6,
    },
    {
        "treaty_id": "TR-2025-PROP-03",
        "treaty_name": "Commercial Property Aggregate Stop Loss Treaty",
        "type": "Annual Aggregate Stop Loss",
        "reinsurer": "Hannover Re",
        "broker": "Gallagher Re",
        "inception_date": "2025-01-01",
        "expiration_date": "2025-12-31",
        "retention_usd": 15000000.0, # $15.0M aggregate
        "limit_usd": 20000000.0,     # $20.0M aggregate
        "covered_perils": ["Windstorm", "Fire", "Winter Storm", "Explosion", "Wildfire"],
        "excluded_perils": ["Flood", "Earthquake", "Cyber"],
        "hours_clause": 168,
        "citation_page_retention": 5,
        "citation_page_limit": 5,
        "citation_page_perils": 8,
        "citation_page_hours": 11,
    }
]

with open(os.path.join(OUT_PROC, "treaties.json"), "w") as f:
    json.dump(TREATIES, f, indent=2)

for t in TREATIES:
    doc_path = os.path.join(OUT_RAW, f"treaty_{t['treaty_id']}.txt")
    with open(doc_path, "w") as f:
        f.write(f"=== [PAGE 1] ===\n")
        f.write(f"REINSURANCE TREATY AGREEMENT: {t['treaty_id']}\n")
        f.write(f"Contract: {t['treaty_name']}\n")
        f.write(f"Type: {t['type']}\n")
        f.write(f"Reinsurer: {t['reinsurer']} | Intermediary Broker: {t['broker']}\n")
        f.write(f"Effective Period: {t['inception_date']} 00:01 Local Time to {t['expiration_date']} 24:00 Local Time\n\n")
        f.write(f"=== [PAGE {t['citation_page_retention']}] ===\n")
        f.write(f"ARTICLE IV — RETENTION AND LIMIT\n")
        f.write(f"The Company (Insurer) shall retain as its initial net loss retention the sum of USD ${t['retention_usd']:,.2f} per event/risk.\n")
        f.write(f"The Reinsurer shall be liable in respect of each loss occurrence for the excess of the Company's net retention up to a maximum limit of liability of USD ${t['limit_usd']:,.2f}.\n\n")
        f.write(f"=== [PAGE {t['citation_page_perils']}] ===\n")
        f.write(f"ARTICLE VIII — COVERED PERILS AND EXCLUSIONS\n")
        f.write(f"Covered Perils: {', '.join(t['covered_perils'])}\n")
        f.write(f"Explicit Exclusions: {', '.join(t['excluded_perils'])}\n\n")
        f.write(f"=== [PAGE {t['citation_page_hours']}] ===\n")
        f.write(f"ARTICLE XI — LOSS OCCURRENCE DEFINITION (HOURS CLAUSE)\n")
        f.write(f"All individual property claims arising out of one atmospheric or catastrophe event within a consecutive {t['hours_clause']}-hour period shall be deemed one single Loss Occurrence for retention and limit aggregation.\n")

# -------------------------------------------------------------
# 2. CATASTROPHE EVENTS
# -------------------------------------------------------------
EVENTS = [
    {"event_id": "CAT-2025-01", "name": "Winter Storm Grayson", "peril": "Winter Storm", "start_date": "2025-01-14", "end_date": "2025-01-17", "treaty_id": "TR-2025-PROP-01"},
    {"event_id": "CAT-2025-02", "name": "Windstorm Vance (Motivating Case)", "peril": "Windstorm", "start_date": "2025-03-02", "end_date": "2025-03-04", "treaty_id": "TR-2025-PROP-01"},
    {"event_id": "CAT-2025-03", "name": "Tornado Outbreak Central", "peril": "Tornado", "start_date": "2025-04-10", "end_date": "2025-04-12", "treaty_id": "TR-2025-PROP-01"},
    {"event_id": "CAT-2025-04", "name": "Midwest Hail Supercell", "peril": "Hail", "start_date": "2025-05-18", "end_date": "2025-05-19", "treaty_id": "TR-2025-PROP-01"},
    {"event_id": "CAT-2025-05", "name": "Chemical Plant Fire Cluster", "peril": "Fire", "start_date": "2025-06-05", "end_date": "2025-06-06", "treaty_id": "TR-2025-PROP-02"},
    {"event_id": "CAT-2025-06", "name": "Wildfire Diablo Surge", "peril": "Wildfire", "start_date": "2025-07-22", "end_date": "2025-07-25", "treaty_id": "TR-2025-PROP-01"},
    {"event_id": "CAT-2025-07", "name": "Hurricane Helene Peripheral Wind", "peril": "Windstorm", "start_date": "2025-08-11", "end_date": "2025-08-14", "treaty_id": "TR-2025-PROP-01"},
    {"event_id": "CAT-2025-08", "name": "Industrial Complex Explosion", "peril": "Explosion", "start_date": "2025-09-02", "end_date": "2025-09-03", "treaty_id": "TR-2025-PROP-02"},
    {"event_id": "CAT-2025-09", "name": "Derecho Windstorm West", "peril": "Windstorm", "start_date": "2025-10-04", "end_date": "2025-10-06", "treaty_id": "TR-2025-PROP-01"},
    {"event_id": "CAT-2025-10", "name": "Great Lakes Early Freeze", "peril": "Freezing", "start_date": "2025-11-15", "end_date": "2025-11-17", "treaty_id": "TR-2025-PROP-01"},
    {"event_id": "CAT-2025-11", "name": "Ohio River Flood Inundation (Excluded)", "peril": "Flood", "start_date": "2025-05-28", "end_date": "2025-05-30", "treaty_id": "TR-2025-PROP-01"},
    {"event_id": "CAT-2025-12", "name": "Severe Hail Storm South", "peril": "Hail", "start_date": "2025-12-01", "end_date": "2025-12-02", "treaty_id": "TR-2025-PROP-01"}
]

with open(os.path.join(OUT_PROC, "events.json"), "w") as f:
    json.dump(EVENTS, f, indent=2)

# -------------------------------------------------------------
# 3. CLAIMS GENERATION
# -------------------------------------------------------------
PROPERTIES = [
    "Apex Logistics Hub", "Summit Distribution Center", "Vanguard Cold Storage",
    "Omni Logistics Center", "Starlight Manufacturing", "Pinnacle Data Center", 
    "Metro Cold Storage", "Pacific Rim Warehouse", "Keystone Processing Facility",
    "Great Lakes Grain Elevator", "Sonora Solar Substation", "Crestview Assembly Plant",
    "Bayside Marina Warehouse", "Highland Medical Supplies", "Midwest Chemical Depot"
]

CITIES = [
    "Dallas, TX", "Plano, TX", "Fort Worth, TX", "Chicago, IL", "Houston, TX",
    "Denver, CO", "Phoenix, AZ", "Atlanta, GA", "Columbus, OH", "Indianapolis, IN"
]

CLAIMS = []
ANSWER_KEY = []
claim_idx = 1

# A. Motivating Case CAT-2025-02: 4 claims totaling $2.9M, retention $2.0M, owed $900k, billed $0
motivating_claims = [
    {"property": "Apex Logistics Hub 1, Dallas TX", "loss": 900000.0, "date": "2025-03-02"},
    {"property": "Apex Logistics Hub 2, Dallas TX", "loss": 800000.0, "date": "2025-03-03"},
    {"property": "Summit Distribution Ctr, Plano TX", "loss": 700000.0, "date": "2025-03-03"},
    {"property": "Vanguard Cold Storage, Fort Worth TX", "loss": 500000.0, "date": "2025-03-04"},
]

for mc in motivating_claims:
    cid = f"CLM-2025-{claim_idx:03d}"
    entitled_alloc = round(900000.0 * (mc["loss"] / 2900000.0), 2)
    c = {
        "claim_id": cid,
        "policy_number": f"POL-CP-{2025000 + claim_idx}",
        "insured_name": mc["property"].split(",")[0],
        "location": mc["property"],
        "loss_date": mc["date"],
        "peril": "Windstorm",
        "event_id": "CAT-2025-02",
        "treaty_id": "TR-2025-PROP-01",
        "gross_loss_usd": mc["loss"],
        "paid_loss_usd": round(mc["loss"] * 0.9, 2),
        "case_reserves_usd": round(mc["loss"] * 0.1, 2),
        "status": "Closed",
        "billed_reinsurance_usd": 0.0,
        "received_reinsurance_usd": 0.0,
        "report_id": f"REP-{cid}"
    }
    CLAIMS.append(c)
    ANSWER_KEY.append({
        "claim_id": cid,
        "event_id": "CAT-2025-02",
        "treaty_id": "TR-2025-PROP-01",
        "is_anomaly": True,
        "anomaly_type": "MISSED_RECOVERY",
        "expected_recoverable_usd": entitled_alloc,
        "actual_billed_usd": 0.0,
        "actual_received_usd": 0.0,
        "leakage_usd": entitled_alloc,
        "confidence_score": 0.98,
        "reason": "CAT-2025-02 storm total ($2.9M) breached $2.0M retention. Event recovery of $900k was never billed because individual claims were below retention."
    })
    claim_idx += 1

# B. 6 Additional Single Claim Missed Recoveries (Per Risk TR-2025-PROP-02)
# Large individual fires above $1.0M retention where analyst completely missed billing
for _ in range(6):
    cid = f"CLM-2025-{claim_idx:03d}"
    prop = random.choice(PROPERTIES) + f" #{random.randint(10, 99)}"
    loc = random.choice(CITIES)
    gross_loss = round(1000000.0 + random.uniform(300000, 1500000), 2)
    recoverable = round(gross_loss - 1000000.0, 2)
    paid = round(gross_loss * 0.85, 2)
    res = round(gross_loss - paid, 2)
    c = {
        "claim_id": cid, "policy_number": f"POL-CP-{2025000 + claim_idx}",
        "insured_name": prop, "location": f"{prop}, {loc}", "loss_date": "2025-06-15",
        "peril": "Fire", "event_id": "CAT-2025-05", "treaty_id": "TR-2025-PROP-02",
        "gross_loss_usd": gross_loss, "paid_loss_usd": paid, "case_reserves_usd": res,
        "status": "Closed", "billed_reinsurance_usd": 0.0, "received_reinsurance_usd": 0.0,
        "report_id": f"REP-{cid}"
    }
    CLAIMS.append(c)
    ANSWER_KEY.append({
        "claim_id": cid, "event_id": "CAT-2025-05", "treaty_id": "TR-2025-PROP-02",
        "is_anomaly": True, "anomaly_type": "MISSED_RECOVERY",
        "expected_recoverable_usd": recoverable, "actual_billed_usd": 0.0,
        "actual_received_usd": 0.0, "leakage_usd": recoverable,
        "confidence_score": 0.98,
        "reason": f"Single fire loss ${gross_loss:,.2f} exceeded $1.0M retention. Recoverable ${recoverable:,.2f} was never billed."
    })
    claim_idx += 1

# C. 8 Under-Billed Anomalies (Billed against early paid loss instead of total incurred)
for _ in range(8):
    cid = f"CLM-2025-{claim_idx:03d}"
    prop = random.choice(PROPERTIES) + f" #{random.randint(10, 99)}"
    loc = random.choice(CITIES)
    gross_loss = round(1000000.0 + random.uniform(500000, 2000000), 2)
    recoverable = round(gross_loss - 1000000.0, 2)
    paid = round(gross_loss * 0.6, 2)
    res = round(gross_loss - paid, 2)
    billed = round(max(50000.0, recoverable * 0.55), 2)
    received = billed
    leakage = round(recoverable - billed, 2)
    c = {
        "claim_id": cid, "policy_number": f"POL-CP-{2025000 + claim_idx}",
        "insured_name": prop, "location": f"{prop}, {loc}", "loss_date": "2025-08-18",
        "peril": "Explosion", "event_id": "CAT-2025-08", "treaty_id": "TR-2025-PROP-02",
        "gross_loss_usd": gross_loss, "paid_loss_usd": paid, "case_reserves_usd": res,
        "status": "Open", "billed_reinsurance_usd": billed, "received_reinsurance_usd": received,
        "report_id": f"REP-{cid}"
    }
    CLAIMS.append(c)
    ANSWER_KEY.append({
        "claim_id": cid, "event_id": "CAT-2025-08", "treaty_id": "TR-2025-PROP-02",
        "is_anomaly": True, "anomaly_type": "UNDER_BILLED",
        "expected_recoverable_usd": recoverable, "actual_billed_usd": billed,
        "actual_received_usd": received, "leakage_usd": leakage,
        "confidence_score": 0.96,
        "reason": f"Incurred loss grew to ${gross_loss:,.2f}. Billed ${billed:,.2f} instead of ${recoverable:,.2f}. Under-billed by ${leakage:,.2f}."
    })
    claim_idx += 1

# D. 7 Unpaid / Short-Paid Anomalies (Billed correctly, broker remittance missing)
for _ in range(7):
    cid = f"CLM-2025-{claim_idx:03d}"
    prop = random.choice(PROPERTIES) + f" #{random.randint(10, 99)}"
    loc = random.choice(CITIES)
    gross_loss = round(1000000.0 + random.uniform(400000, 1800000), 2)
    recoverable = round(gross_loss - 1000000.0, 2)
    billed = recoverable
    received = round(billed * random.choice([0.0, 0.4]), 2)
    leakage = round(billed - received, 2)
    c = {
        "claim_id": cid, "policy_number": f"POL-CP-{2025000 + claim_idx}",
        "insured_name": prop, "location": f"{prop}, {loc}", "loss_date": "2025-06-20",
        "peril": "Fire", "event_id": "CAT-2025-05", "treaty_id": "TR-2025-PROP-02",
        "gross_loss_usd": gross_loss, "paid_loss_usd": round(gross_loss * 0.9, 2),
        "case_reserves_usd": round(gross_loss * 0.1, 2), "status": "Closed",
        "billed_reinsurance_usd": billed, "received_reinsurance_usd": received,
        "report_id": f"REP-{cid}"
    }
    CLAIMS.append(c)
    ANSWER_KEY.append({
        "claim_id": cid, "event_id": "CAT-2025-05", "treaty_id": "TR-2025-PROP-02",
        "is_anomaly": True, "anomaly_type": "UNPAID_RECOVERY",
        "expected_recoverable_usd": recoverable, "actual_billed_usd": billed,
        "actual_received_usd": received, "leakage_usd": leakage,
        "confidence_score": 0.95,
        "reason": f"Billed correctly for ${billed:,.2f}, but received only ${received:,.2f}. Unpaid leakage of ${leakage:,.2f} aged > 90 days."
    })
    claim_idx += 1

# E. 5 Excluded Peril Anomalies (Billed for Flood under TR-2025-PROP-01)
for _ in range(5):
    cid = f"CLM-2025-{claim_idx:03d}"
    prop = random.choice(PROPERTIES) + f" #{random.randint(10, 99)}"
    loc = random.choice(CITIES)
    gross_loss = round(2000000.0 + random.uniform(300000, 1200000), 2)
    billed = round(gross_loss - 2000000.0, 2)
    c = {
        "claim_id": cid, "policy_number": f"POL-CP-{2025000 + claim_idx}",
        "insured_name": prop, "location": f"{prop}, {loc}", "loss_date": "2025-05-29",
        "peril": "Flood", "event_id": "CAT-2025-11", "treaty_id": "TR-2025-PROP-01",
        "gross_loss_usd": gross_loss, "paid_loss_usd": gross_loss,
        "case_reserves_usd": 0.0, "status": "Closed",
        "billed_reinsurance_usd": billed, "received_reinsurance_usd": 0.0,
        "report_id": f"REP-{cid}"
    }
    CLAIMS.append(c)
    ANSWER_KEY.append({
        "claim_id": cid, "event_id": "CAT-2025-11", "treaty_id": "TR-2025-PROP-01",
        "is_anomaly": True, "anomaly_type": "EXCLUDED_PERIL",
        "expected_recoverable_usd": 0.0, "actual_billed_usd": billed,
        "actual_received_usd": 0.0, "leakage_usd": 0.0,
        "confidence_score": 0.98,
        "reason": f"Peril 'Flood' is explicitly excluded in Article VIII of TR-2025-PROP-01. Billed ${billed:,.2f} in error."
    })
    claim_idx += 1

# F. Clean Claims (Remaining 120 claims)
# 1. 60 Clean Per-Risk claims on TR-2025-PROP-02
#    - 30 above retention ($1.0M): correctly billed & paid
#    - 30 below retention: $0 billed & $0 received
for i in range(60):
    cid = f"CLM-2025-{claim_idx:03d}"
    prop = random.choice(PROPERTIES) + f" #{random.randint(10, 99)}"
    loc = random.choice(CITIES)
    if i < 30:
        gross_loss = round(1000000.0 + random.uniform(100000, 1500000), 2)
        recoverable = round(gross_loss - 1000000.0, 2)
        billed = recoverable
        received = recoverable
    else:
        gross_loss = round(random.uniform(50000, 920000), 2)
        recoverable = 0.0
        billed = 0.0
        received = 0.0

    paid = round(gross_loss * 0.8, 2)
    res = round(gross_loss - paid, 2)
    c = {
        "claim_id": cid, "policy_number": f"POL-CP-{2025000 + claim_idx}",
        "insured_name": prop, "location": f"{prop}, {loc}", "loss_date": "2025-07-10",
        "peril": "Fire", "event_id": "CAT-2025-05", "treaty_id": "TR-2025-PROP-02",
        "gross_loss_usd": gross_loss, "paid_loss_usd": paid, "case_reserves_usd": res,
        "status": "Closed" if res == 0 else "Open",
        "billed_reinsurance_usd": billed, "received_reinsurance_usd": received,
        "report_id": f"REP-{cid}" if len(CLAIMS) < 25 else ""
    }
    CLAIMS.append(c)
    ANSWER_KEY.append({
        "claim_id": cid, "event_id": "CAT-2025-05", "treaty_id": "TR-2025-PROP-02",
        "is_anomaly": False, "anomaly_type": "NONE",
        "expected_recoverable_usd": recoverable, "actual_billed_usd": billed,
        "actual_received_usd": received, "leakage_usd": 0.0,
        "confidence_score": 1.0,
        "reason": "Calculations and reconciliations are 100% matched."
    })
    claim_idx += 1

# 2. 60 Clean CAT Weather claims on TR-2025-PROP-01 across other events
# Grouped cleanly so event totals are either correctly billed or correctly under retention
other_cat_events = [e for e in EVENTS if e["event_id"] not in ["CAT-2025-02", "CAT-2025-05", "CAT-2025-08", "CAT-2025-11"]]
for i in range(60):
    cid = f"CLM-2025-{claim_idx:03d}"
    ev = other_cat_events[i % len(other_cat_events)]
    prop = random.choice(PROPERTIES) + f" #{random.randint(10, 99)}"
    loc = random.choice(CITIES)
    gross_loss = round(random.uniform(50000, 350000), 2)  # Minor weather claims below retention
    paid = round(gross_loss * 0.9, 2)
    res = round(gross_loss - paid, 2)

    c = {
        "claim_id": cid, "policy_number": f"POL-CP-{2025000 + claim_idx}",
        "insured_name": prop, "location": f"{prop}, {loc}", "loss_date": ev["start_date"],
        "peril": ev["peril"], "event_id": ev["event_id"], "treaty_id": "TR-2025-PROP-01",
        "gross_loss_usd": gross_loss, "paid_loss_usd": paid, "case_reserves_usd": res,
        "status": "Closed", "billed_reinsurance_usd": 0.0, "received_reinsurance_usd": 0.0,
        "report_id": ""
    }
    CLAIMS.append(c)
    ANSWER_KEY.append({
        "claim_id": cid, "event_id": ev["event_id"], "treaty_id": "TR-2025-PROP-01",
        "is_anomaly": False, "anomaly_type": "NONE",
        "expected_recoverable_usd": 0.0, "actual_billed_usd": 0.0,
        "actual_received_usd": 0.0, "leakage_usd": 0.0,
        "confidence_score": 1.0,
        "reason": "Event loss below retention; correctly billed $0.00."
    })
    claim_idx += 1

# -------------------------------------------------------------
# 4. BROKER BORDEREAU (BDX) RECORDS (~300 rows)
# -------------------------------------------------------------
BDX_RECORDS = []
bdx_id = 1
for c in CLAIMS:
    if c["billed_reinsurance_usd"] > 0:
        b_row = {
            "bdx_record_id": f"BDX-2025-{bdx_id:04d}",
            "claim_id": c["claim_id"],
            "policy_number": c["policy_number"],
            "treaty_id": c["treaty_id"],
            "broker": "Aon Reinsurance Solutions" if c["treaty_id"] == "TR-2025-PROP-01" else "Guy Carpenter",
            "transaction_date": (datetime.strptime(c["loss_date"], "%Y-%m-%d") + timedelta(days=20)).strftime("%Y-%m-%d"),
            "transaction_type": "Ceded Billing Notice",
            "gross_loss_reported": c["gross_loss_usd"],
            "billed_amount_usd": c["billed_reinsurance_usd"],
            "remitted_amount_usd": 0.0,
            "settlement_status": "Pending Remittance",
            "aging_days": 115 if c["billed_reinsurance_usd"] > c["received_reinsurance_usd"] else 30
        }
        BDX_RECORDS.append(b_row)
        bdx_id += 1

    if c["received_reinsurance_usd"] > 0:
        r_row = {
            "bdx_record_id": f"BDX-2025-{bdx_id:04d}",
            "claim_id": c["claim_id"],
            "policy_number": c["policy_number"],
            "treaty_id": c["treaty_id"],
            "broker": "Aon Reinsurance Solutions" if c["treaty_id"] == "TR-2025-PROP-01" else "Guy Carpenter",
            "transaction_date": (datetime.strptime(c["loss_date"], "%Y-%m-%d") + timedelta(days=50)).strftime("%Y-%m-%d"),
            "transaction_type": "Cash Remittance",
            "gross_loss_reported": c["gross_loss_usd"],
            "billed_amount_usd": 0.0,
            "remitted_amount_usd": c["received_reinsurance_usd"],
            "settlement_status": "Settled",
            "aging_days": 0
        }
        BDX_RECORDS.append(r_row)
        bdx_id += 1

while len(BDX_RECORDS) < 300:
    sample_c = random.choice(CLAIMS)
    p_row = {
        "bdx_record_id": f"BDX-2025-{bdx_id:04d}",
        "claim_id": sample_c["claim_id"],
        "policy_number": sample_c["policy_number"],
        "treaty_id": sample_c["treaty_id"],
        "broker": "Aon Reinsurance Solutions",
        "transaction_date": "2025-06-30",
        "transaction_type": "Quarterly Statement Certified",
        "gross_loss_reported": sample_c["gross_loss_usd"],
        "billed_amount_usd": 0.0,
        "remitted_amount_usd": 0.0,
        "settlement_status": "Quarterly Statement Certified",
        "aging_days": 0
    }
    BDX_RECORDS.append(p_row)
    bdx_id += 1

# -------------------------------------------------------------
# 5. GENERATE 25 CLAIM LOSS REPORTS
# -------------------------------------------------------------
report_claims = [c for c in CLAIMS if c.get("report_id")][:25]
for rc in report_claims:
    r_path = os.path.join(OUT_REP, f"{rc['report_id']}.txt")
    with open(r_path, "w") as f:
        f.write(f"EXL COMMERCIAL PROPERTY INDEPENDENT ADJUSTER REPORT\n")
        f.write(f"Report ID: {rc['report_id']} | Date of Report: {rc['loss_date']}\n")
        f.write(f"Claim ID: {rc['claim_id']} | Policy: {rc['policy_number']}\n")
        f.write(f"Insured: {rc['insured_name']}\n")
        f.write(f"Location of Loss: {rc['location']}\n")
        f.write(f"Event Association: {rc['event_id']}\n\n")
        f.write(f"EXECUTIVE SUMMARY (PAGE 1):\n")
        f.write(f"On {rc['loss_date']}, the insured premises sustained major structural damage resulting from {rc['peril']}.\n")
        f.write(f"Adjuster verified direct physical loss to warehouse roofs, perimeter cladding, and storage contents.\n\n")
        f.write(f"QUANTIFICATION OF LOSS (PAGE 2):\n")
        f.write(f"- Gross Incurred Loss: USD ${rc['gross_loss_usd']:,.2f}\n")
        f.write(f"- Paid Damages to Date: USD ${rc['paid_loss_usd']:,.2f}\n")
        f.write(f"- Outstanding Case Reserves: USD ${rc['case_reserves_usd']:,.2f}\n")
        f.write(f"- Applicable Primary Deductible: USD $50,000.00 (absorbed by insured)\n\n")
        f.write(f"REINSURANCE APPLICABILITY & CEDED RECOVERY NOTE (PAGE 3):\n")
        f.write(f"Reinsurance treaty applicable: {rc['treaty_id']}.\n")
        f.write(f"Incurred damage status is verified by Senior Field General Adjuster.\n")

# -------------------------------------------------------------
# 6. WRITE OUT PROCESSED CSVs & JSONs
# -------------------------------------------------------------
with open(os.path.join(OUT_PROC, "claims_list.csv"), "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=list(CLAIMS[0].keys()))
    writer.writeheader()
    writer.writerows(CLAIMS)

with open(os.path.join(OUT_PROC, "broker_bordereau.csv"), "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=list(BDX_RECORDS[0].keys()))
    writer.writeheader()
    writer.writerows(BDX_RECORDS)

with open(os.path.join(OUT_PROC, "master_answer_key.json"), "w") as f:
    json.dump(ANSWER_KEY, f, indent=2)

loss_run = []
for t in TREATIES:
    tid = t["treaty_id"]
    t_claims = [c for c in CLAIMS if c["treaty_id"] == tid]
    tot_gross = sum(c["gross_loss_usd"] for c in t_claims)
    tot_paid = sum(c["paid_loss_usd"] for c in t_claims)
    tot_res = sum(c["case_reserves_usd"] for c in t_claims)
    tot_billed = sum(c["billed_reinsurance_usd"] for c in t_claims)
    tot_recv = sum(c["received_reinsurance_usd"] for c in t_claims)
    loss_run.append({
        "treaty_id": tid,
        "treaty_name": t["treaty_name"],
        "treaty_limit": t["limit_usd"],
        "treaty_retention": t["retention_usd"],
        "total_claims_count": len(t_claims),
        "total_gross_incurred_usd": round(tot_gross, 2),
        "total_paid_losses_usd": round(tot_paid, 2),
        "total_case_reserves_usd": round(tot_res, 2),
        "total_reinsurance_billed_usd": round(tot_billed, 2),
        "total_reinsurance_received_usd": round(tot_recv, 2),
        "remaining_capacity_usd": round(t["limit_usd"] - tot_recv, 2)
    })

with open(os.path.join(OUT_PROC, "treaty_loss_run.json"), "w") as f:
    json.dump(loss_run, f, indent=2)

print(f"Generated:")
print(f"- Treaties: {len(TREATIES)}")
print(f"- Catastrophe Events: {len(EVENTS)}")
print(f"- Claims: {len(CLAIMS)}")
print(f"- Broker Bordereau (BDX) Rows: {len(BDX_RECORDS)}")
print(f"- Claim Adjuster Reports: {len(report_claims)}")
print(f"- Master Answer Key Entries: {len(ANSWER_KEY)}")
print(f"- Planted Anomalies: {sum(1 for a in ANSWER_KEY if a['is_anomaly'])}")
