from datetime import datetime, timezone
from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict, Field


class TransactionLedgerEntry(BaseModel):
    """Canonical RemotePay economic transaction record.

    This model is the persistence boundary for the transaction ledger. Provider-
    specific fields belong in provider_reference/provider_metadata and must not
    replace RemotePay's canonical identifiers or statuses.
    """

    model_config = ConfigDict(extra="forbid")

    payment_id: str
    transaction_id: str
    merchant_id: str
    brand_id: str
    source_system: str
    customer_reference: Optional[str] = None
    product_id: Optional[str] = None
    offer_id: Optional[str] = None
    description: Optional[str] = None
    amount_minor: int = Field(ge=0)
    currency: str = "ZAR"
    fee_minor: Optional[int] = Field(default=None, ge=0)
    net_settlement_minor: Optional[int] = Field(default=None, ge=0)
    status: str
    provider_reference: Optional[str] = None
    provider_metadata: Dict[str, Any] = Field(default_factory=dict)
    idempotency_key: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    paid_at: Optional[datetime] = None
    settled_at: Optional[datetime] = None
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
