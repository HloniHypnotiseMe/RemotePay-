from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # PayFast credentials
    PAYFAST_MERCHANT_ID: str = "10049886"
    PAYFAST_MERCHANT_KEY: str = "ovhgofq8xrkxd"
    PAYFAST_PASSPHRASE: str = ""
    PAYFAST_SANDBOX: bool = True
    
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
