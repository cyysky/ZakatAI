"""
Geospatial Service - Geographic mapping and analysis
"""
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.applicant import Applicant


class GeospatialService:
    """Service for geographic mapping and analysis."""

    def __init__(self, db: AsyncSession = None):
        self.db = db

    async def get_applicants_by_region(self) -> List[Dict[str, Any]]:
        """Get applicant counts by region/state."""
        if not self.db:
            return self._get_mock_regions()

        result = await self.db.execute(
            select(
                Applicant.state,
                Applicant.city,
                func.count(Applicant.id).label("count")
            )
            .where(Applicant.state != None)
            .group_by(Applicant.state, Applicant.city)
            .order_by(Applicant.state, Applicant.city)
        )

        regions = []
        current_state = None
        state_data = None

        for row in result:
            if row[0] != current_state:
                if state_data:
                    regions.append(state_data)
                current_state = row[0]
                state_data = {
                    "state": row[0],
                    "cities": []
                }

            state_data["cities"].append({
                "city": row[1],
                "count": row[2]
            })

        if state_data:
            regions.append(state_data)

        return regions

    async def get_priority_areas(self) -> List[Dict[str, Any]]:
        """Identify high-priority areas based on need."""
        if not self.db:
            return self._get_mock_priority_areas()

        # Areas with highest concentration of approved applicants
        result = await self.db.execute(
            select(
                Applicant.state,
                Applicant.city,
                func.count(Applicant.id).label("total"),
                func.sum(
                    func.case(
                        (Applicant.status.in_(["approved", "paid"]), 1),
                        else_=0
                    )
                ).label("approved")
            )
            .where(Applicant.state != None)
            .group_by(Applicant.state, Applicant.city)
        )

        areas = []
        for row in result:
            approved = row[2] or 0
            total = row[3] or 0

            if total > 0:
                approval_rate = approved / total

                # Calculate priority score based on approval rate and count
                priority_score = (approval_rate * 0.7) + (min(total / 100, 1) * 0.3)

                areas.append({
                    "state": row[0],
                    "city": row[1],
                    "total_applicants": total,
                    "approved": approved,
                    "approval_rate": approval_rate,
                    "priority_score": priority_score,
                    "priority_level": self._get_priority_level(priority_score)
                })

        # Sort by priority score
        areas.sort(key=lambda x: x["priority_score"], reverse=True)

        return areas[:10]  # Top 10 priority areas

    def _get_priority_level(self, score: float) -> str:
        """Determine priority level based on score."""
        if score >= 0.8:
            return "Sangat Tinggi"
        elif score >= 0.6:
            return "Tinggi"
        elif score >= 0.4:
            return "Sederhana"
        else:
            return "Rendah"

    async def get_geo_distribution(self) -> Dict[str, Any]:
        """Get geographic distribution of applicants with coordinates."""
        if not self.db:
            return self._get_mock_geo_distribution()

        result = await self.db.execute(
            select(Applicant)
            .where(Applicant.latitude != None)
            .where(Applicant.longitude != None)
            .limit(100)
        )

        points = []
        for applicant in result.scalars():
            points.append({
                "id": applicant.id,
                "name": applicant.name,
                "lat": applicant.latitude,
                "lng": applicant.longitude,
                "status": applicant.status,
                "asnaf_category": applicant.asnaf_category,
                "monthly_income": applicant.monthly_income
            })

        return {
            "points": points,
            "count": len(points)
        }

    def _get_mock_regions(self) -> List[Dict[str, Any]]:
        """Return mock region data."""
        return [
            {
                "state": "WP Kuala Lumpur",
                "cities": [
                    {"city": "Kuala Lumpur", "count": 500},
                    {"city": "Setiawangsa", "count": 150},
                    {"city": "Kepong", "count": 100}
                ]
            },
            {
                "state": "WP Putrajaya",
                "cities": [
                    {"city": "Putrajaya", "count": 200}
                ]
            },
            {
                "state": "WP Labuan",
                "cities": [
                    {"city": "Labuan", "count": 100}
                ]
            }
        ]

    def _get_mock_priority_areas(self) -> List[Dict[str, Any]]:
        """Return mock priority areas."""
        return [
            {"state": "WP Kuala Lumpur", "city": "Kuala Lumpur", "total_applicants": 500, "approved": 300, "priority_level": "Sangat Tinggi"},
            {"state": "WP Kuala Lumpur", "city": "Setiawangsa", "total_applicants": 150, "approved": 90, "priority_level": "Tinggi"},
            {"state": "WP Putrajaya", "city": "Putrajaya", "total_applicants": 200, "approved": 120, "priority_level": "Tinggi"}
        ]

    def _get_mock_geo_distribution(self) -> Dict[str, Any]:
        """Return mock geo distribution."""
        return {
            "points": [
                {"id": 1, "name": "Ahmed", "lat": 3.1390, "lng": 101.6869, "status": "approved", "asnaf_category": "fakir", "monthly_income": 400},
                {"id": 2, "name": "Sarah", "lat": 3.1395, "lng": 101.6875, "status": "reviewing", "asnaf_category": "miskin", "monthly_income": 800}
            ],
            "count": 2
        }