"""
Eligibility Service - AI-powered eligibility scoring for Zakat applicants
"""
from typing import Dict, Any
from app.models.applicant import Applicant
from app.core.config import settings


class EligibilityService:
    """Service for assessing applicant eligibility for Zakat assistance."""

    def __init__(self, db=None):
        self.db = db
        self.threshold = settings.ELIGIBILITY_THRESHOLD

    async def assess_eligibility(self, applicant: Applicant) -> Dict[str, Any]:
        """
        Assess applicant eligibility using multiple factors.
        Returns a score between 0 and 1, and reasons for the assessment.
        """
        score = 0.0
        reasons = []

        # Factor 1: Monthly income (lower is better for eligibility)
        income_score = self._calculate_income_score(applicant.monthly_income)
        score += income_score * 0.4  # 40% weight

        if income_score > 0.7:
            reasons.append(f"Pendapatan bulanan RM{applicant.monthly_income:.2f} adalah di bawah paras kelayakan")
        elif income_score > 0.4:
            reasons.append(f"Pendapatan bulanan RM{applicant.monthly_income:.2f} adalah sederhana")

        # Factor 2: Household income per person
        household_income = applicant.monthly_income
        if applicant.household_size > 0:
            income_per_person = household_income / applicant.household_size
        else:
            income_per_person = household_income

        if income_per_person < 400:
            reasons.append(f"RM{income_per_person:.2f} per ahli adalah sangat rendah")
            score += 0.3
        elif income_per_person < 700:
            reasons.append(f"RM{income_per_person:.2f} per ahli adalah rendah")
            score += 0.2
        else:
            score += 0.0

        # Factor 3: Household size (larger families with low income get higher scores)
        household_score = self._calculate_household_score(
            applicant.household_size,
            applicant.monthly_income
        )
        score += household_score * 0.2  # 20% weight

        if household_score > 0.5:
            reasons.append(f"Isi rumah {applicant.household_size} orang dengan pendapatan rendah")

        # Factor 4: Employment status
        employment_score = self._calculate_employment_score(applicant.occupation)
        score += employment_score * 0.1  # 10% weight

        # Normalize score to 0-1 range
        score = min(max(score, 0.0), 1.0)

        return {
            "score": score,
            "is_eligible": score >= self.threshold,
            "reasons": "; ".join(reasons) if reasons else "Tiada faktor khusus dikenal pasti"
        }

    def _calculate_income_score(self, monthly_income: float) -> float:
        """Calculate score based on monthly income."""
        # Below RM500 = very low income (high eligibility)
        if monthly_income < 500:
            return 1.0
        # RM500-800 = low income
        elif monthly_income < 800:
            return 0.8
        # RM800-1000 = below average
        elif monthly_income < 1000:
            return 0.6
        # RM1000-1169 = at poverty line (eligibility threshold)
        elif monthly_income < 1169:
            return 0.4
        # Above poverty line
        else:
            return 0.0

    def _calculate_household_score(self, household_size: int, income: float) -> float:
        """Calculate score based on household size and income."""
        if household_size == 0:
            return 0.0

        income_per_person = income / household_size

        # Large families with low per-person income get higher scores
        if income_per_person < 300:
            return 1.0
        elif income_per_person < 500:
            return 0.8
        elif income_per_person < 700:
            return 0.5
        else:
            return 0.2

    def _calculate_employment_score(self, occupation: str) -> float:
        """Calculate score based on employment status."""
        if not occupation:
            return 0.5  # Unknown employment

        occupation_lower = occupation.lower()

        # No income or very low paying jobs
        unemployed_indicators = [
            "tiada", "tidak bekerja", " unemployed", "tidak bekerja",
            "surat rumah", "pencen", "okupasi rumah"
        ]

        for indicator in unemployed_indicators:
            if indicator in occupation_lower:
                return 1.0

        return 0.3

    async def get_eligibility_breakdown(self, applicant: Applicant) -> Dict[str, Any]:
        """Get detailed breakdown of eligibility factors."""
        return {
            "income": {
                "value": applicant.monthly_income,
                "score": self._calculate_income_score(applicant.monthly_income),
                "weight": 0.4
            },
            "income_per_person": {
                "value": applicant.monthly_income / max(applicant.household_size, 1),
                "weight": 0.3
            },
            "household": {
                "size": applicant.household_size,
                "score": self._calculate_household_score(
                    applicant.household_size,
                    applicant.monthly_income
                ),
                "weight": 0.2
            },
            "employment": {
                "occupation": applicant.occupation,
                "score": self._calculate_employment_score(applicant.occupation),
                "weight": 0.1
            }
        }