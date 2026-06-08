from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional, Dict
import uuid
from datetime import datetime

from services.payfast_service import create_payfast_payment
from api.customers import customers_db

router = APIRouter()

# In-memory storage
transactions_db: Dict[str, dict] = {}

class PaymentCreate(BaseModel):
    amount: int  # in cents
    currency: str = "ZAR"
    customer_id: str
    return_url: str
    cancel_url: str
    item_name: str = "RemotePay Payment"
    item_description: Optional[str] = None

class PaymentResponse(BaseModel):
    transaction_id: str
    checkout_url: str
    form_data: dict
    status: str

@router.post("/payments", response_model=PaymentResponse)
async def create_payment(payment: PaymentCreate):
    # Verify customer exists
    if payment.customer_id not in customers_db:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Generate transaction ID
    transaction_id = f"txn_{uuid.uuid4().hex[:16]}"
    
    # Get customer email
    customer = customers_db[payment.customer_id]
    
    # Create PayFast payment
    payfast_result = create_payfast_payment(
        transaction_id=transaction_id,
        amount=payment.amount,
        item_name=payment.item_name,
        customer_email=customer["email"],
        return_url=payment.return_url,
        cancel_url=payment.cancel_url
    )
    
    # Store transaction
    transactions_db[transaction_id] = {
        "id": transaction_id,
        "amount": payment.amount,
        "currency": payment.currency,
        "customer_id": payment.customer_id,
        "status": "pending",
        "created_at": datetime.now().isoformat()
    }
    
    return PaymentResponse(
        transaction_id=transaction_id,
        checkout_url=payfast_result["checkout_url"],
        form_data=payfast_result["form_data"],
        status="pending"
    )



@router.get("/transactions/customer/{customer_id}")
async def get_customer_transactions(customer_id: str, limit: int = 50):
    """Get transaction history for a specific customer"""
    customer_transactions = [
        t for t in transactions_db.values() 
        if t.get("customer_id") == customer_id
    ]
    customer_transactions.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return {
        "customer_id": customer_id,
        "total_transactions": len(customer_transactions),
        "transactions": customer_transactions[:limit]
    }

@router.get("/payments/{transaction_id}")
async def get_payment(transaction_id: str):
    if transaction_id not in transactions_db:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transactions_db[transaction_id]
