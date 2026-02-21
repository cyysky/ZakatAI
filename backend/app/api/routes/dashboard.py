from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.audit import User
from app.api.deps import get_current_user
from app.services.monitoring_service import MonitoringService
from app.services.early_warning_service import EarlyWarningService

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats")
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get dashboard statistics."""
    monitoring_service = MonitoringService(db)
    return await monitoring_service.get_dashboard_summary()


@router.get("/critical-cases")
async def get_critical_cases(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get critical cases requiring attention."""
    warning_service = EarlyWarningService(db)
    return await warning_service.get_critical_cases()


@router.get("/warning-stats")
async def get_warning_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get warning statistics."""
    warning_service = EarlyWarningService(db)
    return await warning_service.get_warning_stats()