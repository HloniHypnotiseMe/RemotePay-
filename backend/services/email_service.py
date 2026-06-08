import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Email config (set these in .env)
SMTP_HOST = os.getenv("SMTP_HOST", "")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
FROM_EMAIL = os.getenv("FROM_EMAIL", "noreply@remote-pay.co.za")

def send_payment_email(to_email: str, customer_name: str, amount: float, transaction_id: str, status: str):
    """Send payment confirmation email"""
    if not SMTP_USER or not SMTP_PASSWORD:
        print(f"Email not configured - would send to {to_email}")
        return False
    
    subject = f"RemotePay Payment {status.upper()} - R{amount:.2f}"
    
    if status == "success":
        body = f"""
        Hello {customer_name},
        
        Your payment of R{amount:.2f} was successful!
        
        Transaction ID: {transaction_id}
        
        Thank you for using RemotePay.
        """
    else:
        body = f"""
        Hello {customer_name},
        
        Your payment of R{amount:.2f} could not be processed.
        
        Transaction ID: {transaction_id}
        Status: {status}
        
        Please try again or contact support.
        """
    
    msg = MIMEMultipart()
    msg["From"] = FROM_EMAIL
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))
    
    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"Email failed: {e}")
        return False
