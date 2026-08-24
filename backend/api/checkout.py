from html import escape

from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse

from core.config import settings
from services.payfast_service import create_payfast_payment
from services.transaction_ledger import TransactionLedger

router = APIRouter()
ledger = TransactionLedger()


@router.get("/pay/{payment_id}", response_class=HTMLResponse)
async def hosted_checkout(payment_id: str):
    """Render a RemotePay-owned checkout boundary for the configured provider."""
    entry = await ledger.get_by_payment_id(payment_id)
    if entry is None:
        raise HTTPException(status_code=404, detail="Payment link not found")
    if entry.status != "pending":
        raise HTTPException(status_code=409, detail=f"payment is {entry.status}")

    if settings.PAYMENT_PROVIDER.lower() != "payfast":
        raise HTTPException(status_code=503, detail="configured payment provider is unavailable")

    metadata = entry.metadata
    return_url = str(metadata.get("return_url") or "")
    cancel_url = str(metadata.get("cancel_url") or "")
    if not return_url or not cancel_url:
        raise HTTPException(status_code=422, detail="payment return/cancel URLs are required")

    customer_email = str(metadata.get("customer_email") or "")
    provider_payment = create_payfast_payment(
        transaction_id=entry.transaction_id,
        amount=entry.amount_minor,
        item_name=entry.description or "RemotePay payment",
        customer_email=customer_email,
        return_url=return_url,
        cancel_url=cancel_url,
    )

    inputs = "\n".join(
        f'<input type="hidden" name="{escape(str(key))}" value="{escape(str(value))}">' 
        for key, value in provider_payment["form_data"].items()
    )
    action = escape(provider_payment["checkout_url"], quote=True)
    return HTMLResponse(
        "<!doctype html><html><head><meta charset=\"utf-8\"><title>RemotePay Secure Checkout</title>"
        "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\"></head>"
        "<body><main><h1>RemotePay Secure Checkout</h1>"
        "<p>Redirecting you to secure payment processing…</p>"
        f'<form id="checkout" method="post" action="{action}">{inputs}</form>'
        "<script>document.getElementById('checkout').submit();</script>"
        "<noscript><button form=\"checkout\" type=\"submit\">Continue to secure payment</button></noscript>"
        "</main></body></html>"
    )
