from datetime import datetime, timezone
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorClient

from core.config import settings
from models.transaction_ledger import TransactionLedgerEntry


class TransactionLedger:
    """Append/update canonical RemotePay transaction records in MongoDB.

    The ledger is deliberately independent of the payment provider. Provider
    adapters should normalize their results before writing to this service.
    """

    def __init__(self, database_url: Optional[str] = None):
        url = database_url or settings.DATABASE_URL
        if not url:
            raise RuntimeError("DATABASE_URL is required for the RemotePay transaction ledger")

        self._client = AsyncIOMotorClient(url)
        self._database = self._client.get_default_database()
        self._collection = self._database["transaction_ledger"]

    async def ensure_indexes(self) -> None:
        await self._collection.create_index("payment_id", unique=True)
        await self._collection.create_index("transaction_id", unique=True)
        await self._collection.create_index("idempotency_key", unique=True)
        await self._collection.create_index([("merchant_id", 1), ("created_at", -1)])
        await self._collection.create_index([("brand_id", 1), ("created_at", -1)])
        await self._collection.create_index([("status", 1), ("created_at", -1)])

    async def create(self, entry: TransactionLedgerEntry) -> TransactionLedgerEntry:
        document = entry.model_dump(mode="json")
        await self._collection.insert_one(document)
        return entry

    async def get_by_payment_id(self, payment_id: str) -> Optional[TransactionLedgerEntry]:
        document = await self._collection.find_one({"payment_id": payment_id}, {"_id": 0})
        return TransactionLedgerEntry(**document) if document else None

    async def get_by_transaction_id(self, transaction_id: str) -> Optional[TransactionLedgerEntry]:
        document = await self._collection.find_one({"transaction_id": transaction_id}, {"_id": 0})
        return TransactionLedgerEntry(**document) if document else None

    async def get_by_idempotency_key(self, idempotency_key: str) -> Optional[TransactionLedgerEntry]:
        document = await self._collection.find_one({"idempotency_key": idempotency_key}, {"_id": 0})
        return TransactionLedgerEntry(**document) if document else None

    async def apply_provider_event(self, event) -> Optional[TransactionLedgerEntry]:
        """Reconcile one normalized provider event into the canonical ledger."""
        now = datetime.now(timezone.utc)
        update = {"status": event.status, "updated_at": now}
        if event.provider_reference:
            update["provider_reference"] = event.provider_reference
        if event.status == "paid":
            update["paid_at"] = now
        if event.status == "refunded":
            update["metadata.provider_refund_event_id"] = event.event_id
        if event.metadata:
            update["metadata.provider_event"] = event.metadata

        document = await self._collection.find_one_and_update(
            {"payment_id": event.payment_id, "transaction_id": event.transaction_id},
            {"$set": update},
            projection={"_id": 0},
            return_document=True,
        )
        return TransactionLedgerEntry(**document) if document else None
