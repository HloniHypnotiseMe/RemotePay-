from datetime import datetime
from typing import Optional, Dict
import uuid

class WebhookLog:
    """Store webhook payloads for audit"""
    
    def __init__(self, transaction_id: str, payload: Dict, status: str = "received"):
        self.id = str(uuid.uuid4())
        self.transaction_id = transaction_id
        self.payload = payload
        self.status = status
        self.created_at = datetime.now().isoformat()
        self.processed_at = None
    
    def to_dict(self):
        return {
            "id": self.id,
            "transaction_id": self.transaction_id,
            "payload": self.payload,
            "status": self.status,
            "created_at": self.created_at,
            "processed_at": self.processed_at
        }

# In-memory storage (replace with DB in production)
webhook_logs = []

def save_webhook_log(log: WebhookLog):
    webhook_logs.append(log)

def get_webhook_logs(limit: int = 100):
    return [log.to_dict() for log in webhook_logs[-limit:]]
