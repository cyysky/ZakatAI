from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class ApplicantStatus(str, enum.Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    REVIEWING = "reviewing"
    APPROVED = "approved"
    REJECTED = "rejected"
    PAID = "paid"


class AsnafCategory(str, enum.Enum):
    FAKIR = "fakir"
    MISKIN = "miskin"
    AMIL = "amil"
    MUALLAF = "muallaf"
    RIKAB = "rikab"
    GHARIM = "gharim"
    FISABILILLAH = "fisabilillah"
    IBN_SABIL = "ibn_sabil"


class Applicant(Base):
    __tablename__ = "applicants"

    id = Column(Integer, primary_key=True, index=True)
    ic_number = Column(String(12), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=True)
    phone = Column(String(20), nullable=True)
    address = Column(Text, nullable=True)
    postcode = Column(String(10), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)

    # Financial information
    monthly_income = Column(Float, default=0)
    household_size = Column(Integer, default=1)
    occupation = Column(String(255), nullable=True)
    employer = Column(String(255), nullable=True)

    # AI Assessment
    eligibility_score = Column(Float, nullable=True)
    fraud_risk_score = Column(Float, nullable=True)
    is_fraud_detected = Column(Boolean, default=False)
    fraud_reasons = Column(Text, nullable=True)

    # Status
    status = Column(String(50), default=ApplicantStatus.DRAFT.value)
    asnaf_category = Column(String(50), nullable=True)

    # Geo-coordinates for mapping
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Relationships
    documents = relationship("Document", back_populates="applicant")
    payments = relationship("Payment", back_populates="applicant")
    audit_logs = relationship("AuditLog", back_populates="applicant")


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    applicant_id = Column(Integer, ForeignKey("applicants.id"), nullable=False)
    document_type = Column(String(50), nullable=False)  # ic, salary_slip, utility_bill, etc.
    file_path = Column(String(500), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=True)
    mime_type = Column(String(100), nullable=True)

    # OCR and verification results
    extracted_text = Column(Text, nullable=True)
    is_verified = Column(Boolean, default=False)
    verification_notes = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    applicant = relationship("Applicant", back_populates="documents")