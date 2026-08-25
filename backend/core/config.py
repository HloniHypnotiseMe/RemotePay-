from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Current underlying processor. RemotePay remains the merchant-facing boundary.
    PAYMENT_PROVIDER: str = "simplyblu"

    # PayFast credentials must be supplied through environment configuration.
    PAYFAST_MERCHANT_ID: str = ""
    PAYFAST_MERCHANT_KEY: str = ""
    PAYFAST_PASSPHRASE: str = ""
    PAYFAST_SANDBOX: bool = True

    # SimplyBlu / Standard Bank hosted-payment credentials.
    SIMPLYBLU_API_URL: str = "https://sandbox.simplify.com/v1"
    SIMPLYBLU_PUBLIC_KEY: str = ""
    SIMPLYBLU_PRIVATE_KEY: str = ""
    SIMPLYBLU_MERCHANT_EMAIL: str = ""

    # API settings
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "RemotePay API"
    VERSION: str = "2.0.0"

    # CORS
    ALLOWED_ORIGINS: list[str] = ["http://localhost:5173", "https://www.remote-pay.co.za"]

    # Database
    DATABASE_URL: Optional[str] = None

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")


settings = Settings()
