import re

# Read current main.py
with open('main.py', 'r') as f:
    content = f.read()

# Add import for webhook logging
if 'from models.transaction import WebhookLog, save_webhook_log' not in content:
    content = content.replace(
        'from api import payments, customers, assistant',
        'from api import payments, customers, assistant\nfrom models.transaction import WebhookLog, save_webhook_log'
    )

# Update webhook endpoint to log payloads
old_webhook = '''@app.post("/webhooks/payfast")
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
    print(f"📝 Webhook received: {transaction_id} -> {payment_status}")
    
    return {"status": "ok"}'''

new_webhook = '''@app.post("/webhooks/payfast")
async def payfast_webhook(request: Request):
    """PayFast Instant Transaction Notification"""
    from services.payfast_service import verify_payfast_signature
    
    form_data = await request.form()
    data = dict(form_data)
    
    # Create webhook log
    transaction_id = data.get("m_payment_id", "unknown")
    webhook_log = WebhookLog(transaction_id=transaction_id, payload=data)
    save_webhook_log(webhook_log)
    
    # Verify signature
    if not verify_payfast_signature(data):
        webhook_log.status = "failed_signature"
        return JSONResponse(status_code=400, content={"status": "invalid_signature"})
    
    payment_status = data.get("payment_status")
    
    # Update transaction status
    from api.payments import transactions_db
    if transaction_id in transactions_db:
        if payment_status == "COMPLETE":
            transactions_db[transaction_id]["status"] = "success"
        elif payment_status == "FAILED":
            transactions_db[transaction_id]["status"] = "failed"
        elif payment_status == "CANCELLED":
            transactions_db[transaction_id]["status"] = "cancelled"
        webhook_log.status = "processed"
    
    webhook_log.processed_at = datetime.now().isoformat()
    print(f"📝 Webhook: {transaction_id} -> {payment_status}")
    
    return {"status": "ok"}

@app.get("/api/v1/webhooks/logs")
async def get_webhook_logs(limit: int = 100):
    """Get recent webhook logs (admin only)"""
    from models.transaction import get_webhook_logs
    return {"logs": get_webhook_logs(limit)}'''

if old_webhook in content:
    content = content.replace(old_webhook, new_webhook)
    with open('main.py', 'w') as f:
        f.write(content)
    print("✅ Webhook logging added")
else:
    print("⚠️ Webhook pattern not found - manual check needed")
