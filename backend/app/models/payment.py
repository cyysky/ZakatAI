from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class PaymentMethod(str, enum.Enum):
    CASH = "cash"
    BANK_TRANSFER = "bank_transfer"
    E_WALLET = "e_wallet"
    CHEQUE = "cheque"


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    applicant_id = Column(Integer, ForeignKey("applicants.id"), nullable=False)
    payment_reference = Column(String(50), unique=True, index=True, nullable=False)

    amount = Column(Float, nullable=False)
    payment_method = Column(String(50), nullable=True)
    status = Column(String(50), default=PaymentStatus.PENDING.value)

    # Bank details
    bank_name = Column(String(100), nullable=True)
    account_number = Column(String(50), nullable=True)
    account_holder_name = Column(String(255), nullable=True)

    # Transaction details
    transaction_date = Column(DateTime(timezone=True), nullable=True)
    transaction_id = Column(String(100), nullable=True)

    # Approval
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)

    # Notes
    notes = Column(Text, nullable=True)

    # Anomaly detection
    is_anomaly = Column(Boolean, default=False)
    anomaly_reason = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    applicant = relationship("Applicant", back_populates="payments")