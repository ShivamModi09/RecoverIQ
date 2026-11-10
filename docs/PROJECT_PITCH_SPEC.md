# RecoverIQ — MVP Pitch Specification
**EXL AI BUILDATHON 2026 · MVP · COMMERCIAL PROPERTY INSURANCE**  
*Built and Demonstrated on Synthetic Data*

---

## 1. Executive Summary & Core Concept

**RecoverIQ** is an AI-enabled analytics and reconciliation engine designed to:
> *"Find the reinsurance money an insurer was owed on past claims but never billed, and show the evidence for every amount."*

### Key Insurance & Reinsurance Definitions
- **Treaty**: The contract in which a reinsurer agrees to pay part of the insurer's large losses.
- **Retention**: The amount of each loss the insurer pays itself before the reinsurer pays.
- **Limit**: The most the reinsurer will pay for one loss event.
- **Recovery**: The money the insurer claims back from the reinsurer.

---

## 2. Why This Idea

### User Story
> *"As a reinsurance analyst at a commercial property insurer, I want to check last year's claims against our treaties and see which recoveries we missed or under-billed, so that I can claim them from the reinsurer with clear evidence."*

### Motivating Example: How Money Gets Missed
One windstorm damages four insured warehouses. Each individual claim is below the $2.0M retention threshold, so none is sent for review. But the treaty counts the whole storm as one event, and together the claims exceed the retention:

- **Claim 1**: \$0.9M
- **Claim 2**: \$0.8M
- **Claim 3**: \$0.7M
- **Claim 4**: \$0.5M
- **Storm Total**: **\$2.9M**
- **Retention**: **\$2.0M**
- **Reinsurer Owes**: **\$0.9M**
- **Actually Billed**: **\$0** (Direct leak of \$900k profit!)

### Value Proposition (Why It Is Worth Solving)
1. **Direct Bottom-Line Impact**: Recovered money goes straight to profit. A recovery that is never billed is permanently lost; reinsurers have no incentive to point it out.
2. **Current Process is Manual & Fragile**: Reinsurance analysts manually read treaty contracts and work out claims in complex spreadsheets.
3. **Common Failure Modes**:
   - Small claims from one single catastrophic event aggregate above retention.
   - Initial billings are not updated when ultimate loss or case reserves grow.
   - Payments from reinsurers are never received, short-paid, or missed.
4. **Low Client Effort / High Feasibility**: Operates as a retrospective audit on historical files; no complex integration with live core legacy systems required.

### Why Commercial Property?
- High severity: Large fires and weather events regularly trigger reinsurance attachment points.
- Clean foundational math: Standard Excess of Loss (XOL) formulas are well-defined.
- High document volume: Long claim adjustor reports and complex treaty legal documents make AI/GenAI an ideal fit.

---

## 3. MVP Scope Boundaries

### What is INCLUDED:
- **LOB**: Commercial property claims for one year (in USD).
- **Treaty Type**: Excess of Loss (reinsurer pays event loss above retention up to the limit).
- **AI Extraction**: AI reads treaties and claim reports, citing exact page references for each extracted parameter.
- **Deterministic Calculation**: Rule-based calculator computes what the reinsurer should have paid.
- **Reconciliation Engine**: Compares calculated amounts with insurer's recorded, billed, and received records.
- **Analyst Audit Screen**: Displays ranked gaps with side-by-side evidence (treaty clause, claim details, math calculation) for analyst verification.

### What is NOT INCLUDED (Deferred):
- Real-time prospective claims billing on live new claims (future phase).
- Complex alternative treaty lines (e.g., complex multi-tier whole-account stop loss).
- Clustering claims into catastrophe events (event grouping is pre-tagged in data).
- Contested legal disputes over obscure ambiguity clauses.
- Automated API billing/remittance into production banking/ERP.

---

## 4. Synthetic Data Generation Plan

Because real client reinsurance files are proprietary and confidential, synthetic data is generated with Python scripts and LLMs.

### Ingestion Dataset Table

| Data Asset | Format | Target Size | Content Description |
| :--- | :--- | :--- | :--- |
| **Treaty Documents** | PDF | ~3 treaties | Reinsurance contracts specifying retentions, limits, inception/expiry dates, perils covered (e.g., fire, wind covered; flood excluded). |
| **Claims List** | Spreadsheet | ~150 claims | Claim number, date of loss, cause/peril, location, gross loss amount, paid to date, status, and associated Event ID. |
| **Claim Reports** | PDF | ~25 reports | Detailed adjuster loss narratives for select claims (including all cases with planted anomalies). |
| **Events List** | Spreadsheet | ~12 events | Named CAT events (storms, wildfires) that aggregated across multiple properties. |
| **Recovery Records** | Spreadsheet | ~300 rows | Recorded ceded amounts, invoice dates, billed amounts, and actual cash received from reinsurers. |
| **Ground Truth Answer Key** | File | 1 master key | Hidden ground truth benchmark used to validate RecoverIQ's recall and accuracy. |

### Planted Anomaly Types (~30 problematic cases)
1. **Missed Recovery**: Loss exceeded retention/layer, money was owed, but \$0 was billed.
2. **Under-Billed**: Recoverable amount was calculated incorrectly or billed lower than treaty entitlement.
3. **Not Received / Short-Paid**: Billed correctly, but reinsurer payment was partial, delayed, or missing without follow-up.
4. **Wrong Entry / Ineligible**: Billed for an excluded peril (e.g., flood), wrong policy period, or double-billed.

### Generation Methodology
- Python generates numerical truth first so all spreadsheets and PDFs remain 100% mathematically consistent.
- LLMs are used to introduce realistic adjuster phrasing and contract clause styling (never modifying amounts).
- Borderline boundary cases included (e.g., loss at \$1.99M or \$2.01M with \$2.0M retention).
- All screens and data marked **SYNTHETIC**.

---

## 5. End-to-End Workflow Architecture

```
[1. Inputs]
 ├── Treaty Documents (PDF)
 ├── Claim Reports (PDF)
 ├── Claims & Events (Excel/CSV)
 └── Recovery Records (Excel/CSV)
       │
       ▼
[2. Read Documents (AI + Verification)]
 ├── AI extracts key values (retentions, limits, dates, perils, page citations)
 └── Validation against structural rules; flag ambiguous clauses
       │
       ▼
[3. Calculate & Compare (Deterministic Engine)]
 ├── Eligibility Verification (dates, covered perils)
 ├── Recoverable Calculation (Event loss above retention up to limit)
 └── 3-Way Variance Check (Calculated vs. Recorded vs. Billed vs. Received)
       │
       ▼
[4. Analyst Audit & Review Screen]
 ├── AI-generated succinct executive summary using deterministic numbers
 └── Interactive UI: Filtered gaps ranked by dollar leakage with side-by-side evidence
```

---

## 6. Success Metrics & Demonstration Targets (Nov 17 Demo)
- **Mathematical Accuracy**: 100% match with the deterministic calculation engine against answer key.
- **Anomaly Detection Rate**: ≥ 90% (find at least 9 in 10 planted anomalies) with low false alarms.
- **Traceability & Evidence**: 100% of flagged leaks feature side-by-side treaty clause excerpts, page citations, and math breakdowns.
- **Fault-Tolerant Resilience**: Core rules and reconciliation operate smoothly even if LLM services experience latency.

