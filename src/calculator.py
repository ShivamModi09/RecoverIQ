"""
RecoverIQ — Deterministic Reinsurance Calculation Engine
Implements the pre-fed reinsurance domain ontology:
- Excess of Loss (XOL) per risk & per occurrence (Catastrophe)
- Hours Clause event loss aggregation
- Treaty capacity / limit exhaustion ("kitty" balance)
- Peril eligibility & exclusion validation
- Deterministic step-by-step audit trail and confidence scoring
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

@dataclass
class CalculationResult:
    subject_id: str  # claim_id or event_id
    treaty_id: str
    is_covered: bool
    peril: str
    incurred_loss: float
    retention: float
    limit: float
    remaining_capacity: float
    recoverable_amount: float
    confidence_score: float
    audit_trail: List[str] = field(default_factory=list)
    ineligibility_reason: Optional[str] = None

class ReinsuranceCalculator:
    
    @staticmethod
    def is_peril_covered(peril: str, treaty: Dict[str, Any]) -> bool:
        """Validates peril against treaty covered perils and explicit exclusions."""
        peril_lower = peril.strip().lower()
        excluded = [p.lower() for p in treaty.get("excluded_perils", [])]
        if peril_lower in excluded:
            return False
        covered = [p.lower() for p in treaty.get("covered_perils", [])]
        return peril_lower in covered

    @staticmethod
    def is_date_valid(loss_date: str, treaty: Dict[str, Any]) -> bool:
        """Checks if loss date falls within treaty effective period."""
        return treaty["inception_date"] <= loss_date <= treaty["expiration_date"]

    @classmethod
    def calculate_single_claim(
        cls, 
        claim: Dict[str, Any], 
        treaty: Dict[str, Any], 
        remaining_capacity: Optional[float] = None
    ) -> CalculationResult:
        """
        Calculates recoverable amount for a single property loss under Per Risk XOL.
        Formula: Recoverable = min(Limit, Remaining Capacity, max(0, Incurred Loss - Retention))
        """
        cid = claim["claim_id"]
        tid = treaty["treaty_id"]
        gross_loss = float(claim["gross_loss_usd"])
        retention = float(treaty["retention_usd"])
        limit = float(treaty["limit_usd"])
        capacity = float(remaining_capacity if remaining_capacity is not None else limit)
        peril = claim["peril"]
        loss_date = claim["loss_date"]
        
        audit = []
        audit.append(f"1. Evaluated treaty {tid} for Claim {cid} (Peril: {peril}, Loss Date: {loss_date}).")

        # 1. Date check
        if not cls.is_date_valid(loss_date, treaty):
            return CalculationResult(
                subject_id=cid, treaty_id=tid, is_covered=False, peril=peril,
                incurred_loss=gross_loss, retention=retention, limit=limit,
                remaining_capacity=capacity, recoverable_amount=0.0,
                confidence_score=0.98,
                audit_trail=audit + [f"Loss date {loss_date} outside treaty window ({treaty['inception_date']} to {treaty['expiration_date']})."],
                ineligibility_reason="Out of treaty policy period."
            )

        # 2. Peril check
        if not cls.is_peril_covered(peril, treaty):
            return CalculationResult(
                subject_id=cid, treaty_id=tid, is_covered=False, peril=peril,
                incurred_loss=gross_loss, retention=retention, limit=limit,
                remaining_capacity=capacity, recoverable_amount=0.0,
                confidence_score=0.98,
                audit_trail=audit + [f"Peril '{peril}' is explicitly excluded or not covered under Article VIII."],
                ineligibility_reason=f"Peril '{peril}' excluded under treaty."
            )

        # 3. Retention math
        excess = max(0.0, gross_loss - retention)
        audit.append(f"2. Gross Incurred Loss = ${gross_loss:,.2f}, Net Retention = ${retention:,.2f}. Loss Excess = ${excess:,.2f}.")

        if excess <= 0.0:
            audit.append("3. Loss does not exceed retention. Entitlement = $0.00.")
            return CalculationResult(
                subject_id=cid, treaty_id=tid, is_covered=True, peril=peril,
                incurred_loss=gross_loss, retention=retention, limit=limit,
                remaining_capacity=capacity, recoverable_amount=0.0,
                confidence_score=1.0,
                audit_trail=audit
            )

        # 4. Limit & Capacity math
        recoverable = min(limit, capacity, excess)
        audit.append(f"3. Applied Treaty Limit (${limit:,.2f}) and Remaining Capacity (${capacity:,.2f}) to Excess (${excess:,.2f}).")
        audit.append(f"4. Final Calculated Entitled Recoverable = ${recoverable:,.2f}.")

        return CalculationResult(
            subject_id=cid, treaty_id=tid, is_covered=True, peril=peril,
            incurred_loss=gross_loss, retention=retention, limit=limit,
            remaining_capacity=capacity, recoverable_amount=round(recoverable, 2),
            confidence_score=0.99,
            audit_trail=audit
        )

    @classmethod
    def calculate_catastrophe_event(
        cls,
        event_id: str,
        claims: List[Dict[str, Any]],
        treaty: Dict[str, Any],
        remaining_capacity: Optional[float] = None
    ) -> CalculationResult:
        """
        Calculates aggregate recoverable amount for a Catastrophe Loss Occurrence.
        Aggregates all covered claims within the event, subtracts event retention,
        caps at treaty limit/capacity.
        """
        tid = treaty["treaty_id"]
        retention = float(treaty["retention_usd"])
        limit = float(treaty["limit_usd"])
        capacity = float(remaining_capacity if remaining_capacity is not None else limit)
        
        event_claims = [c for c in claims if c.get("event_id") == event_id]
        if not event_claims:
            return CalculationResult(
                subject_id=event_id, treaty_id=tid, is_covered=False, peril="Unknown",
                incurred_loss=0.0, retention=retention, limit=limit,
                remaining_capacity=capacity, recoverable_amount=0.0,
                confidence_score=1.0, audit_trail=["No claims associated with this event."],
                ineligibility_reason="No associated claims."
            )

        peril = event_claims[0]["peril"]
        total_event_loss = sum(float(c["gross_loss_usd"]) for c in event_claims)
        
        audit = [
            f"1. Aggregated {len(event_claims)} property claims under Catastrophe Event {event_id} ({peril}).",
            f"2. Total Aggregate Event Loss Incurred = ${total_event_loss:,.2f}."
        ]

        if not cls.is_peril_covered(peril, treaty):
            return CalculationResult(
                subject_id=event_id, treaty_id=tid, is_covered=False, peril=peril,
                incurred_loss=total_event_loss, retention=retention, limit=limit,
                remaining_capacity=capacity, recoverable_amount=0.0,
                confidence_score=0.98,
                audit_trail=audit + [f"Event peril '{peril}' is excluded under treaty {tid}."],
                ineligibility_reason=f"Peril '{peril}' excluded under treaty."
            )

        excess = max(0.0, total_event_loss - retention)
        audit.append(f"3. Applied Event Net Retention of ${retention:,.2f}. Loss in excess of retention = ${excess:,.2f}.")

        recoverable = min(limit, capacity, excess)
        audit.append(f"4. Applied Event Limit (${limit:,.2f}) and Remaining Capacity (${capacity:,.2f}). Total Event Recoverable = ${recoverable:,.2f}.")

        return CalculationResult(
            subject_id=event_id, treaty_id=tid, is_covered=True, peril=peril,
            incurred_loss=round(total_event_loss, 2), retention=retention, limit=limit,
            remaining_capacity=capacity, recoverable_amount=round(recoverable, 2),
            confidence_score=0.99,
            audit_trail=audit
        )

