import re

with open('api/payments.py', 'r') as f:
    content = f.read()

# Add get_transactions endpoint if not exists
if 'get_customer_transactions' not in content:
    new_endpoint = '''

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
    }'''
    
    # Insert before the last function
    content = content.replace('@router.get("/payments/{transaction_id}")', new_endpoint + '\n\n@router.get("/payments/{transaction_id}")')
    
    with open('api/payments.py', 'w') as f:
        f.write(content)
    print("✅ Transaction history added")
else:
    print("✅ Transaction history already exists")
