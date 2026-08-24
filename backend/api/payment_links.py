from typing import Dict, Optional
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter()


class PaymentLinkCreate(BaseModel):
    merchant_id: str = Field(min_length=1)
    brand_id: str = Field(min_length=1)
    source_system: str = Field(min_length=1)
    customer_reference: Optional[str] = None
    product_id: Optional[str] = None
    offer_id: Optional[str] = None
    description: str = Field(min_length=1)
    amount_minor: int = Field(ge=0)
    currency: str = Field(default="ZAR", min_length=3, max_length=3)
    return_url: Optional[str] = None
    cancel_url: Optional[str] = None
    idempotency_key: str = Field(min_length=1)
    metadata: Dict[str, str] = Field(default_factory=dict)


class PaymentLinkResponse(BaseModel):
    payment_id: str
    transaction_id: str
    status: str
    payment_url: str
    currency: str
    amount_minor: int
    merchant_id: str
    brand_id: str


# Temporary API boundary store. Persistent ledger integration is the next layer.
payment_links: Dict[str, dict] = {}
idempotency_index: Dict[str, str] = {}


@router.post("/payment-links", response_model=PaymentLinkResponse, status_code=201)
async def create_payment_link(payment: PaymentLinkCreate):
    existing_id = idempotency_index.get(payment.idempotency_key)
    if existing_id:
        return PaymentLinkResponse(**payment_links[existing_id])

    payment_id = f"pay_{uuid4().hex[:16]}"
    transaction_id = f"txn_{uuid4().hex[:16]}"
    payment_url = f"/pay/{payment_id}"

    record = {
        "payment_id": payment_id,
        "transaction_id": transaction_id,
        "status": "pending",
        "payment_url": payment_url,
        "currency": payment.currency.upper(),
        "amount_minor": payment.amount_minor,
        "merchant_id": payment.merchant_id,
        "brand_id": payment.brand_id,
    }

    payment_links[payment_id] = record
    idempotency_index[payment.idempotency_key] = payment_id
    return PaymentLinkResponse(**record)


@router.get("/payment-links/{payment_id}", response_model=PaymentLinkResponse)
async def get_payment_link(payment_id: str):
    record = payment_links.get(payment_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Payment link not found")
    return PaymentLinkResponse(**record)
