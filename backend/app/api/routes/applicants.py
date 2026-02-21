from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional

from app.core.database import get_db
from app.models.applicant import Applicant, Document
from app.models.audit import User
from app.schemas.applicant import (
    ApplicantCreate,
    ApplicantUpdate,
    ApplicantResponse,
    ApplicantWithDocuments,
    DocumentCreate,
    DocumentResponse,
    PaginatedApplicants,
    AIAssessment,
)
from app.api.deps import get_current_user, require_role
from app.services.eligibility_service import EligibilityService
from app.services.fraud_detection_service import FraudDetectionService

router = APIRouter(prefix="/applicants", tags=["Applicants"])


@router.get("", response_model=PaginatedApplicants)
async def get_applicants(
    page: int = 1,
    page_size: int = 20,
    status: Optional[str] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get list of applicants with pagination."""
    query = select(Applicant)

    if status:
        query = query.where(Applicant.status == status)

    if search:
        query = query.where(
            (Applicant.name.ilike(f"%{search}%")) |
            (Applicant.ic_number.ilike(f"%{search}%"))
        )

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Get paginated results
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    items = result.scalars().all()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": items
    }


@router.get("/{applicant_id}", response_model=ApplicantWithDocuments)
async def get_applicant(
    applicant_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get applicant details with documents."""
    result = await db.execute(
        select(Applicant).where(Applicant.id == applicant_id)
    )
    applicant = result.scalar_one_or_none()

    if not applicant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Applicant not found"
        )

    return applicant


@router.post("", response_model=ApplicantResponse, status_code=status.HTTP_201_CREATED)
async def create_applicant(
    applicant_data: ApplicantCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "officer"]))
):
    """Create a new applicant."""
    # Check if IC number already exists
    result = await db.execute(
        select(Applicant).where(Applicant.ic_number == applicant_data.ic_number)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="IC number already registered"
        )

    applicant = Applicant(
        **applicant_data.model_dump(),
        status="draft",
        created_by=current_user.id
    )

    db.add(applicant)
    await db.commit()
    await db.refresh(applicant)

    return applicant


@router.patch("/{applicant_id}", response_model=ApplicantResponse)
async def update_applicant(
    applicant_id: int,
    applicant_data: ApplicantUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "officer"]))
):
    """Update applicant information."""
    result = await db.execute(
        select(Applicant).where(Applicant.id == applicant_id)
    )
    applicant = result.scalar_one_or_none()

    if not applicant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Applicant not found"
        )

    # Update fields
    update_data = applicant_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(applicant, field, value)

    await db.commit()
    await db.refresh(applicant)

    return applicant


@router.post("/{applicant_id}/assess", response_model=AIAssessment)
async def assess_applicant(
    applicant_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "officer"]))
):
    """Run AI assessment on applicant."""
    result = await db.execute(
        select(Applicant).where(Applicant.id == applicant_id)
    )
    applicant = result.scalar_one_or_none()

    if not applicant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Applicant not found"
        )

    # Run eligibility scoring
    eligibility_service = EligibilityService(db)
    eligibility_result = await eligibility_service.assess_eligibility(applicant)

    # Run fraud detection
    fraud_service = FraudDetectionService(db)
    fraud_result = await fraud_service.detect_fraud(applicant)

    # Update applicant with results
    applicant.eligibility_score = eligibility_result["score"]
    applicant.fraud_risk_score = fraud_result["risk_score"]
    applicant.is_fraud_detected = fraud_result["is_fraud"]
    applicant.fraud_reasons = fraud_result.get("reasons")

    # Determine eligibility and asnaf category
    if eligibility_result["score"] >= 0.7:
        applicant.asnaf_category = "fakir" if applicant.monthly_income < 500 else "miskin"
        applicant.status = "reviewing"

    await db.commit()
    await db.refresh(applicant)

    return {
        "eligibility_score": eligibility_result["score"],
        "fraud_risk_score": fraud_result["risk_score"],
        "is_fraud_detected": fraud_result["is_fraud"],
        "fraud_reasons": fraud_result.get("reasons"),
        "eligibility_reasons": eligibility_result.get("reasons")
    }


@router.post("/{applicant_id}/documents", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    applicant_id: int,
    document_type: str,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "officer"]))
):
    """Upload a document for an applicant."""
    # Verify applicant exists
    result = await db.execute(
        select(Applicant).where(Applicant.id == applicant_id)
    )
    applicant = result.scalar_one_or_none()

    if not applicant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Applicant not found"
        )

    # Save file
    import os
    from app.core.config import settings
    from datetime import datetime

    upload_dir = os.path.join(settings.UPLOAD_DIR, str(applicant_id))
    os.makedirs(upload_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = os.path.join(upload_dir, f"{timestamp}_{file.filename}")

    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    # Create document record
    document = Document(
        applicant_id=applicant_id,
        document_type=document_type,
        file_path=file_path,
        file_name=file.filename,
        file_size=len(content),
        mime_type=file.content_type
    )

    db.add(document)
    await db.commit()
    await db.refresh(document)

    return document


@router.post("/{applicant_id}/status", response_model=ApplicantResponse)
async def update_applicant_status(
    applicant_id: int,
    status: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "officer"]))
):
    """Update applicant status."""
    result = await db.execute(
        select(Applicant).where(Applicant.id == applicant_id)
    )
    applicant = result.scalar_one_or_none()

    if not applicant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Applicant not found"
        )

    valid_statuses = ["draft", "submitted", "reviewing", "approved", "rejected", "paid"]
    if status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
        )

    applicant.status = status
    await db.commit()
    await db.refresh(applicant)

    return applicant