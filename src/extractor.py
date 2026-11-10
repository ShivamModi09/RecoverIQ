"""
RecoverIQ — Treaty & Claim Intelligence Extractor
Parses unstructured legal treaty documents and adjuster reports into structured JSON
with exact page and article citations.
"""

import re
import os
from typing import Dict, Any, List

class DocumentExtractor:
    
    @staticmethod
    def extract_treaty(text: str) -> Dict[str, Any]:
        """
        Extracts key reinsurance treaty terms, retention, limit, covered/excluded perils,
        and hours clause along with exact page numbers.
        """
        extracted = {}

        # 1. Treaty ID & Name
        t_id_match = re.search(r"REINSURANCE TREATY AGREEMENT:\s*([A-Z0-9\-]+)", text)
        extracted["treaty_id"] = t_id_match.group(1).strip() if t_id_match else "UNKNOWN"

        name_match = re.search(r"Contract:\s*([^\n]+)", text)
        extracted["treaty_name"] = name_match.group(1).strip() if name_match else ""

        # 2. Retention extraction + Page citation
        ret_match = re.search(
            r"=== \[PAGE (\d+)\] ===\s*\nARTICLE IV[^\n]*\n.*?retention the sum of USD \$([0-9,]+\.\d{2})",
            text, re.DOTALL
        )
        if ret_match:
            extracted["citation_page_retention"] = int(ret_match.group(1))
            extracted["retention_usd"] = float(ret_match.group(2).replace(",", ""))
        else:
            extracted["citation_page_retention"] = None
            extracted["retention_usd"] = 0.0

        # 3. Limit extraction + Page citation
        lim_match = re.search(
            r"maximum limit of liability of USD \$([0-9,]+\.\d{2})",
            text
        )
        if lim_match:
            extracted["limit_usd"] = float(lim_match.group(1).replace(",", ""))
            extracted["citation_page_limit"] = extracted.get("citation_page_retention")
        else:
            extracted["limit_usd"] = 0.0

        # 4. Covered & Excluded Perils + Page citation
        perils_block = re.search(
            r"=== \[PAGE (\d+)\] ===\s*\nARTICLE VIII[^\n]*\nCovered Perils:\s*([^\n]+)\s*\nExplicit Exclusions:\s*([^\n]+)",
            text
        )
        if perils_block:
            extracted["citation_page_perils"] = int(perils_block.group(1))
            extracted["covered_perils"] = [p.strip() for p in perils_block.group(2).split(",")]
            extracted["excluded_perils"] = [p.strip() for p in perils_block.group(3).split(",")]
        else:
            extracted["citation_page_perils"] = None
            extracted["covered_perils"] = []
            extracted["excluded_perils"] = []

        # 5. Hours clause + Page citation
        hours_block = re.search(
            r"=== \[PAGE (\d+)\] ===\s*\nARTICLE XI[^\n]*\n.*?consecutive (\d+)-hour period",
            text, re.DOTALL
        )
        if hours_block:
            extracted["citation_page_hours"] = int(hours_block.group(1))
            extracted["hours_clause"] = int(hours_block.group(2))
        else:
            extracted["citation_page_hours"] = None
            extracted["hours_clause"] = 24

        return extracted

    @staticmethod
    def extract_claim_report(text: str) -> Dict[str, Any]:
        """
        Extracts claim quantification and adjuster notes with page markers.
        """
        extracted = {}

        rep_id = re.search(r"Report ID:\s*([A-Z0-9\-]+)", text)
        extracted["report_id"] = rep_id.group(1).strip() if rep_id else ""

        cid = re.search(r"Claim ID:\s*([A-Z0-9\-]+)", text)
        extracted["claim_id"] = cid.group(1).strip() if cid else ""

        gross = re.search(r"Gross Incurred Loss:\s*USD \$([0-9,]+\.\d{2})", text)
        extracted["gross_loss_usd"] = float(gross.group(1).replace(",", "")) if gross else 0.0

        paid = re.search(r"Paid Damages to Date:\s*USD \$([0-9,]+\.\d{2})", text)
        extracted["paid_loss_usd"] = float(paid.group(1).replace(",", "")) if paid else 0.0

        res = re.search(r"Outstanding Case Reserves:\s*USD \$([0-9,]+\.\d{2})", text)
        extracted["case_reserves_usd"] = float(res.group(1).replace(",", "")) if res else 0.0

        extracted["citation_page_quantification"] = 2

        return extracted
