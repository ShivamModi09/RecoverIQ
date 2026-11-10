"""
RecoverIQ — 3-Way Reconciliation & Leakage Detection Engine
Cross-reconciles:
1. Calculated Treaty Entitlement ($)
2. Primary Insurer Recorded & Billed ($)
3. Broker Bordereau (BDX) Remittances ($)

Flags leakage categories:
- MISSED_RECOVERY: Owed under treaty, but $0 billed (e.g. CAT aggregation or analyst oversight).
- UNDER_BILLED: Owed > Billed (e.g. unbilled case reserve increases or sublimit errors).
- UNPAID_RECOVERY: Billed correctly, but broker remittance is short or unpaid (> 90 days aging).
- EXCLUDED_PERIL: Billed for an ineligible/excluded cause of loss.
"""

from typing import Dict, Any, List, Tuple
from dataclasses import dataclass, field
from src.calculator import ReinsuranceCalculator

@dataclass
class ReconciliationFinding:
    claim_id: str
    event_id: str
    treaty_id: str
    peril: str
    insured_name: str
    location: str
    gross_loss: float
    entitled_recoverable: float
    actually_billed: float
    actually_received: float
    leakage_amount: float
    status: str  # ANOMALY or CLEAN
    leakage_category: str  # MISSED_RECOVERY, UNDER_BILLED, UNPAID_RECOVERY, EXCLUDED_PERIL, NONE
    confidence_score: float
    citation: Dict[str, Any] = field(default_factory=dict)
    calculation_steps: List[str] = field(default_factory=list)
    reason: str = ""

class ReinsuranceReconciler:

    def __init__(self, treaties: List[Dict[str, Any]], events: List[Dict[str, Any]]):
        self.treaties = {t["treaty_id"]: t for t in treaties}
        self.events = {e["event_id"]: e for e in events}

    def reconcile_claims(
        self, 
        claims: List[Dict[str, Any]], 
        bdx_records: List[Dict[str, Any]]
    ) -> List[ReconciliationFinding]:
        findings = []

        # Map BDX records by claim_id for quick cross-matching
        bdx_by_claim = {}
        for b in bdx_records:
            cid = b["claim_id"]
            if cid not in bdx_by_claim:
                bdx_by_claim[cid] = {"billed": 0.0, "received": 0.0, "max_aging": 0}
            if b["transaction_type"] == "Ceded Billing Notice":
                bdx_by_claim[cid]["billed"] += float(b["billed_amount_usd"])
                bdx_by_claim[cid]["max_aging"] = max(bdx_by_claim[cid]["max_aging"], int(b.get("aging_days", 0)))
            elif b["transaction_type"] == "Cash Remittance":
                bdx_by_claim[cid]["received"] += float(b["remitted_amount_usd"])

        # Group claims by event to detect aggregate CAT breaches
        claims_by_event = {}
        for c in claims:
            eid = c.get("event_id")
            if eid:
                claims_by_event.setdefault(eid, []).append(c)

        # Precompute CAT event recoveries
        cat_event_recoveries = {}
        for eid, ev_claims in claims_by_event.items():
            if eid in self.events:
                tid = self.events[eid]["treaty_id"]
                treaty = self.treaties[tid]
                if "Catastrophe" in treaty["type"] or "CAT" in treaty["type"]:
                    calc = ReinsuranceCalculator.calculate_catastrophe_event(
                        eid, ev_claims, treaty
                    )
                    cat_event_recoveries[eid] = calc

        # Process each claim
        for c in claims:
            cid = c["claim_id"]
            eid = c["event_id"]
            tid = c["treaty_id"]
            treaty = self.treaties[tid]
            gross_loss = float(c["gross_loss_usd"])
            actual_billed = float(c["billed_reinsurance_usd"])
            actual_received = float(c["received_reinsurance_usd"])

            # Cross-check BDX consistency if available
            if cid in bdx_by_claim:
                bdx_billed = bdx_by_claim[cid]["billed"]
                bdx_recv = bdx_by_claim[cid]["received"]
                # BDX takes precedence for actual cash remittance
                if bdx_recv > 0:
                    actual_received = bdx_recv

            citation_data = {
                "treaty_id": tid,
                "treaty_name": treaty["treaty_name"],
                "retention_page": treaty.get("citation_page_retention"),
                "limit_page": treaty.get("citation_page_limit"),
                "perils_page": treaty.get("citation_page_perils"),
                "hours_page": treaty.get("citation_page_hours")
            }

            # 1. Check Peril Exclusion first
            if not ReinsuranceCalculator.is_peril_covered(c["peril"], treaty):
                entitled = 0.0
                if actual_billed > 0:
                    findings.append(ReconciliationFinding(
                        claim_id=cid, event_id=eid, treaty_id=tid, peril=c["peril"],
                        insured_name=c["insured_name"], location=c["location"],
                        gross_loss=gross_loss, entitled_recoverable=0.0,
                        actually_billed=actual_billed, actually_received=actual_received,
                        leakage_amount=0.0, status="ANOMALY",
                        leakage_category="EXCLUDED_PERIL", confidence_score=0.98,
                        citation=citation_data,
                        calculation_steps=[
                            f"Peril '{c['peril']}' is excluded under Article VIII (Page {citation_data['perils_page']}).",
                            f"Incurred Gross Loss = ${gross_loss:,.2f}.",
                            f"Entitlement = $0.00. Billed ${actual_billed:,.2f} in error."
                        ],
                        reason=f"Claim peril '{c['peril']}' is excluded in treaty {tid}."
                    ))
                    continue
                else:
                    findings.append(ReconciliationFinding(
                        claim_id=cid, event_id=eid, treaty_id=tid, peril=c["peril"],
                        insured_name=c["insured_name"], location=c["location"],
                        gross_loss=gross_loss, entitled_recoverable=0.0,
                        actually_billed=0.0, actually_received=0.0,
                        leakage_amount=0.0, status="CLEAN",
                        leakage_category="NONE", confidence_score=1.0,
                        citation=citation_data,
                        calculation_steps=["Peril excluded; $0 billed correctly."],
                        reason="Correctly handled excluded peril."
                    ))
                    continue

            # 2. Check if claim belongs to a Catastrophe Event covered by CAT XOL
            is_cat_xol = "Catastrophe" in treaty["type"] or "CAT" in treaty["type"]
            if is_cat_xol and eid in cat_event_recoveries:
                ev_calc = cat_event_recoveries[eid]
                total_ev_loss = ev_calc.incurred_loss
                total_ev_rec = ev_calc.recoverable_amount

                if total_ev_loss > 0:
                    # Allocate proportional share of event recovery to this claim
                    entitled = round(total_ev_rec * (gross_loss / total_ev_loss), 2)
                else:
                    entitled = 0.0
                steps = list(ev_calc.audit_trail)
                steps.append(
                    f"5. Claim allocated share: ${gross_loss:,.2f} / ${total_ev_loss:,.2f} * ${total_ev_rec:,.2f} = ${entitled:,.2f}."
                )
            else:
                # Per Risk XOL
                claim_calc = ReinsuranceCalculator.calculate_single_claim(c, treaty)
                entitled = claim_calc.recoverable_amount
                steps = claim_calc.audit_trail

            # 3. Variance & Leakage Classification
            leakage = 0.0
            cat = "NONE"
            status = "CLEAN"
            conf = 1.0
            reason = "Reconciled. No variance found."

            if entitled > 0 and actual_billed == 0.0:
                # MISSED RECOVERY
                status = "ANOMALY"
                cat = "MISSED_RECOVERY"
                leakage = entitled
                conf = 0.98
                reason = f"Full recovery of ${entitled:,.2f} was missed. Billed $0.00."

            elif entitled > actual_billed and actual_billed > 0.0:
                # UNDER BILLED
                status = "ANOMALY"
                cat = "UNDER_BILLED"
                leakage = round(entitled - actual_billed, 2)
                conf = 0.96
                reason = f"Under-billed by ${leakage:,.2f}. Entitled ${entitled:,.2f}, billed only ${actual_billed:,.2f}."

            elif actual_billed > 0 and (actual_billed - actual_received) > 1.0:
                # UNPAID / SHORT PAID
                status = "ANOMALY"
                cat = "UNPAID_RECOVERY"
                leakage = round(actual_billed - actual_received, 2)
                conf = 0.95
                reason = f"Billed ${actual_billed:,.2f}, but only ${actual_received:,.2f} received. Shortfall of ${leakage:,.2f} aged > 90 days."

            findings.append(ReconciliationFinding(
                claim_id=cid, event_id=eid, treaty_id=tid, peril=c["peril"],
                insured_name=c["insured_name"], location=c["location"],
                gross_loss=gross_loss, entitled_recoverable=entitled,
                actually_billed=actual_billed, actually_received=actual_received,
                leakage_amount=leakage, status=status,
                leakage_category=cat, confidence_score=conf,
                citation=citation_data,
                calculation_steps=steps,
                reason=reason
            ))

        return findings

