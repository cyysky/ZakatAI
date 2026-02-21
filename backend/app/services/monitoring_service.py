"""
Monitoring Service - Real-time applicant status monitoring
"""
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.applicant import Applicant
from app.models.payment import Payment
from datetime import datetime, timedelta


class MonitoringService:
    """Service for real-time monitoring of applicants and payments."""

    def __init__(self, db: AsyncSession = None):
        self.db = db

    async def get_dashboard_summary(self) -> Dict[str, Any]:
        """Get summary statistics for dashboard."""
        if not self.db:
            return self._get_mock_summary()

        # Total applicants
        total_result = await self.db.execute(
            select(func.count(Applicant.id))
        )
        total_applicants = total_result.scalar()

        # By status
        status_result = await self.db.execute(
            select(
                Applicant.status,
                func.count(Applicant.id).label("count")
            )
            .group_by(Applicant.status)
        )

        by_status = {row[0]: row[1] for row in status_result}

        # Recent applications (last 7 days)
        week_ago = datetime.now() - timedelta(days=7)
        recent_result = await self.db.execute(
            select(func.count(Applicant.id))
            .where(Applicant.created_at >= week_ago)
        )
        recent_applications = recent_result.scalar()

        # Pending payments
        pending_result = await self.db.execute(
            select(func.count(Payment.id))
            .where(Payment.status == "pending")
        )
        pending_payments = pending_result.scalar()

        # Average processing time (mock for now)
        avg_processing_days = 14

        # Fraud alerts
        fraud_result = await self.db.execute(
            select(func.count(Applicant.id))
            .where(Applicant.is_fraud_detected == True)
        )
        fraud_alerts = fraud_result.scalar()

        return {
            "total_applicants": total_applicants,
            "by_status": by_status,
            "recent_applications": recent_applications,
            "pending_payments": pending_payments,
            "avg_processing_days": avg_processing_days,
            "fraud_alerts": fraud_alerts,
            "generated_at": datetime.now().isoformat()
        }

    async def get_recent_applicants(
        self,
        limit: int = 10,
        status: str = None
    ) -> List[Applicant]:
        """Get recent applicants."""
        if not self.db:
            return []

        query = select(Applicant).order_by(Applicant.created_at.desc())

        if status:
            query = query.where(Applicant.status == status)

        query = query.limit(limit)
        result = await self.db.execute(query)

        return result.scalars().all()

    async def get_applicants_by_status(self) -> Dict[str, int]:
        """Get count of applicants by status."""
        if not self.db:
            return {"draft": 0, "submitted": 0, "reviewing": 0, "approved": 0, "rejected": 0, "paid": 0}

        result = await self.db.execute(
            select(Applicant.status, func.count(Applicant.id))
            .group_by(Applicant.status)
        )

        return {row[0]: row[1] for row in result}

    async def get_asnaf_distribution(self) -> List[Dict[str, Any]]:
        """Get distribution of asnaf categories."""
        if not self.db:
            return [
                {"category": "fakir", "count": 450},
                {"category": "miskin", "count": 300},
                {"category": "muallaf", "count": 50}
            ]

        result = await self.db.execute(
            select(
                Applicant.asnaf_category,
                func.count(Applicant.id).label("count")
            )
            .where(Applicant.asnaf_category != None)
            .group_by(Applicant.asnaf_category)
        )

        return [
            {"category": row[0], "count": row[1]}
            for row in result
        ]

    async def get_monthly_trends(self, months: int = 6) -> List[Dict[str, Any]]:
        """Get monthly application trends."""
        if not self.db:
            return []

        trends = []
        for i in range(months):
            month_date = datetime.now() - timedelta(days=30 * i)
            month_start = month_date.replace(day=1, hour=0, minute=0, second=0)

            if i == months - 1:
                month_end = month_date.replace(day=1, hour=0, minute=0, second=0)
            else:
                next_month = month_date.replace(day=1, hour=0, minute=0, second=0) + timedelta(days=32)
                month_end = next_month.replace(day=1)

            result = await self.db.execute(
                select(func.count(Applicant.id))
                .where(Applicant.created_at >= month_start)
                .where(Applicant.created_at < month_end)
            )

            count = result.scalar()

            trends.append({
                "month": month_start.strftime("%B %Y"),
                "applications": count
            })

        return list(reversed(trends))

    def _get_mock_summary(self) -> Dict[str, Any]:
        """Return mock summary when database is not available."""
        return {
            "total_applicants": 800,
            "by_status": {
                "draft": 50,
                "submitted": 150,
                "reviewing": 100,
                "approved": 350,
                "rejected": 100,
                "paid": 50
            },
            "recent_applications": 120,
            "pending_payments": 25,
            "avg_processing_days": 14,
            "fraud_alerts": 5,
            "generated_at": datetime.now().isoformat()
        }