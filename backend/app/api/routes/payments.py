from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.models.payment import Payment
from app.models.applicant import Applicant
from app.models.audit import User
from app.schemas.payment import (
    PaymentCreate,
    PaymentUpdate,
    PaymentResponse,
    TransactionAnomaly,
)
from app.api.deps import get_current_user, require_role

router = APIRouter(prefix="/payments", tags=["Payments"])


def generate_payment_reference() -> str:
    """Generate a unique payment reference."""
    import random
    import string
    timestamp = datetime.now().strftime("%Y%m%d")
    random_str = ''.join(random.choices(string.digits, k=6))
    return f"ZKT-{timestamp}-{random_str}"


@router.get("", response_model=List[PaymentResponse])
async def get_payments(
    page: int = 1,
    page_size: int = 20,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get list of payments with pagination."""
    query = select(Payment).order_by(Payment.created_at.desc())

    if status:
        query = query.where(Payment.status == status)

    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)

    return result.scalars().all()


@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment(
    payment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get payment details."""
    result = await db.execute(
        select(Payment).where(Payment.id == payment_id)
    )
    payment = result.scalar_one_or_none()

    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )

    return payment


@router.post("", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
async def create_payment(
    payment_data: PaymentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "officer"]))
):
    """Create a new payment."""
    # Verify applicant exists
    result = await db.execute(
        select(Applicant).where(Applicant.id == payment_data.applicant_id)
    )
    applicant = result.scalar_one_or_none()

    if not applicant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Applicant not found"
        )

    # Check applicant is approved
    if applicant.status != "approved":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Applicant must be approved before payment"
        )

    # Create payment
    payment = Payment(
        **payment_data.model_dump(),
        payment_reference=generate_payment_reference(),
        status="pending"
    )

    db.add(payment)
    await db.commit()
    await db.refresh(payment)

    return payment


@router.patch("/{payment_id}", response_model=PaymentResponse)
async def update_payment(
    payment_id: int,
    payment_data: PaymentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "officer"]))
):
    """Update payment information."""
    result = await db.execute(
        select(Payment).where(Payment.id == payment_id)
    )
    payment = result.scalar_one_or_none()

    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )

    update_data = payment_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(payment, field, value)

    await db.commit()
    await db.refresh(payment)

    return payment


@router.post("/{payment_id}/approve")
async def approve_payment(
    payment_id: int,
    approved: bool,
    notes: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "officer"]))
):
    """Approve or reject a payment."""
    result = await db.execute(
        select(Payment).where(Payment.id == payment_id)
    )
    payment = result.scalar_one_or_none()

    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )

    if approved:
        payment.status = "completed"
        payment.approved_by = current_user.id
        payment.approved_at = datetime.now()
        if notes:
            payment.notes = notes

        # Update applicant status to paid
        applicant = payment.applicant
        applicant.status = "paid"
    else:
        payment.status = "cancelled"
        if notes:
            payment.notes = notes

    await db.commit()
    await db.refresh(payment)

    return payment


@router.get("/{payment_id}/anomaly", response_model=TransactionAnomaly)
async def check_payment_anomaly(
    payment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Check payment for anomalies."""
    from app.services.anomaly_detection_service import AnomalyDetectionService

    result = await db.execute(
        select(Payment).where(Payment.id == payment_id)
    )
    payment = result.scalar_one_or_none()

    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )

    anomaly_service = AnomalyDetectionService(db)
    anomaly_result = await anomaly_service.detect_anomaly(payment)

    return anomaly_result


@router.get("/stats/summary")
async def get_payment_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get payment summary statistics."""
    # Total payments
    total_result = await db.execute(select(func.count(Payment.id)))
    total_payments = total_result.scalar()

    # Total amount
    amount_result = await db.execute(
        select(func.sum(Payment.amount)).where(Payment.status == "completed")
    )
    total_amount = amount_result.scalar() or 0

    # By status
    status_result = await db.execute(
        select(Payment.status, func.count(Payment.id), func.sum(Payment.amount))
        .group_by(Payment.status)
    )

    by_status = []
    for row in status_result:
        by_status.append({
            "status": row[0],
            "count": row[1],
            "amount": float(row[2] or 0)
        })

    # Anomaly count
    anomaly_result = await db.execute(
        select(func.count(Payment.id)).where(Payment.is_anomaly == True)
    )
    anomaly_count = anomaly_result.scalar()

    return {
        "total_payments": total_payments,
        "total_amount": total_amount,
        "by_status": by_status,
        "anomaly_count": anomaly_count
    }