"""
QoE Simulator - Level 6: EQCR Partner Feedback Memo Generator.

Implements spec Section 8 (AICPA SQMS No. 1) and LP-09: a fully deterministic,
templated slot-filling memo generator. The quantitative score vector is pre-computed
by the rubric scorer; this module only synthesizes the human-readable narrative.
There are no stochastic LLM grading levers.
"""

from __future__ import annotations

from typing import Dict, List


class EQCRMemoGenerator:
    """Deterministic partner-grade feedback memo (temperature-equivalent = 0.0)."""

    def generate(self, engagement_id: str, user_id: str, partner_name: str,
                 scores: Dict[str, float], grade_letter: str,
                 critical_defects: List[str], strengths: List[str],
                 findings_by_quadrant=None, review_status="AUTOMATED ASSESSMENT") -> dict:
        displayed = scores.get("weighted_quadrant_scores", scores)
        maxima = (30.0, 25.0, 25.0, 20.0) if "weighted_quadrant_scores" in scores else (100.0,) * 4
        q1 = displayed["q1_investigative_rigor"]
        q2 = displayed["q2_modeling_hygiene"]
        q3 = displayed["q3_commercial_judgment"]
        q4 = displayed["q4_legal_protection"]
        composite = scores["composite_score"]

        groups = findings_by_quadrant or {1: critical_defects}
        memo = (
            f"ENGAGEMENT QUALITY CONTROL REVIEW (EQCR) MEMORANDUM — AUDIT RATING\n"
            f"{'=' * 80}\n"
            f"ENGAGEMENT: {engagement_id} | CANDIDATE: {user_id}\n"
            f"EVALUATOR: {partner_name}\n"
            f"BLIND PARTNER REVIEW: {review_status}\n"
            f"COMPOSITE GRADE: {composite} / 100 (GRADE: {grade_letter})\n\n"
            f"1. INVESTIGATIVE RIGOR (Score: {q1} / {maxima[0]}):\n"
            f"{self._bullets('STRENGTH', strengths[:2])}"
            f"{self._bullets('DEFECT', groups.get(1, []))}\n"
            f"2. MODELING HYGIENE & REPRODUCIBILITY (Score: {q2} / {maxima[1]}):\n"
            f"{self._bullets('STRENGTH', strengths[2:4])}"
            f"{self._bullets('DEFECT', groups.get(2, []))}\n"
            f"3. COMMERCIAL & VALUATION JUDGMENT (Score: {q3} / {maxima[2]}):\n"
            f"{self._bullets('STRENGTH', strengths[4:6])}"
            f"{self._bullets('DEFECT', groups.get(3, []))}\n"
            f"4. CONTRACTUAL & LEGAL PROTECTION (Score: {q4} / {maxima[3]}):\n"
            f"{self._bullets('STRENGTH', strengths[6:8])}"
            f"{self._bullets('DEFECT', groups.get(4, []))}\n"
        )

        return {
            "engagement_id": engagement_id,
            "evaluating_partner_name": partner_name,
            "overall_grade_letter": grade_letter,
            "scores": scores,
            "memo_markdown_text": memo,
            "critical_defects_summary": list(critical_defects),
            "commended_strengths_summary": list(strengths),
        }

    @staticmethod
    def _bullets(kind: str, items: List[str]) -> str:
        if not items:
            return ""
        sign = "[+]" if kind == "STRENGTH" else "[-]"
        return "".join(f"   {sign} {kind}: {item}\n" for item in items)
