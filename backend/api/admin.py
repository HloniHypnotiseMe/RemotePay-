from fastapi import APIRouter, HTTPException, Request
from typing import Optional
from datetime import datetime
import os

router = APIRouter()

# Admin key (change this in production)
ADMIN_KEY = os.getenv("ADMIN_KEY", "remote-pay-admin-2026")

def verify_admin(request: Request):
    admin_key = request.headers.get("X-Admin-Key")
    if admin_key != ADMIN_KEY:
        raise HTTPException(status_code=401, detail="Invalid admin key")
    return True

@router.get("/admin/stats")
async def get_stats(request: Request):
    verify_admin(request)
    from api.customers import customers_db
    from api.payments import transactions_db
    from api.assistant import assistants_db
    
    total_volume = sum(t.get("amount", 0) for t in transactions_db.values() if t.get("status") == "success")
    
    return {
        "total_customers": len(customers_db),
        "total_transactions": len(transactions_db),
        "successful_transactions": len([t for t in transactions_db.values() if t.get("status") == "success"]),
        "failed_transactions": len([t for t in transactions_db.values() if t.get("status") == "failed"]),
        "total_volume_zar": total_volume / 100,
        "total_assistants": len(assistants_db),
        "timestamp": datetime.now().isoformat()
    }

@router.get("/admin/transactions")
async def get_all_transactions(request: Request, limit: int = 100):
    verify_admin(request)
    from api.payments import transactions_db
    transactions = list(transactions_db.values())
    transactions.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return {"transactions": transactions[:limit]}

@router.get("/admin/customers")
async def get_all_customers(request: Request, limit: int = 100):
    verify_admin(request)
    from api.customers import customers_db
    customers = list(customers_db.values())
    customers.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return {"customers": customers[:limit]}
