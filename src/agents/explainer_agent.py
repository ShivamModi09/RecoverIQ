"""
RecoverIQ — Reconciliation Explanation Agent (Agent B)
Generates adjuster-grade Proof-of-Loss and Reinsurance Recovery Demand Briefs
using Groq LLM (GPT-OSS 120B) based on verified deterministic calculation proofs.
"""

from typing import Dict, Any, Optional
import json
from src.agents.groq_client import GroqClient

SYSTEM_PROMPT = """You are the RecoverIQ Audit & Legal Explanation Agent, an expert in commercial reinsurance claims advocacy.
Your task is to analyze an identified reinsurance recovery leakage and synthesize a formal, adjuster-grade "Reinsurance Ceded Loss Notice & Billing Demand Brief".

The brief is presented to the reinsurance broker (e.g. Aon, Guy Carpenter) and lead underwriting syndicate to demand recovery of unbilled or under-billed funds.

You MUST respond strictly with a valid JSON object matching this schema:
{
  "notice_reference": "string",
  "subject_claim_id": "string",
  "treaty_id": "string",
  "executive_summary": "concise 2-sentence summary of the leakage and opportunity",
  "contract_legal_basis": "detailed explanation of applicable treaty articles and page citations",
  "calculation_audit_trail": "step-by-step mathematical demonstration showing retention, excess, and entitled amount",
  "broker_reconciliation_finding": "explanation of variance between billed amount and broker bordereau remittance",
  "formal_recovery_demand": "formal demand text specifying the exact dollar amount due immediately"
}
Do not hallucinate dollar amounts. Strictly use the exact verified figures provided in the prompt.
"""

class ReconciliationExplainerAgent:

    def __init__(self, groq_client: Optional[GroqClient] = None):
        self.client = groq_client or GroqClient()

    def generate_audit_brief(self, finding: Dict[str, Any]) -> Dict[str, Any]:
        """
        Synthesizes a formal audit brief and billing notice using Groq LLM.
        """
        user_prompt = f"""Generate a formal Reinsurance Ceded Loss Notice & Billing Demand Brief based on this verified finding:
Claim ID: {finding['claim_id']}
Insured Name: {finding['insured_name']}
Location: {finding['location']}
Event ID: {finding['event_id']}
Peril: {finding['peril']}
Treaty ID: {finding['treaty_id']}
Gross Incurred Loss: ${finding['gross_loss']:,.2f}
Calculated Entitled Recoverable: ${finding['entitled_recoverable']:,.2f}
Actually Billed to Date: ${finding['actually_billed']:,.2f}
Broker BDX Remitted: ${finding['actually_received']:,.2f}
Net Leakage / Owed Amount: ${finding['leakage_amount']:,.2f}
Classification: {finding['leakage_category']}
Treaty Retention Page: {finding.get('citation', {}).get('retention_page')}
Treaty Limit Page: {finding.get('citation', {}).get('limit_page')}
Treaty Perils Page: {finding.get('citation', {}).get('perils_page')}
Calculation Steps: {json.dumps(finding.get('calculation_steps', []))}
"""
        resp = self.client.chat_completion(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
            json_mode=True
        )

        if resp["success"] and resp["content"]:
            data = resp["content"]
            data["generated_by"] = "Groq LLM Agent (openai/gpt-oss-120b)"
            data["model_usage"] = resp.get("usage", {})
            return data

        # Fallback template if LLM is offline
        return {
            "notice_reference": f"RECOV-DEMAND-{finding['claim_id']}",
            "subject_claim_id": finding["claim_id"],
            "treaty_id": finding["treaty_id"],
            "executive_summary": f"Audit of Claim {finding['claim_id']} identified ${finding['leakage_amount']:,.2f} in unbilled recovery under treaty {finding['treaty_id']}.",
            "contract_legal_basis": f"Pursuant to Article IV (Page {finding.get('citation', {}).get('retention_page', 'N/A')}) of treaty {finding['treaty_id']}.",
            "calculation_audit_trail": " -> ".join(finding.get("calculation_steps", [])),
            "broker_reconciliation_finding": f"Insurer billed ${finding['actually_billed']:,.2f}; Broker BDX shows ${finding['actually_received']:,.2f}.",
            "formal_recovery_demand": f"Demand is hereby submitted for immediate remittance of USD ${finding['leakage_amount']:,.2f}.",
            "generated_by": "Deterministic Fallback Template"
        }

