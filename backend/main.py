from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uuid
from datetime import datetime

from core.config import settings
from api import payments, customers, assistant, admin

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print(f"Starting {settings.PROJECT_NAME} v{settings.VERSION}...")
    print(f"PayFast Mode: {'SANDBOX' if settings.PAYFAST_SANDBOX else 'PRODUCTION'}")
    yield
    # Shutdown
    print("Shutting down...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check
@app.get("/health")
async def health():
    return {
        "status": "ok",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "payfast_mode": "sandbox" if settings.PAYFAST_SANDBOX else "production",
        "timestamp": datetime.now().isoformat()
    }

# Include routers
app.include_router(customers.router, prefix=settings.API_V1_PREFIX, tags=["Customers"])
app.include_router(payments.router, prefix=settings.API_V1_PREFIX, tags=["Payments"])
app.include_router(admin.router, prefix=settings.API_V1_PREFIX, tags=["Admin"])
app.include_router(assistant.router, prefix=settings.API_V1_PREFIX, tags=["Assistant"])

# Webhook endpoint
@app.post("/webhooks/payfast")
async def payfast_webhook(request: Request):
    """PayFast Instant Transaction Notification"""
    from services.payfast_service import verify_payfast_signature
    
    form_data = await request.form()
    data = dict(form_data)
    
    # Verify signature
    if not verify_payfast_signature(data):
        return JSONResponse(status_code=400, content={"status": "invalid_signature"})
    
    transaction_id = data.get("m_payment_id")
    payment_status = data.get("payment_status")
    
    # Update transaction status (in production, update database)
    print(f"Webhook received: {transaction_id} -> {payment_status}")
    
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
