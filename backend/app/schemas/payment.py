from pydantic import BaseModel
from typing import Optional
from datetime import datetime


# Base payment schema
class PaymentBase(BaseModel):
    applicant_id: int
    amount: float
    payment_method: Optional[str] = None
    bank_name: Optional[str] = None
    account_number: Optional[str] = None
    account_holder_name: Optional[str] = None
    notes: Optional[str] = None


# Create payment
class PaymentCreate(PaymentBase):
    pass


# Update payment
class PaymentUpdate(BaseModel):
    amount: Optional[float] = None
    payment_method: Optional[str] = None
    status: Optional[str] = None
    bank_name: Optional[str] = None
    account_number: Optional[str] = None
    account_holder_name: Optional[str] = None
    transaction_date: Optional[datetime] = None
    transaction_id: Optional[str] = None
    notes: Optional[str] = None


# Payment response
class PaymentResponse(PaymentBase):
    id: int
    payment_reference: str
    status: str
    transaction_date: Optional[datetime] = None
    transaction_id: Optional[str] = None
    approved_by: Optional[int] = None
    approved_at: Optional[datetime] = None
    is_anomaly: bool = False
    anomaly_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Payment approval
class PaymentApprove(BaseModel):
    approved: bool
    notes: Optional[str] = None


# Transaction anomaly
class TransactionAnomaly(BaseModel):
    is_anomaly: bool
    anomaly_reason: Optional[str] = None
    confidence_score: float = 0.0