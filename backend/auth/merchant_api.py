import json
from typing import Mapping

from fastapi import Header, HTTPException

from core.config import settings


def _api_keys() -> Mapping[str, str]:
    if not settings.REMOTEPAY_API_KEYS_JSON:
        return {}
    try:
        values = json.loads(settings.REMOTEPAY_API_KEYS_JSON)
    except json.JSONDecodeError as exc:
        raise RuntimeError("REMOTEPAY_API_KEYS_JSON is invalid JSON") from exc
    if not isinstance(values, dict):
        raise RuntimeError("REMOTEPAY_API_KEYS_JSON must be a JSON object")
    return {str(key): str(value) for key, value in values.items() if key and value}


async def authenticate_merchant(
    authorization: str | None = Header(default=None),
) -> str:
    """Authenticate an ecosystem caller and return its server-side merchant ID."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="RemotePay API authentication required")

    token = authorization.removeprefix("Bearer ").strip()
    if not token:
        raise HTTPException(status_code=401, detail="RemotePay API authentication required")

    merchant_id = _api_keys().get(token)
    if not merchant_id:
        raise HTTPException(status_code=401, detail="Invalid RemotePay API credentials")
    return merchant_id
