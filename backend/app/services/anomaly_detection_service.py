"""
Anomaly Detection Service - Transaction anomaly detection
"""
from typing import Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.payment import Payment
import statistics


class AnomalyDetectionService:
    """Service for detecting anomalies in transactions."""

    def __init__(self, db: AsyncSession = None):
        self.db = db

    async def detect_anomaly(self, payment: Payment) -> Dict[str, Any]:
        """Detect if a payment has anomalous patterns."""
        if not self.db:
            return self._get_mock_anomaly_check(payment)

        risk_score = 0.0
        reasons = []
        flags = []

        # Check 1: Amount vs average
        amount_check = await self._check_amount_anomaly(payment)
        risk_score += amount_check["risk_score"]
        if amount_check["is_anomaly"]:
            flags.append("unusual_amount")
            reasons.append(amount_check["reason"])

        # Check 2: Payment frequency
        frequency_check = await self._check_payment_frequency(payment)
        risk_score += frequency_check["risk_score"]
        if frequency_check["is_anomaly"]:
            flags.append("high_frequency")
            reasons.append(frequency_check["reason"])

        # Check 3: Unusual timing
        timing_check = self._check_timing_anomaly(payment)
        risk_score += timing_check["risk_score"]
        if timing_check["is_anomaly"]:
            flags.append("unusual_timing")
            reasons.append(timing_check["reason"])

        # Check 4: Duplicate payment reference
        if payment.transaction_id:
            dup_check = await self._check_duplicate_transaction(payment)
            risk_score += dup_check["risk_score"]
            if dup_check["is_duplicate"]:
                flags.append("duplicate_transaction")
                reasons.append(dup_check["reason"])

        risk_score = min(risk_score, 1.0)

        return {
            "is_anomaly": risk_score >= 0.6,
            "risk_score": risk_score,
            "anomaly_reason": "; ".join(reasons) if reasons else "Tiada anomali dikesan",
            "confidence_score": 0.85,
            "flags": flags
        }

    async def _check_amount_anomaly(self, payment: Payment) -> Dict[str, Any]:
        """Check if payment amount is unusual."""
        # Get all payments for this applicant
        result = await self.db.execute(
            select(Payment.amount)
            .where(Payment.applicant_id == payment.applicant_id)
            .where(Payment.id != payment.id)
        )
        amounts = [row[0] for row in result]

        if not amounts:
            # No previous payments - check against global average
            global_result = await self.db.execute(
                select(func.avg(Payment.amount), func.stddev(Payment.amount))
                .where(Payment.status == "completed")
            )
            row = global_result.first()
            if row and row[0]:
                avg = float(row[0])
                std = float(row[1] or 0)

                # Check if amount is more than 2 std deviations
                if std > 0:
                    z_score = abs(payment.amount - avg) / std
                    if z_score > 2:
                        return {
                            "is_anomaly": True,
                            "risk_score": 0.4,
                            "reason": f"RM{payment.amount:.2f} jauh berbeza dari purata RM{avg:.2f}"
                        }

            return {"is_anomaly": False, "risk_score": 0.0}

        # Check against applicant's own payment history
        mean = statistics.mean(amounts)
        if amounts:
            stdev = statistics.stdev(amounts) if len(amounts) > 1 else 0

            if stdev > 0:
                z_score = abs(payment.amount - mean) / stdev
                if z_score > 2:
                    return {
                        "is_anomaly": True,
                        "risk_score": 0.3,
                        "reason": f"RM{payment.amount:.2f} tidak konsisten dengan sejarah pembayaran"
                    }

        return {"is_anomaly": False, "risk_score": 0.0}

    async def _check_payment_frequency(self, payment: Payment) -> Dict[str, Any]:
        """Check for unusually frequent payments."""
        # Get recent payments
        week_ago = datetime.now() - timedelta(days=7)
        result = await self.db.execute(
            select(func.count(Payment.id))
            .where(Payment.applicant_id == payment.applicant_id)
            .where(Payment.created_at >= week_ago)
        )
        recent_count = result.scalar()

        if recent_count and recent_count >= 3:
            return {
                "is_anomaly": True,
                "risk_score": 0.3,
                "reason": f"{recent_count} pembayaran dalam seminggu adalah tidak biasa"
            }

        return {"is_anomaly": False, "risk_score": 0.0}

    def _check_timing_anomaly(self, payment: Payment) -> Dict[str, Any]:
        """Check for unusual payment timing."""
        # Check if payment is made on weekend
        if payment.created_at:
            weekday = payment.created_at.weekday()
            if weekday >= 5:  # Saturday or Sunday
                return {
                    "is_anomaly": True,
                    "risk_score": 0.1,
                    "reason": "Pembayaran dibuat pada hari cuti"
                }

        return {"is_anomaly": False, "risk_score": 0.0}

    async def _check_duplicate_transaction(self, payment: Payment) -> Dict[str, Any]:
        """Check for duplicate transaction IDs."""
        result = await self.db.execute(
            select(Payment.id)
            .where(Payment.transaction_id == payment.transaction_id)
            .where(Payment.id != payment.id)
        )

        if result.scalar_one_or_none():
            return {
                "is_duplicate": True,
                "risk_score": 0.5,
                "reason": "Nombor transaksi telah digunakan sebelum"
            }

        return {"is_duplicate": False, "risk_score": 0.0}

    def _get_mock_anomaly_check(self, payment: Payment) -> Dict[str, Any]:
        """Return mock anomaly check for testing."""
        return {
            "is_anomaly": False,
            "risk_score": 0.0,
            "anomaly_reason": "Tiada anomali dikesan",
            "confidence_score": 0.8
        }

    async def analyze_spending_patterns(
        self,
        applicant_id: int
    ) -> Dict[str, Any]:
        """Analyze spending patterns for an applicant."""
        if not self.db:
            return {"error": "Database not available"}

        # Get all payments for applicant
        result = await self.db.execute(
            select(Payment)
            .where(Payment.applicant_id == applicant_id)
            .order_by(Payment.created_at)
        )
        payments = result.scalars().all()

        if not payments:
            return {"message": "Tiada sejarah pembayaran"}

        amounts = [p.amount for p in payments]

        return {
            "total_payments": len(payments),
            "total_amount": sum(amounts),
            "average_amount": statistics.mean(amounts),
            "min_amount": min(amounts),
            "max_amount": max(amounts),
            "first_payment": payments[0].created_at.isoformat() if payments else None,
            "last_payment": payments[-1].created_at.isoformat() if payments else None
        }