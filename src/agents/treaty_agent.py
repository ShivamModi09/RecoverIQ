"""
RecoverIQ — Treaty Policy Intelligence Agent (Agent A)
Uses Groq LLM (GPT-OSS 120B) with Structured Output to extract complex
reinsurance contract terms, limits, retentions, perils, and page citations.
"""

from typing import Dict, Any, Optional
import json
from src.agents.groq_client import GroqClient
from src.extractor import DocumentExtractor

SYSTEM_PROMPT = """You are the RecoverIQ Treaty Policy Intelligence Agent, an expert in commercial reinsurance law and underwriting.
Your task is to analyze the full text of a reinsurance treaty agreement and extract structured underwriting parameters with exact page number citations.

You MUST respond strictly with a valid JSON object matching this schema:
{
  "treaty_id": "string",
  "treaty_name": "string",
  "type": "string",
  "retention_usd": float,
  "citation_page_retention": int,
  "limit_usd": float,
  "citation_page_limit": int,
  "covered_perils": ["string"],
  "excluded_perils": ["string"],
  "citation_page_perils": int,
  "hours_clause": int,
  "citation_page_hours": int,
  "clause_excerpt_retention": "exact quote from contract",
  "clause_excerpt_perils": "exact quote from contract"
}
Do not add conversational commentary. Return ONLY the JSON object.
"""

class TreatyIntelligenceAgent:

    def __init__(self, groq_client: Optional[GroqClient] = None):
        self.client = groq_client or GroqClient()

    def analyze_treaty(self, treaty_text: str) -> Dict[str, Any]:
        """
        Extracts structured treaty parameters using Groq LLM.
        Falls back to rule-based extractor if LLM is unreachable.
        """
        user_prompt = f"Analyze this reinsurance treaty contract and extract all parameters:\n\n{treaty_text}"
        
        resp = self.client.chat_completion(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
            json_mode=True
        )

        if resp["success"] and resp["content"]:
            data = resp["content"]
            data["extracted_by"] = "Groq LLM Agent (openai/gpt-oss-120b)"
            data["model_usage"] = resp.get("usage", {})
            return data

        # Fallback to local rule extractor if LLM network call fails
        fallback_data = DocumentExtractor.extract_treaty(treaty_text)
        fallback_data["extracted_by"] = "Deterministic Rule Fallback"
        fallback_data["error"] = resp.get("error")
        return fallback_data

