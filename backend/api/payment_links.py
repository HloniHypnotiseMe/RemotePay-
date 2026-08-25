from typing import Any, Dict, Optional
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from core.config import settings
from models.transaction_ledger import TransactionLedgerEntry
from services.simplyblu_provider import SimplyBluProvider
from services.transaction_ledger import TransactionLedger

router = APIRouter()
ledger = TransactionLedger()
ledger_ready = False


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
    metadata: Dict[str, Any] = Field(default_factory=dict)


class PaymentLinkResponse(BaseModel):
    payment_id: str
    transaction_id: str
    status: str
    payment_url: str
    currency: str
    amount_minor: int
    merchant_id: str
    brand_id: str


async def _ensure_ledger() -> None:
    global ledger_ready
    if ledger_ready:
        return
    if not settings.DATABASE_URL:
        raise HTTPException(status_code=503, detail="RemotePay transaction ledger is not configured")
    await ledger.ensure_indexes()
    ledger_ready = True


def _response(entry: TransactionLedgerEntry) -> PaymentLinkResponse:
    payment_url = str(entry.provider_metadata.get("checkout_url") or "")
    if not payment_url:
        raise HTTPException(status_code=502, detail="Stored payment record has no hosted payment URL")
    return PaymentLinkResponse(
        payment_id=entry.payment_id,
        transaction_id=entry.transaction_id,
        status=entry.status,
        payment_url=payment_url,
        currency=entry.currency,
        amount_minor=entry.amount_minor,
        merchant_id=entry.merchant_id,
        brand_id=entry.brand_id,
    )


@router.post("/payment-links", response_model=PaymentLinkResponse, status_code=201)
async def create_payment_link(payment: PaymentLinkCreate):
    await _ensure_ledger()

    existing = await ledger.get_by_idempotency_key(payment.idempotency_key)
    if existing:
        return _response(existing)

    payment_id = f"pay_{uuid4().hex[:16]}"
    transaction_id = f"txn_{uuid4().hex[:16]}"

    if settings.PAYMENT_PROVIDER != "simplyblu":
        raise HTTPException(status_code=503, detail="Configured payment provider is not supported")

    try:
        checkout = SimplyBluProvider().create_payment(
            amount_minor=payment.amount_minor,
            currency=payment.currency,
            reference=transaction_id,
            description=payment.description,
            return_url=payment.return_url,
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail="Underlying payment provider checkout failed") from exc

    entry = TransactionLedgerEntry(
        payment_id=payment_id,
        transaction_id=transaction_id,
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
        provider_reference=checkout.provider_payment_id,
        provider_metadata={
            "provider": checkout.provider,
            "checkout_url": checkout.checkout_url,
            "raw": checkout.raw,
        },
        idempotency_key=payment.idempotency_key,
        metadata={"return_url": payment.return_url, "cancel_url": payment.cancel_url, **payment.metadata},
    )

    try:
        await ledger.create(entry)
    except Exception as exc:
        # A provider checkout exists but cannot be safely persisted. Do not hand
        # the caller a payment URL that RemotePay cannot account for.
        raise HTTPException(status_code=503, detail="Payment created at provider but could not be persisted by RemotePay") from exc

    return _response(entry)


@router.get("/payment-links/{payment_id}", response_model=PaymentLinkResponse)
async def get_payment_link(payment_id: str):
    await _ensure_ledger()
    entry = await ledger.get_by_payment_id(payment_id)
    if entry is None:
        raise HTTPException(status_code=404, detail="Payment link not found")
    return _response(entry)
