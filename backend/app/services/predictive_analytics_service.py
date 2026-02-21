"""
Predictive Analytics Service - Trend prediction and forecasting
"""
from typing import Dict, Any, List
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.applicant import Applicant
from app.models.payment import Payment
import json


class PredictiveAnalyticsService:
    """Service for predictive analytics and trend forecasting."""

    def __init__(self, db: AsyncSession = None):
        self.db = db

    async def get_regional_forecast(self, region: str = None) -> Dict[str, Any]:
        """Predict future assistance needs by region."""
        if not self.db:
            return self._get_mock_forecast()

        # Get current statistics by region/state
        query = select(
            Applicant.state,
            func.count(Applicant.id).label("total"),
            func.sum(
                func.case(
                    (Applicant.status == "approved", 1),
                    else_=0
                )
            ).label("approved"),
            func.avg(Applicant.monthly_income).label("avg_income")
        )

        if region:
            query = query.where(Applicant.state == region)

        query = query.group_by(Applicant.state)
        result = await self.db.execute(query)

        regional_data = []
        for row in result:
            approved_rate = row.approved / row.total if row.total > 0 else 0
            regional_data.append({
                "state": row.state,
                "total_applicants": row.total,
                "approved_count": row.approved,
                "approval_rate": approved_rate,
                "avg_income": float(row.avg_income or 0)
            })

        # Generate forecast
        forecast = self._generate_forecast(regional_data)

        return {
            "current_data": regional_data,
            "forecast": forecast,
            "generated_at": datetime.now().isoformat()
        }

    def _generate_forecast(self, data: List[Dict]) -> List[Dict]:
        """Generate simple forecast based on current trends."""
        forecast = []
        current_date = datetime.now()

        for month_offset in range(1, 7):  # 6 month forecast
            forecast_date = current_date + timedelta(days=30 * month_offset)
            month_name = forecast_date.strftime("%B %Y")

            # Simple linear projection with growth factor
            projected_data = []
            for region in data:
                # Add slight growth based on historical patterns
                growth_factor = 1 + (month_offset * 0.02)
                projected = {
                    "state": region["state"],
                    "projected_applicants": int(region["total_applicants"] * growth_factor),
                    "projected_approved": int(region["approved_count"] * growth_factor),
                    "confidence": max(0.5, 0.9 - (month_offset * 0.08))
                }
                projected_data.append(projected)

            forecast.append({
                "month": month_name,
                "regions": projected_data
            })

        return forecast

    def _get_mock_forecast(self) -> Dict[str, Any]:
        """Return mock forecast data when database is not available."""
        return {
            "current_data": [
                {"state": "WP Kuala Lumpur", "total_applicants": 1500, "approved_count": 900, "approval_rate": 0.6},
                {"state": "WP Putrajaya", "total_applicants": 200, "approved_count": 120, "approval_rate": 0.6},
                {"state": "WP Labuan", "total_applicants": 100, "approved_count": 60, "approval_rate": 0.6}
            ],
            "forecast": [
                {
                    "month": "March 2026",
                    "regions": [
                        {"state": "WP Kuala Lumpur", "projected_applicants": 1530, "confidence": 0.9},
                        {"state": "WP Putrajaya", "projected_applicants": 204, "confidence": 0.9},
                        {"state": "WP Labuan", "projected_applicants": 102, "confidence": 0.9}
                    ]
                }
            ],
            "generated_at": datetime.now().isoformat()
        }

    async def get_poverty_trends(self) -> Dict[str, Any]:
        """Analyze poverty trends over time."""
        if not self.db:
            return self._get_mock_trends()

        # Get monthly application trends
        result = await self.db.execute(
            select(
                func.date_trunc('month', Applicant.created_at).label("month"),
                func.count(Applicant.id).label("count"),
                func.avg(Applicant.monthly_income).label("avg_income")
            )
            .group_by(func.date_trunc('month', Applicant.created_at))
            .order_by(func.date_trunc('month', Applicant.created_at))
        )

        monthly_data = []
        for row in result:
            monthly_data.append({
                "month": row.month.isoformat() if row.month else None,
                "applicants": row.count,
                "avg_income": float(row.avg_income or 0)
            })

        return {
            "monthly_trends": monthly_data,
            "analysis": self._analyze_trends(monthly_data)
        }

    def _analyze_trends(self, data: List[Dict]) -> Dict[str, Any]:
        """Analyze trend patterns."""
        if len(data) < 2:
            return {"trend": "insufficient_data"}

        # Calculate simple trend
        first_half = data[:len(data)//2]
        second_half = data[len(data)//2:]

        first_avg = sum(d["applicants"] for d in first_half) / len(first_half)
        second_avg = sum(d["applicants"] for d in second_half) / len(second_half)

        change = (second_avg - first_avg) / first_avg if first_avg > 0 else 0

        return {
            "trend": "increasing" if change > 0.1 else "decreasing" if change < -0.1 else "stable",
            "change_percentage": change * 100,
            "insights": self._generate_insights(change)
        }

    def _generate_insights(self, change: float) -> List[str]:
        """Generate insights based on trend."""
        insights = []

        if change > 0.2:
            insights.append("Terdapat peningkatan ketara dalam permohonan bantuan")
            insights.append("Disyorkan untuk menambah sumber untuk pemprosesan")
        elif change > 0.1:
            insights.append("Permohonan menunjukkan peningkatan sederhana")
        elif change < -0.2:
            insights.append("Permohonan menunjukkan penurunan ketara")
            insights.append("Keberkesanan program bantuan mungkin meningkat")
        else:
            insights.append("Permohonan adalah stabil")

        return insights

    def _get_mock_trends(self) -> Dict[str, Any]:
        """Return mock trend data."""
        return {
            "monthly_trends": [
                {"month": "2025-08-01", "applicants": 120, "avg_income": 850},
                {"month": "2025-09-01", "applicants": 135, "avg_income": 820},
                {"month": "2025-10-01", "applicants": 150, "avg_income": 790},
                {"month": "2025-11-01", "applicants": 145, "avg_income": 810},
                {"month": "2025-12-01", "applicants": 160, "avg_income": 780},
                {"month": "2026-01-01", "applicants": 175, "avg_income": 760}
            ],
            "analysis": {
                "trend": "increasing",
                "change_percentage": 15.5,
                "insights": [
                    "Terdapat peningkatan ketara dalam permohonan bantuan",
                    "Disyorkan untuk menambah sumber untuk pemprosesan"
                ]
            }
        }

    async def get_demographic_analysis(self) -> Dict[str, Any]:
        """Analyze applicant demographics."""
        if not self.db:
            return self._get_mock_demographics()

        # By asnaf category
        category_result = await self.db.execute(
            select(
                Applicant.asnaf_category,
                func.count(Applicant.id).label("count")
            )
            .group_by(Applicant.asnaf_category)
        )

        by_category = [
            {"category": row[0], "count": row[1]}
            for row in category_result if row[0]
        ]

        # By income bracket
        income_brackets = [
            ("Bawah RM500", 0, 500),
            ("RM500 - RM800", 500, 800),
            ("RM800 - RM1000", 800, 1000),
            ("RM1000 - RM1169", 1000, 1169),
            ("RM1169 ke atas", 1169, 999999)
        ]

        by_income = []
        for bracket_name, min_income, max_income in income_brackets:
            result = await self.db.execute(
                select(func.count(Applicant.id))
                .where(
                    Applicant.monthly_income >= min_income,
                    Applicant.monthly_income < max_income
                )
            )
            count = result.scalar()
            by_income.append({"bracket": bracket_name, "count": count})

        return {
            "by_asnaf_category": by_category,
            "by_income_bracket": by_income,
            "generated_at": datetime.now().isoformat()
        }

    def _get_mock_demographics(self) -> Dict[str, Any]:
        """Return mock demographic data."""
        return {
            "by_asnaf_category": [
                {"category": "fakir", "count": 450},
                {"category": "miskin", "count": 300},
                {"category": "muallaf", "count": 50}
            ],
            "by_income_bracket": [
                {"bracket": "Bawah RM500", "count": 200},
                {"bracket": "RM500 - RM800", "count": 350},
                {"bracket": "RM800 - RM1000", "count": 150},
                {"bracket": "RM1000 - RM1169", "count": 80},
                {"bracket": "RM1169 ke atas", "count": 20}
            ],
            "generated_at": datetime.now().isoformat()
        }