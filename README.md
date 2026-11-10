# RecoverIQ — AI-Powered Reinsurance Leakage & Reconciliation Workbench
**EXL AI Buildathon 2026 · Commercial Property Insurance MVP**

> *"Find the reinsurance money an insurer was owed on past claims but never billed, and show verifiable evidence for every dollar."*

---

## 👥 Project Team & Stakeholders
- **Project Lead / Mentor:** Biswajit Das
- **Engineering Leads:** Shivam Manojkumar Modi, Ashish Chavan, Arin
- **Senior Judge & Reviewer:** Sayan Ghosh
- **Milestone Date:** 17 November 2026 (Working MVP Demo)

---

## 💡 The Core Problem: How Reinsurance Money Gets Missed
Commercial property insurers buy reinsurance to protect against large losses. However, primary insurers regularly miss out on millions of dollars in legitimate recoveries due to manual tracking in spreadsheets and complex multi-page treaties.

### The Motivating Example (CAT-2025-02 Windstorm Vance):
A single windstorm damages four insured warehouses:
- Warehouse 1: **\$900k**
- Warehouse 2: **\$800k**
- Warehouse 3: **\$700k**
- Warehouse 4: **\$500k**
- **Storm Total Loss:** **\$2.9M**
- **Treaty Retention (Deductible):** **\$2.0M**
- **Reinsurer Owes:** **\$900k**
- **Actually Billed:** **\$0** (Individual claims were each below \$2.0M, so analysts overlooked the aggregate event entitlement).

**RecoverIQ** eliminates this leakage by combining **autonomous GenAI document agents** with **deterministic calculation rules** and **3-way broker reconciliation**.

---

## 🏗️ Core Architecture & Pipeline

```
[ Ingested Files ]
  ├── Treaty Documents (3 Commercial XOL Contracts: PDF / Legal Text)
  ├── Loss Portfolio (150 Claims · 12 CAT Events · 25 Adjuster Reports)
  ├── Broker Bordereaux (300 BDX Ceded Billing & Remittance Records)
  └── Cumulative Loss Runs & Case Reserves (Remaining Capacity Tracker)
            │
            ▼
┌─────────────────────────────────────────────────────────┐
│ 1. Treaty Policy Intelligence Agent (Agent A)           │
│    - Powered by Groq LLM (openai/gpt-oss-120b)          │
│    - Extracts: Retention, Limit, Perils, Hours Clause,  │
│      and exact page citations into structured JSON       │
└───────────────────────────┬─────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│ 2. Recovery Calculation Engine                          │
│    - Deterministic Reinsurance Domain Logic (No AI math)│
│    - Excess of Loss, Quota Share, Kitty Check           │
│    - Calculates Recoverable $ + Confidence Score        │
└───────────────────────────┬─────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│ 3. Reconciliation & Leakage Detection Engine            │
│    - 3-Way Cross-Match: Entitled vs Billed vs BDX Recv  │
│    - Detects 30 planted anomalies with 100% precision   │
└───────────────────────────┬─────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│ 4. Audit & Legal Explanation Agent (Agent B)            │
│    - Powered by Groq LLM (openai/gpt-oss-120b)          │
│    - Synthesizes formal Proof-of-Loss Notice &          │
│      Reinsurance Billing Demand Brief for Brokers       │
└───────────────────────────┬─────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│ 5. Analyst Audit Workbench (UI / Dashboard)             │
│    - Live streaming multi-agent flowchart (Cyber style) │
│    - Side-by-side contract citations & math audit trail │
│    - One-click Confirm / Dispute recovery actions       │
└─────────────────────────────────────────────────────────┘
```

---

## 🛠️ Setup & Installation

RecoverIQ is built with radical simplicity and zero third-party bloat. All core modules run on the **Python 3.9+ Standard Library** with zero external pip dependencies.

### Prerequisites
- **Python 3.9 or higher** (`python3 --version`)
- **Git** (`git --version`)
- *(Optional)* **Groq API Key** for live LLM inference (`export GROQ_API_KEY="..."`). The platform includes automatic deterministic fallbacks if offline.

### 1. Clone the Repository
```bash
git clone https://github.com/shivammodi/Buildathon-17Nov.git
cd Buildathon-17Nov
```

### 2. Configure Environment (Optional for Live Groq LLM)
If you want to run live LLM contract parsing and notice drafting via Groq:
```bash
export GROQ_API_KEY="your-groq-api-key-here"
```
*(If omitted, RecoverIQ automatically falls back to deterministic rule extraction without failing).*

---

## 💻 How to Use

Follow these verified steps to run the pipeline from scratch:

### Step 1: Generate & Verify the Synthetic Dataset
Generate the 150 claims, 3 legal treaties, 12 CAT events, 300 broker bordereaux (BDX) records, and master answer key:
```bash
python3 scripts/generate_synthetic_data.py
python3 scripts/verify_synthetic_data.py
```
*Expected Output:* `ALL VERIFICATIONS PASSED: 100% consistent referential integrity & 30 planted anomalies verified.`

### Step 2: Run the 3-Way Reconciliation Benchmark
Execute the automated cross-reconciliation engine against the ground truth benchmark:
```bash
python3 scripts/run_reconciliation.py
```
*Expected Output:*
```
==================================================
RECOVERIQ — BENCHMARK EVALUATION RESULTS
==================================================
Total Claims Analyzed:          150
Planted Anomalies in Key:       30
Anomalies Detected:             30
False Positives (Clean as Bug): 0
False Negatives (Missed Bug):   0
Exact Category Matches:         30 / 30
--------------------------------------------------
Recall (Target >= 90%):         100.00%
Precision:                      100.00%
Overall Accuracy:               100.00%
--------------------------------------------------
Total Ground Truth Leakage:     $17,653,338.77
Total Identified Leakage:       $17,653,338.77
==================================================
✓ VERIFICATION PASSED: Recall >= 90%, Precision >= 95%, Zero False Alarms.
```

### Step 3: Run the Automated Unit Test Suite
Run all 13 unit tests covering math formulas, treaty parsing, API servers, and LLM agent contracts:
```bash
python3 -m unittest discover tests/
```
*Expected Output:* `Ran 13 tests in 0.04s ... OK`

### Step 4: Launch the Interactive Web Dashboard
Start the local server:
```bash
python3 server.py 8080
```
Then open your browser to:
👉 **[http://localhost:8080](http://localhost:8080)**

---

## 🖥️ Web Dashboard Features

1. **⚡ Live Agentic Workflow Stream:**
   - Visualizes the entire autonomous agent graph inspired by Shivam's signature design from CyberRiskInsurance.
   - Click **"▶ Run Live Pipeline Stream"** to watch the real-time execution telemetry flow from document ingestion to Groq extraction, deterministic math, 3-way reconciliation, and human sign-off.
2. **📋 Audit Workbench & Evidence Pane:**
   - Filter portfolio by leakage category (*Missed Recovery, Under-Billed, Unpaid/Short-Paid, Excluded Peril*).
   - Click **"Audit Evidence"** on any claim to view side-by-side treaty citations, step-by-step math calculation proofs, and broker variance.
   - Click **"🤖 Generate LLM Recovery Notice"** to watch Groq draft a formal, adjuster-grade legal recovery demand brief live.
3. **📄 Treaty Policy Intelligence View:**
   - Inspect parsed treaties, retentions, limits, and covered perils.
   - Click **"🤖 Run Live LLM Extraction (Groq)"** on any contract to trigger real-time AI parsing.
4. **📊 Treaty Capacity & Loss Run Tracker:**
   - Monitors cumulative losses against treaty limits to prevent catastrophic capacity exhaustion.

---

## ❓ Technical Handover FAQ: 10 Core Questions & 1-Line Answers

1. **What is our input data, where is it stored, and is it real or synthetic?**  
   It is 100% synthetic (realistic but made-up) data generated by `scripts/generate_synthetic_data.py` into the `data/` directory (3 contracts, 150 claims, 300 broker transaction records, and 25 adjuster reports) because real insurance company claim records are confidential.

2. **Does the portfolio data change every time the application runs?**  
   No, the dataset is deterministic and stored permanently on disk using a fixed random seed (`42`) for consistent demo figures, though running `python3 scripts/generate_synthetic_data.py` can regenerate fresh records anytime.

3. **What is "reinsurance leakage" and what is the $2.9M windstorm example?**  
   Leakage is money contractually owed to the insurer that was never billed or collected; in our motivating case, four warehouse losses totaling $2.9M exceeded the $2.0M event retention, leaving $900,000 unbilled because claims were reviewed in isolation.

4. **How do I start and view the application from scratch?**  
   In your terminal, run `python3 server.py 8080` and open **`http://localhost:8080`** in any web browser.

5. **Do I need to install external Python packages or manage a virtual environment?**  
   No, the entire codebase runs exclusively on Python's built-in standard library (`urllib`, `json`, `csv`, `http.server`), requiring zero `pip` installations.

6. **Where is the Groq API key stored and how do I configure it?**  
   It can be set via the system environment variable `export GROQ_API_KEY="your_key"`, with a fallback default defined in `src/agents/groq_client.py`.

7. **How does the 3-way reconciliation algorithm actually match claims, treaties, and broker bordereaux (BDX)?**  
   `src/reconciler.py` aggregates claims by catastrophe event, evaluates treaty excess-of-loss math, and cross-references claim IDs against broker BDX transaction logs to flag any variance between entitled, billed, and remitted dollars.

8. **What does the AI agent do versus the deterministic Python engine?**  
   The Python rules engine performs 100% of the mathematical calculations to guarantee bug-free amounts, while the Groq LLM agents extract contract clauses from unstructured legal documents and draft formal billing demand briefs.

9. **What happens if the Groq API is offline, rate-limited, or unreachable?**  
   The application never crashes; both AI agents have built-in deterministic fallbacks that automatically provide local structured extractions and pre-formatted recovery notices.

10. **How is detection performance verified against the ground truth?**  
    Running `python3 scripts/run_reconciliation.py` benchmarks the system against a hidden master answer key of 30 planted anomalies, verifying 100% recall and zero false alarms.

---

## 📁 Repository Map

```
.
├── server.py                        # Lightweight HTTP/REST Server (port 8080)
├── requirements.txt                 # Dependency documentation (pure standard library)
├── static/
│   └── index.html                   # Interactive Workbench & Agent Flowchart UI
├── src/
│   ├── calculator.py                # Deterministic Reinsurance Math & Ontology
│   ├── extractor.py                 # Structural Contract & Report Parser
│   ├── reconciler.py                # 3-Way Reconciliation & Leakage Detection Engine
│   └── agents/
│       ├── groq_client.py           # Standard Library Groq Cloud LLM Client
│       ├── treaty_agent.py          # Agent 1: Treaty Policy Intelligence (Groq)
│       └── explainer_agent.py       # Agent 2: Audit & Legal Demand Brief (Groq)
├── scripts/
│   ├── generate_synthetic_data.py   # Generates 150 claims, treaties, BDX, & ground truth
│   ├── verify_synthetic_data.py     # Rigorous mathematical invariant & foreign key test
│   └── run_reconciliation.py        # Benchmark evaluator against master answer key
├── tests/                           # 13 Automated Unit Tests
│   ├── test_calculator.py
│   ├── test_extractor.py
│   ├── test_server.py
│   ├── test_treaty_agent.py
│   └── test_explainer_agent.py
├── data/
│   ├── raw/                         # Raw legal treaty contracts
│   ├── processed/                   # Claims CSV, BDX CSV, Answer Key JSON, Loss Run JSON
│   └── reports/                     # 25 Adjuster Loss Narrative Reports
└── docs/
    ├── RecoverIQ_Overview.html      # Interactive Visual Pitch & Architecture Deck
    ├── PROJECT_PITCH_SPEC.md        # Verbatim transcription of original pitch deck
    └── JUDGES_FEEDBACK_AND_ARCHITECTURE.md # Analysis of feedback from Sayan Ghosh
```

---

## 📄 License
Internal Prototype for **EXL AI Buildathon 2026**. Confidential and Proprietary.
