from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List, Optional

from app.core.database import get_db
from app.models.audit import AuditLog, User
from app.schemas.user import AuditLogResponse
from app.api.deps import get_current_user, require_role

router = APIRouter(prefix="/audit", tags=["Audit"])


@router.get("", response_model=List[AuditLogResponse])
async def get_audit_logs(
    page: int = 1,
    page_size: int = 50,
    entity_type: Optional[str] = None,
    action: Optional[str] = None,
    user_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get audit logs with filters."""
    query = select(AuditLog).order_by(desc(AuditLog.created_at))

    if entity_type:
        query = query.where(AuditLog.entity_type == entity_type)

    if action:
        query = query.where(AuditLog.action == action)

    if user_id:
        query = query.where(AuditLog.user_id == user_id)

    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)

    return result.scalars().all()


@router.get("/{log_id}", response_model=AuditLogResponse)
async def get_audit_log(
    log_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    """Get specific audit log details."""
    result = await db.execute(
        select(AuditLog).where(AuditLog.id == log_id)
    )
    log = result.scalar_one_or_none()

    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audit log not found"
        )

    return log


@router.get("/stats/summary")
async def get_audit_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    """Get audit summary statistics."""
    from sqlalchemy import func
    from datetime import datetime, timedelta

    # Total logs
    total_result = await db.execute(select(func.count(AuditLog.id)))
    total_logs = total_result.scalar()

    # Today's logs
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_result = await db.execute(
        select(func.count(AuditLog.id)).where(AuditLog.created_at >= today)
    )
    today_logs = today_result.scalar()

    # By action type
    action_result = await db.execute(
        select(AuditLog.action, func.count(AuditLog.id))
        .group_by(AuditLog.action)
    )

    by_action = {row[0]: row[1] for row in action_result}

    # By entity type
    entity_result = await db.execute(
        select(AuditLog.entity_type, func.count(AuditLog.id))
        .group_by(AuditLog.entity_type)
    )

    by_entity = {row[0]: row[1] for row in entity_result}

    # Recent activity (last 7 days)
    week_ago = datetime.now() - timedelta(days=7)
    daily_result = await db.execute(
        select(
            func.date(AuditLog.created_at).label("date"),
            func.count(AuditLog.id).label("count")
        )
        .where(AuditLog.created_at >= week_ago)
        .group_by(func.date(AuditLog.created_at))
        .order_by(func.date(AuditLog.created_at))
    )

    daily_logs = [{"date": str(row[0]), "count": row[1]} for row in daily_result]

    return {
        "total_logs": total_logs,
        "today_logs": today_logs,
        "by_action": by_action,
        "by_entity": by_entity,
        "daily_logs": daily_logs
    }