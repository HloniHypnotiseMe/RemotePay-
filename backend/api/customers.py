from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict
import uuid
from datetime import datetime

router = APIRouter()

# In-memory storage (replace with database in production)
customers_db: Dict[str, dict] = {}

class CustomerCreate(BaseModel):
    email: EmailStr
    name: str
    phone: Optional[str] = None

class CustomerResponse(BaseModel):
    id: str
    email: str
    name: str
    phone: Optional[str]
    created_at: str

@router.post("/customers", response_model=CustomerResponse)
async def create_customer(customer: CustomerCreate):
    customer_id = f"cus_{uuid.uuid4().hex[:12]}"
    customers_db[customer_id] = {
        "id": customer_id,
        "email": customer.email,
        "name": customer.name,
        "phone": customer.phone,
        "created_at": datetime.now().isoformat()
    }
    return customers_db[customer_id]

@router.get("/customers/{customer_id}", response_model=CustomerResponse)
async def get_customer(customer_id: str):
    if customer_id not in customers_db:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customers_db[customer_id]
