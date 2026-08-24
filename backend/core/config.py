from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Provider credentials are runtime secrets. Never commit real values.
    PAYFAST_MERCHANT_ID: Optional[str] = None
    PAYFAST_MERCHANT_KEY: Optional[str] = None
    PAYFAST_PASSPHRASE: Optional[str] = None
    PAYFAST_SANDBOX: bool = True

    # RemotePay merchant API authentication.
    # JSON object mapping API key -> merchant_id, e.g. {"secret":"mrc_c6"}.
    REMOTEPAY_API_KEYS_JSON: str = ""
    CHECKOUT_BASE_URL: str = "https://api.remote-pay.co.za"
    PAYMENT_PROVIDER: str = "payfast"

    # API settings
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "RemotePay API"
    VERSION: str = "2.0.0"

    # CORS
    ALLOWED_ORIGINS: list = ["http://localhost:5173", "https://www.remote-pay.co.za"]

    # Database
    DATABASE_URL: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
