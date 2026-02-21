"""
Early Warning Service - Critical case detection and alerts
"""
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.models.applicant import Applicant
from datetime import datetime, timedelta


class EarlyWarningService:
    """Service for early warning system and critical case detection."""

    def __init__(self, db: AsyncSession = None):
        self.db = db

    async def get_critical_cases(self) -> List[Dict[str, Any]]:
        """Get list of critical cases requiring attention."""
        if not self.db:
            return self._get_mock_critical_cases()

        critical_cases = []

        # Case 1: Long-pending applications (>30 days)
        thirty_days_ago = datetime.now() - timedelta(days=30)
        result = await self.db.execute(
            select(Applicant)
            .where(Applicant.status.in_(["submitted", "reviewing"]))
            .where(Applicant.created_at < thirty_days_ago)
        )

        for applicant in result.scalars():
            days_pending = (datetime.now() - applicant.created_at).days
            critical_cases.append({
                "type": "long_pending",
                "severity": "tinggi" if days_pending > 45 else "sederhana",
                "applicant_id": applicant.id,
                "applicant_name": applicant.name,
                "ic_number": applicant.ic_number,
                "days_pending": days_pending,
                "description": f"Permohonan masih belum selesai sejak {days_pending} hari",
                "recommended_action": "Semak dan proses dengan segera"
            })

        # Case 2: High fraud risk
        fraud_result = await self.db.execute(
            select(Applicant)
            .where(Applicant.is_fraud_detected == True)
            .where(Applicant.status.in_(["approved", "paid"]))
        )

        for applicant in fraud_result.scalars():
            critical_cases.append({
                "type": "fraud_risk",
                "severity": "tinggi",
                "applicant_id": applicant.id,
                "applicant_name": applicant.name,
                "ic_number": applicant.ic_number,
                "fraud_score": applicant.fraud_risk_score,
                "fraud_reasons": applicant.fraud_reasons,
                "description": "Risiko penipuan dikesan pada permohonan yang telah diluluskan",
                "recommended_action": "Semak semula kelulusan dan dokumentasi"
            })

        # Case 3: Very low income with large household
        low_income_result = await self.db.execute(
            select(Applicant)
            .where(Applicant.status == "approved")
            .where(Applicant.monthly_income < 300)
            .where(Applicant.household_size > 4)
        )

        for applicant in low_income_result.scalars():
            critical_cases.append({
                "type": "severe_poverty",
                "severity": "sederhana",
                "applicant_id": applicant.id,
                "applicant_name": applicant.name,
                "ic_number": applicant.ic_number,
                "monthly_income": applicant.monthly_income,
                "household_size": applicant.household_size,
                "description": f"Isi rumah {applicant.household_size} orang dengan pendapatan RM{applicant.monthly_income:.2f}",
                "recommended_action": "Pertimbangkan bantuan tambahan"
            })

        # Sort by severity
        severity_order = {"tinggi": 0, "sederhana": 1, "rendah": 2}
        critical_cases.sort(key=lambda x: severity_order.get(x["severity"], 2))

        return critical_cases

    async def get_warning_stats(self) -> Dict[str, Any]:
        """Get warning statistics."""
        if not self.db:
            return self._get_mock_warning_stats()

        critical_cases = await self.get_critical_cases()

        by_type = {}
        by_severity = {"tinggi": 0, "sederhana": 0, "rendah": 0}

        for case in critical_cases:
            case_type = case["type"]
            severity = case["severity"]

            by_type[case_type] = by_type.get(case_type, 0) + 1
            by_severity[severity] += 1

        return {
            "total_warnings": len(critical_cases),
            "by_type": by_type,
            "by_severity": by_severity,
            "generated_at": datetime.now().isoformat()
        }

    async def get_poverty_hotspots(self) -> List[Dict[str, Any]]:
        """Identify poverty hotspots based on approved applicants."""
        if not self.db:
            return self._get_mock_poverty_hotspots()

        # Get areas with high concentration of very low income applicants
        result = await self.db.execute(
            select(
                Applicant.state,
                Applicant.city,
                func.count(Applicant.id).label("count"),
                func.avg(Applicant.monthly_income).label("avg_income")
            )
            .where(Applicant.status == "approved")
            .where(Applicant.monthly_income < 500)
            .group_by(Applicant.state, Applicant.city)
            .having(func.count(Applicant.id) >= 5)
        )

        hotspots = []
        for row in result:
            avg_income = float(row[3] or 0)
            hotspot_score = (500 - avg_income) / 500 * 0.7 + min(row[2] / 50, 1) * 0.3

            hotspots.append({
                "state": row[0],
                "city": row[1],
                "applicant_count": row[2],
                "avg_income": avg_income,
                "hotspot_score": hotspot_score,
                "priority": " критич" if hotspot_score > 0.8 else "tinggi" if hotspot_score > 0.6 else "sederhana"
            })

        return sorted(hotspots, key=lambda x: x["hotspot_score"], reverse=True)[:10]

    def _get_mock_critical_cases(self) -> List[Dict[str, Any]]:
        """Return mock critical cases."""
        return [
            {
                "type": "long_pending",
                "severity": "tinggi",
                "applicant_id": 1,
                "applicant_name": "Ahmad bin Ali",
                "ic_number": "880101012345",
                "days_pending": 45,
                "description": "Permohonan masih belum selesai sejak 45 hari",
                "recommended_action": "Semak dan proses dengan segera"
            },
            {
                "type": "fraud_risk",
                "severity": "tinggi",
                "applicant_id": 2,
                "applicant_name": "Sarah bt Ahmad",
                "ic_number": "900202023456",
                "fraud_score": 0.85,
                "fraud_reasons": "Maklumat serupa dengan permohonan lain",
                "description": "Risiko penipuan dikesan",
                "recommended_action": "Semak semula kelulusan"
            }
        ]

    def _get_mock_warning_stats(self) -> Dict[str, Any]:
        """Return mock warning stats."""
        return {
            "total_warnings": 5,
            "by_type": {
                "long_pending": 3,
                "fraud_risk": 2
            },
            "by_severity": {
                "tinggi": 4,
                "sederhana": 1,
                "rendah": 0
            },
            "generated_at": datetime.now().isoformat()
        }

    def _get_mock_poverty_hotspots(self) -> List[Dict[str, Any]]:
        """Return mock poverty hotspots."""
        return [
            {"state": "WP Kuala Lumpur", "city": "Kuala Lumpur", "applicant_count": 50, "avg_income": 350, "priority": "kritikal"},
            {"state": "WP Kuala Lumpur", "city": "Kepong", "applicant_count": 30, "avg_income": 400, "priority": "tinggi"}
        ]