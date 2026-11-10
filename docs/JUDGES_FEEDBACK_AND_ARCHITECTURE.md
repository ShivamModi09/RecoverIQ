# RecoverIQ — Senior Leadership & Judges Feedback Analysis
**EXL AI Buildathon 2026**  
**Reviewer:** Sayan Ghosh  
**Engineering Leads:** Ashish Chavan, Shivam Modi, Arin Mangal  
**Mentor/Project Lead:** Biswajit Das  

---

## 1. Key Takeaways & Strategic Endorsement

1. **Strategic Topic Selection**:
   - Reinsurance is a greenfield area in the competition and across EXL solutions ("Stand out any which way by choosing a product which nobody else has").
   - Clear and immediate **bottom-line dollar impact** — every dollar recovered goes straight to company profit.

2. **Shift Positioning: From Just "Missed Claims" to "Leakage & Complex Treaty Interpretation"**:
   - In real-world commercial reinsurance, missed money doesn't simply happen because someone failed to notice a claim.
   - It primarily occurs because **treaty structures, layered towers, attachment points, and sharing arrangements are highly intricate**, leading to miscalculations, wrong layer allocations, and un-reconciled broker statements.

3. **"Breadth over Depth" Strategy (Pareto 80/20)**:
   - Sayan explicitly advised: *"Go broad rather than depth, but touch everything in the breadth of it."*
   - Cover realistic industry complexity (layers, broker bordereaux, reserves) even at a lighter, synthetic 80% level, rather than getting bogged down in legal edge cases.

---

## 2. Technical Feedback & Architecture Enhancements

### A. Multi-Agent Sequential Workflow (Optical & Architectural)
Instead of a single opaque box, present the solution as a clear multi-agent modular pipeline where each agent’s output is transparently inspectable:

```
[ Ingested Files ]
       │
       ▼
┌───────────────────────────────────────────────┐
│ 1. Treaty Policy Intelligence Agent          │
│    - Extracts: Attachment points, Limits,     │
│      Exclusions, Layers, Reinstatement rules, │
│      Quota share % vs Excess of Loss terms   │
│    - Emits structured JSON + Page Citations   │
└───────────────────────┬───────────────────────┘
                        │
                        ▼
┌───────────────────────────────────────────────┐
│ 2. Recovery Calculation Engine / Agent        │
│    - Pre-fed Reinsurance Domain Ontology      │
│    - Layering logic (Primary vs Excess layers)│
│    - Cumulates losses (Loss Runs, Reserves)   │
│    - Evaluates available "kitty" balance      │
│    - Calculates exact recoverable dollars     │
│    - Computes confidence score for each       │
└───────────────────────┬───────────────────────┘
                        │
                        ▼
┌───────────────────────────────────────────────┐
│ 3. Reconciliation & Leakage Detection Agent  │
│    - 3-Way Cross-Match: Treaty entitlement    │
│      vs Billed vs Broker Bordereau received   │
│    - Flags: Missed, Under-billed, Unpaid,     │
│      Wrong Peril, Exhausted Layer             │
│    - Confidence percentage & dollar impact    │
└───────────────────────┬───────────────────────┘
                        │
                        ▼
┌───────────────────────────────────────────────┐
│ 4. Analyst Audit & Explanation Workbench      │
│    - Side-by-side evidence pane               │
│    - Treaty clause quote with page number     │
│    - Step-by-step formula transparency        │
│    - Human-in-the-loop: Confirm or Reject     │
└───────────────────────────────────────────────┘
```

---

### B. Ingestion File Expansion: The "Bordereau" & "Loss Run" Additions
Sayan highlighted that in reinsurance, claims and placements flow through **Brokers** and **Bordereaux**. Adding these makes our synthetic dataset authentic and enterprise-ready:

1. **Broker Bordereaux (BDX)**:
   - Monthly/quarterly tabular statements sent by reinsurance brokers detailing ceded risks, paid claims, pending recoveries, and broker fees.
2. **Loss Runs & Case Reserves**:
   - Historical claim loss history by policy year/accident year.
   - Cumulative paid losses + outstanding case reserves (knowing how much was already claimed against the treaty limit to track remaining treaty capacity).
3. **Layered Towers / Syndicated Placements**:
   - e.g., Layer 1: \$1M xs \$500k; Layer 2: \$5M xs \$1.5M with split participation (e.g., 60% Munich Re, 40% Swiss Re).

---

### C. Reinsurance Domain Ontology to Pre-Feed into the Engine
Sayan requested an explicit 10–12 metric ontology:
1. **Attachment Point / Retention**: Dollar threshold the primary insurer must absorb before reinsurance attaches.
2. **Limit of Liability**: Maximum recoverable amount per risk or per occurrence.
3. **Excess of Loss (XOL)**: Per-occurrence or per-risk reinsurance cover.
4. **Quota Share (%)**: Pro-rata percentage split of premiums and losses.
5. **Loss Occurrence / Hours Clause**: Catastrophe definition (e.g., 72 hours or 168 hours window for windstorms).
6. **Cumulative Paid Losses (Loss Run)**: Total claims paid to date under the treaty year.
7. **Case Reserves**: Estimated future payments reserved on open claims.
8. **Treaty Capacity Remaining (The "Kitty" Balance)**: Treaty limit minus cumulative previous recoveries.
9. **Reinstatement Premium**: Cost required to restore treaty coverage after a major loss.
10. **Excluded Perils / Sub-limits**: Perils excluded (e.g., Flood, Cyber) or subject to separate lower caps.
11. **Recoverable Amount**: `min(Limit, max(0, Incurred Loss - Retention) * Participation %)`.
12. **Leakage Amount**: `Recoverable Amount - (Actually Billed or Received)`.

---

### D. UI/UX & Demonstration Guidance (For Shivam & Team)
- Biswajit noted that **Shivam** has strong experience from the prior **Cyber Rating** initiative in building interactive frontends and connecting pipeline stages.
- The UI should feature:
  - **Pipeline visualizer**: Visual step indicators showing inputs → extraction → calculation → reconciliation.
  - **Side-by-side verification screen**: Left side shows original PDF snippet/treaty clause with highlighting; right side shows mathematical formula and billed variance.
  - **Summary Dashboard**: Total recovered dollar opportunity, total leakage prevented, breakdown by leakage category.
  - **Confidence Scores**: Explicit confidence percentage on each identified recovery gap.

