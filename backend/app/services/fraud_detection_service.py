"""
Fraud Detection Service - AI-powered duplicate and anomaly detection
"""
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.applicant import Applicant
from app.core.config import settings


class FraudDetectionService:
    """Service for detecting potential fraud in applications."""

    def __init__(self, db: AsyncSession = None):
        self.db = db
        self.similarity_threshold = settings.SIMILARITY_THRESHOLD

    async def detect_fraud(self, applicant: Applicant) -> Dict[str, Any]:
        """
        Detect potential fraud in an applicant application.
        Returns risk score and reasons for flags.
        """
        risk_score = 0.0
        reasons = []
        flags = []

        # Check 1: Duplicate IC number
        ic_check = await self._check_duplicate_ic(applicant)
        if ic_check["is_duplicate"]:
            risk_score += 0.5
            flags.append("duplicate_ic")
            reasons.append(f"Nombor IC telah digunakan sebelum (ID: {ic_check['existing_id']})")

        # Check 2: Similar personal details with different IC
        if self.db:
            similarity_check = await self._check_similarity(applicant)
            if similarity_check["has_similarity"]:
                risk_score += similarity_check["risk_score"]
                flags.extend(similarity_check["flags"])
                reasons.extend(similarity_check["reasons"])

        # Check 3: Unusual income pattern
        income_check = self._check_income_pattern(applicant)
        if income_check["is_suspicious"]:
            risk_score += income_check["risk_score"]
            flags.append("unusual_income")
            reasons.append(income_check["reason"])

        # Check 4: Address validation
        address_check = self._check_address(applicant)
        if address_check["is_suspicious"]:
            risk_score += address_check["risk_score"]
            flags.append("invalid_address")
            reasons.append(address_check["reason"])

        # Cap risk score at 1.0
        risk_score = min(risk_score, 1.0)

        return {
            "risk_score": risk_score,
            "is_fraud": risk_score >= 0.7,
            "flags": flags,
            "reasons": "; ".join(reasons) if reasons else "Tiada aktiviti mencurigakan dikesan"
        }

    async def _check_duplicate_ic(self, applicant: Applicant) -> Dict[str, Any]:
        """Check for duplicate IC numbers."""
        if not self.db:
            return {"is_duplicate": False}

        result = await self.db.execute(
            select(Applicant).where(
                Applicant.ic_number == applicant.ic_number,
                Applicant.id != applicant.id
            )
        )
        existing = result.scalars().first()

        if existing:
            return {
                "is_duplicate": True,
                "existing_id": existing.id,
                "existing_name": existing.name
            }

        return {"is_duplicate": False}

    async def _check_similarity(self, applicant: Applicant) -> Dict[str, Any]:
        """Check for similar applicants with different IC numbers."""
        result = await self.db.execute(
            select(Applicant).where(Applicant.id != applicant.id)
        )
        all_applicants = result.scalars().all()

        similar = []
        for existing in all_applicants:
            similarity = self._calculate_similarity(applicant, existing)
            if similarity > 0.7:
                similar.append({
                    "id": existing.id,
                    "name": existing.name,
                    "similarity": similarity
                })

        if not similar:
            return {"has_similarity": False}

        max_similarity = max(s["similarity"] for s in similar)

        return {
            "has_similarity": True,
            "risk_score": max_similarity * 0.3,
            "flags": ["similar_details"],
            "reasons": [
                f"Perincian serupa dengan permohonan lain (similarity: {max_similarity:.2f})"
            ]
        }

    def _calculate_similarity(self, a: Applicant, b: Applicant) -> float:
        """Calculate similarity between two applicants."""
        score = 0.0
        checks = 0

        # Name similarity
        if a.name and b.name:
            name_sim = self._string_similarity(a.name.lower(), b.name.lower())
            score += name_sim
            checks += 1

        # Phone similarity
        if a.phone and b.phone:
            if a.phone == b.phone:
                score += 1.0
            checks += 1

        # Address similarity
        if a.address and b.address:
            addr_sim = self._string_similarity(
                a.address.lower(),
                b.address.lower()
            )
            score += addr_sim
            checks += 1

        # City similarity
        if a.city and b.city:
            if a.city.lower() == b.city.lower():
                score += 1.0
            checks += 1

        return score / checks if checks > 0 else 0.0

    def _string_similarity(self, s1: str, s2: str) -> float:
        """Calculate string similarity using simple character overlap."""
        if not s1 or not s2:
            return 0.0

        # Simple Jaccard similarity on character bigrams
        def get_bigrams(s):
            return set(s[i:i+2] for i in range(len(s)-1))

        bigrams1 = get_bigrams(s1)
        bigrams2 = get_bigrams(s2)

        if not bigrams1 or not bigrams2:
            return 0.0

        intersection = bigrams1.intersection(bigrams2)
        union = bigrams1.union(bigrams2)

        return len(intersection) / len(union)

    def _check_income_pattern(self, applicant: Applicant) -> Dict[str, Any]:
        """Check for unusual income patterns."""
        # Zero income
        if applicant.monthly_income == 0:
            return {
                "is_suspicious": True,
                "risk_score": 0.2,
                "reason": "Pendapatan kosong"
            }

        # Very round numbers (potential fabrication)
        if applicant.monthly_income in [500, 1000, 1500, 2000, 3000]:
            return {
                "is_suspicious": True,
                "risk_score": 0.1,
                "reason": "Pendapatan dalam nombor bulat"
            }

        return {"is_suspicious": False}

    def _check_address(self, applicant: Applicant) -> Dict[str, Any]:
        """Validate address information."""
        # Check for missing address
        if not applicant.address or len(applicant.address) < 10:
            return {
                "is_suspicious": True,
                "risk_score": 0.2,
                "reason": "Alamat tidak lengkap"
            }

        # Check for placeholder addresses
        placeholder_words = ["test", "example", "dummy", "xxx", "na"]
        address_lower = applicant.address.lower()
        for word in placeholder_words:
            if word in address_lower:
                return {
                    "is_suspicious": True,
                    "risk_score": 0.5,
                    "reason": "Alamat mengandungi placeholder"
                }

        return {"is_suspicious": False}

    async def get_applicant_risk_profile(self, applicant: Applicant) -> Dict[str, Any]:
        """Get comprehensive risk profile for an applicant."""
        fraud_result = await self.detect_fraud(applicant)

        return {
            "applicant_id": applicant.id,
            "risk_score": fraud_result["risk_score"],
            "risk_level": self._get_risk_level(fraud_result["risk_score"]),
            "flags": fraud_result["flags"],
            "recommendations": self._get_recommendations(fraud_result["flags"])
        }

    def _get_risk_level(self, score: float) -> str:
        """Get risk level based on score."""
        if score >= 0.7:
            return "TINGGI"
        elif score >= 0.4:
            return "SEDERHANA"
        else:
            return "RENDAH"

    def _get_recommendations(self, flags: List[str]) -> List[str]:
        """Get recommendations based on flags."""
        recommendations = []

        if "duplicate_ic" in flags:
            recommendations.append("Semak semula nombor IC dan sejarah permohonan")

        if "similar_details" in flags:
            recommendations.append("Bandingkan dengan permohonan serupa")

        if "unusual_income" in flags:
            recommendations.append("Minta slip gaji atau bukti pendapatan")

        if "invalid_address" in flags:
            recommendations.append("Sila lengkapkan maklumat alamat")

        return recommendations