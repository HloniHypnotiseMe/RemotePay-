import hashlib
import urllib.parse
from core.config import settings

def generate_payfast_signature(data: dict) -> str:
    """Generate MD5 signature for PayFast"""
    # Remove empty values
    filtered = {k: str(v) for k, v in data.items() if v and k != 'signature'}
    
    # Sort keys alphabetically
    sorted_items = sorted(filtered.items())
    
    # Create query string
    query_string = '&'.join([f"{k}={v}" for k, v in sorted_items])
    
    # Add passphrase if set
    if settings.PAYFAST_PASSPHRASE:
        query_string += f'&passphrase={settings.PAYFAST_PASSPHRASE}'
    
    # Generate MD5 hash
    return hashlib.md5(query_string.encode()).hexdigest()

def create_payfast_payment(
    transaction_id: str,
    amount: int,
    item_name: str,
    customer_email: str,
    return_url: str,
    cancel_url: str
) -> dict:
    """Create PayFast payment data"""
    
    # Convert cents to Rand
    amount_rand = amount / 100
    
    # Base URL
    if settings.PAYFAST_SANDBOX:
        checkout_url = "https://sandbox.payfast.co.za/eng/process"
    else:
        checkout_url = "https://www.payfast.co.za/eng/process"
    
    # Prepare form data
    form_data = {
        "merchant_id": settings.PAYFAST_MERCHANT_ID,
        "merchant_key": settings.PAYFAST_MERCHANT_KEY,
        "return_url": return_url,
        "cancel_url": cancel_url,
        "notify_url": f"https://api.remote-pay.co.za/webhooks/payfast",
        "m_payment_id": transaction_id,
        "amount": f"{amount_rand:.2f}",
        "item_name": item_name,
        "item_description": f"Payment for {item_name}",
        "email_confirmation": "1",
        "confirmation_address": customer_email,
    }
    
    # Add signature
    form_data["signature"] = generate_payfast_signature(form_data)
    
    return {
        "checkout_url": checkout_url,
        "form_data": form_data
    }

def verify_payfast_signature(data: dict) -> bool:
    """Verify incoming webhook signature"""
    received_signature = data.get("signature", "")
    calculated_signature = generate_payfast_signature(data)
    return received_signature == calculated_signature
