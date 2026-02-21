from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


# Base applicant schema
class ApplicantBase(BaseModel):
    ic_number: str
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    postcode: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    monthly_income: float = 0
    household_size: int = 1
    occupation: Optional[str] = None
    employer: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


# Create applicant
class ApplicantCreate(ApplicantBase):
    pass


# Update applicant
class ApplicantUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    postcode: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    monthly_income: Optional[float] = None
    household_size: Optional[int] = None
    occupation: Optional[str] = None
    employer: Optional[str] = None
    status: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


# AI Assessment result
class AIAssessment(BaseModel):
    eligibility_score: Optional[float] = None
    fraud_risk_score: Optional[float] = None
    is_fraud_detected: bool = False
    fraud_reasons: Optional[str] = None
    eligibility_reasons: Optional[str] = None


# Full applicant response
class ApplicantResponse(ApplicantBase):
    id: int
    eligibility_score: Optional[float] = None
    fraud_risk_score: Optional[float] = None
    is_fraud_detected: bool = False
    fraud_reasons: Optional[str] = None
    status: str
    asnaf_category: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Document schemas
class DocumentBase(BaseModel):
    document_type: str
    file_name: str


class DocumentCreate(DocumentBase):
    applicant_id: int
    file_path: str
    file_size: Optional[int] = None
    mime_type: Optional[str] = None


class DocumentResponse(DocumentBase):
    id: int
    applicant_id: int
    file_path: str
    file_size: Optional[int] = None
    mime_type: Optional[str] = None
    extracted_text: Optional[str] = None
    is_verified: bool = False
    verification_notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Complete applicant with documents
class ApplicantWithDocuments(ApplicantResponse):
    documents: List[DocumentResponse] = []


# Eligibility criteria
class EligibilityCriteria(BaseModel):
    monthly_income_threshold: float = 1169  # Below RM1169 is poor
    household_income_per_person: float = 400  # Below RM400 per person
    max_assets_value: float = 20000
    has_valid_documents: bool = True


# Pagination
class PaginatedApplicants(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[ApplicantResponse]