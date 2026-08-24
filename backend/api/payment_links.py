from typing import Dict, Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from pymongo.errors import DuplicateKeyError

from auth.merchant_api import authenticate_merchant
from core.config import settings
from models.transaction_ledger import TransactionLedgerEntry
from services.transaction_ledger import TransactionLedger

router = APIRouter()
ledger = TransactionLedger()


class PaymentLinkCreate(BaseModel):
    merchant_id: str = Field(min_length=1)
    brand_id: str = Field(min_length=1)
    source_system: str = Field(min_length=1)
    customer_reference: Optional[str] = None
    product_id: Optional[str] = None
    offer_id: Optional[str] = None
    description: str = Field(min_length=1)
    amount_minor: int = Field(gt=0)
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


def _response(entry: TransactionLedgerEntry) -> PaymentLinkResponse:
    return PaymentLinkResponse(
        payment_id=entry.payment_id,
        transaction_id=entry.transaction_id,
        status=entry.status,
        payment_url=f"{settings.CHECKOUT_BASE_URL.rstrip('/')}/pay/{entry.payment_id}",
        currency=entry.currency,
        amount_minor=entry.amount_minor,
        merchant_id=entry.merchant_id,
        brand_id=entry.brand_id,
    )


@router.post("/payment-links", response_model=PaymentLinkResponse, status_code=201)
async def create_payment_link(
    payment: PaymentLinkCreate,
    authenticated_merchant_id: str = Depends(authenticate_merchant),
):
    if payment.merchant_id != authenticated_merchant_id:
        raise HTTPException(status_code=403, detail="merchant_id does not match API credentials")

    existing = await ledger.get_by_idempotency_key(payment.idempotency_key)
    if existing is not None:
        if existing.merchant_id != authenticated_merchant_id:
            raise HTTPException(status_code=409, detail="idempotency key belongs to another merchant")
        return _response(existing)

    entry = TransactionLedgerEntry(
        payment_id=f"pay_{uuid4().hex[:16]}",
        transaction_id=f"txn_{uuid4().hex[:16]}",
        merchant_id=payment.merchant_id,
        brand_id=payment.brand_id,
        source_system=payment.source_system,
        customer_reference=payment.customer_reference,
        product_id=payment.product_id,
        offer_id=payment.offer_id,
        description=payment.description,
        amount_minor=payment.amount_minor,
        currency=payment.currency.upper(),
        status="pending",
        idempotency_key=payment.idempotency_key,
        metadata={
            **payment.metadata,
            "return_url": payment.return_url or "",
            "cancel_url": payment.cancel_url or "",
        },
    )

    try:
        await ledger.create(entry)
    except DuplicateKeyError:
        existing = await ledger.get_by_idempotency_key(payment.idempotency_key)
        if existing is None:
            raise HTTPException(status_code=409, detail="payment creation conflict")
        return _response(existing)

    return _response(entry)


@router.get("/payment-links/{payment_id}", response_model=PaymentLinkResponse)
async def get_payment_link(
    payment_id: str,
    authenticated_merchant_id: str = Depends(authenticate_merchant),
):
    entry = await ledger.get_by_payment_id(payment_id)
    if entry is None:
        raise HTTPException(status_code=404, detail="Payment link not found")
    if entry.merchant_id != authenticated_merchant_id:
        raise HTTPException(status_code=403, detail="payment does not belong to merchant")
    return _response(entry)
