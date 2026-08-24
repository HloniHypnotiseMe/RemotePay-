from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from datetime import datetime

from core.config import settings
from api import payments, customers, assistant, payment_links, checkout, webhooks
from services.transaction_ledger import TransactionLedger


@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"🚀 {settings.PROJECT_NAME} v{settings.VERSION} starting...")
    print(f"💰 PayFast Mode: {'SANDBOX' if settings.PAYFAST_SANDBOX else 'PRODUCTION'}")
    if settings.DATABASE_URL:
        await TransactionLedger().ensure_indexes()
        print("🧾 Transaction ledger indexes verified")
    else:
        print("⚠️ DATABASE_URL is not configured; payment persistence is unavailable")
    yield
    print("👋 Shutting down...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "payfast_mode": "sandbox" if settings.PAYFAST_SANDBOX else "production",
        "ledger_configured": bool(settings.DATABASE_URL),
        "timestamp": datetime.now().isoformat(),
    }


app.include_router(customers.router, prefix=settings.API_V1_PREFIX, tags=["Customers"])
app.include_router(payments.router, prefix=settings.API_V1_PREFIX, tags=["Payments"])
app.include_router(payment_links.router, prefix=settings.API_V1_PREFIX, tags=["Payment Links"])
app.include_router(assistant.router, prefix=settings.API_V1_PREFIX, tags=["Assistant"])
app.include_router(webhooks.router, prefix=settings.API_V1_PREFIX, tags=["Provider Webhooks"])
app.include_router(checkout.router, tags=["Hosted Checkout"])


@app.post("/webhooks/payfast")
async def payfast_webhook(request: Request):
    """PayFast Instant Transaction Notification."""
    from services.payfast_service import verify_payfast_signature
    from services.transaction_ledger import TransactionLedger

    form_data = await request.form()
    data = dict(form_data)

    if not verify_payfast_signature(data):
        return JSONResponse(status_code=400, content={"status": "invalid_signature"})

    transaction_id = data.get("m_payment_id")
    payment_status = str(data.get("payment_status", "")).lower()
    ledger = TransactionLedger()
    entry = await ledger.get_by_transaction_id(str(transaction_id)) if transaction_id else None
    if entry is None:
        return JSONResponse(status_code=404, content={"status": "transaction_not_found"})

    status_map = {"complete": "paid", "failed": "failed", "cancelled": "cancelled"}
    status = status_map.get(payment_status)
    if status is None:
        return JSONResponse(status_code=400, content={"status": "unsupported_payment_status"})

    updated = await ledger.update_status(
        entry.payment_id,
        status,
        provider_reference=str(data.get("pf_payment_id") or "") or None,
    )
    return {
        "status": "ok",
        "payment_id": updated.payment_id if updated else entry.payment_id,
        "transaction_id": entry.transaction_id,
        "payment_status": status,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
