from datetime import datetime, timezone
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ReturnDocument

from core.config import settings
from models.transaction_ledger import TransactionLedgerEntry


class TransactionLedger:
    """Append/update canonical RemotePay transaction records in MongoDB.

    The ledger is deliberately independent of the payment provider. Provider
    adapters normalize provider results before writing to this service.
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

    async def update_status(
        self,
        payment_id: str,
        status: str,
        *,
        provider_reference: Optional[str] = None,
    ) -> Optional[TransactionLedgerEntry]:
        now = datetime.now(timezone.utc)
        updates = {"status": status, "updated_at": now}
        if provider_reference:
            updates["provider_reference"] = provider_reference
        if status == "paid":
            updates["paid_at"] = now
        if status == "settled":
            updates["settled_at"] = now

        document = await self._collection.find_one_and_update(
            {"payment_id": payment_id},
            {"$set": updates},
            return_document=ReturnDocument.AFTER,
            projection={"_id": 0},
        )
        return TransactionLedgerEntry(**document) if document else None
