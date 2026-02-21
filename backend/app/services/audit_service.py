"""
Audit Service - Automated audit trail logging
"""
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.audit import AuditLog, User
from app.models.applicant import Applicant
from datetime import datetime


class AuditService:
    """Service for audit logging and trail management."""

    def __init__(self, db: AsyncSession = None):
        self.db = db

    async def log_action(
        self,
        user_id: Optional[int],
        action: str,
        entity_type: str,
        entity_id: int,
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        applicant_id: Optional[int] = None
    ) -> AuditLog:
        """Log an action to the audit trail."""
        if not self.db:
            return None

        log = AuditLog(
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            old_values=old_values,
            new_values=new_values,
            ip_address=ip_address,
            user_agent=user_agent,
            applicant_id=applicant_id
        )

        self.db.add(log)
        await self.db.commit()
        await self.db.refresh(log)

        return log

    async def log_applicant_create(
        self,
        user_id: int,
        applicant: Applicant,
        ip_address: Optional[str] = None
    ):
        """Log applicant creation."""
        await self.log_action(
            user_id=user_id,
            action="create",
            entity_type="applicant",
            entity_id=applicant.id,
            new_values=applicant.__dict__,
            ip_address=ip_address,
            applicant_id=applicant.id
        )

    async def log_applicant_update(
        self,
        user_id: int,
        applicant: Applicant,
        old_data: Dict[str, Any],
        ip_address: Optional[str] = None
    ):
        """Log applicant update."""
        await self.log_action(
            user_id=user_id,
            action="update",
            entity_type="applicant",
            entity_id=applicant.id,
            old_values=old_data,
            new_values=applicant.__dict__,
            ip_address=ip_address,
            applicant_id=applicant.id
        )

    async def log_status_change(
        self,
        user_id: int,
        applicant: Applicant,
        old_status: str,
        new_status: str,
        ip_address: Optional[str] = None
    ):
        """Log applicant status change."""
        await self.log_action(
            user_id=user_id,
            action=f"status_change_{new_status}",
            entity_type="applicant",
            entity_id=applicant.id,
            old_values={"status": old_status},
            new_values={"status": new_status},
            ip_address=ip_address,
            applicant_id=applicant.id
        )

    async def log_payment_approval(
        self,
        user_id: int,
        payment_id: int,
        approved: bool,
        amount: float,
        ip_address: Optional[str] = None
    ):
        """Log payment approval/rejection."""
        action = "approve" if approved else "reject"

        await self.log_action(
            user_id=user_id,
            action=action,
            entity_type="payment",
            entity_id=payment_id,
            new_values={
                "status": "approved" if approved else "rejected",
                "amount": amount
            },
            ip_address=ip_address
        )

    async def log_user_login(
        self,
        user_id: int,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ):
        """Log user login."""
        await self.log_action(
            user_id=user_id,
            action="login",
            entity_type="user",
            entity_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent
        )

    async def log_fraud_alert(
        self,
        applicant_id: int,
        fraud_score: float,
        reasons: str,
        ip_address: Optional[str] = None
    ):
        """Log fraud detection alert."""
        await self.log_action(
            user_id=None,
            action="fraud_alert",
            entity_type="applicant",
            entity_id=applicant_id,
            new_values={
                "fraud_score": fraud_score,
                "reasons": reasons,
                "alert_type": "automated"
            },
            ip_address=ip_address,
            applicant_id=applicant_id
        )

    async def get_entity_history(
        self,
        entity_type: str,
        entity_id: int
    ) -> list:
        """Get audit history for an entity."""
        if not self.db:
            return []

        from sqlalchemy import select
        result = await self.db.execute(
            select(AuditLog)
            .where(AuditLog.entity_type == entity_type)
            .where(AuditLog.entity_id == entity_id)
            .order_by(AuditLog.created_at.desc())
        )

        return result.scalars().all()

    async def get_user_activity(
        self,
        user_id: int,
        limit: int = 50
    ) -> list:
        """Get activity log for a user."""
        if not self.db:
            return []

        from sqlalchemy import select
        result = await self.db.execute(
            select(AuditLog)
            .where(AuditLog.user_id == user_id)
            .order_by(AuditLog.created_at.desc())
            .limit(limit)
        )

        return result.scalars().all()