from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    PAYFAST_MERCHANT_ID: str = "10049886"
    PAYFAST_MERCHANT_KEY: str = "ovhgofq8xrkxd"
    PAYFAST_PASSPHRASE: str = ""
    PAYFAST_SANDBOX: bool = False
    
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "RemotePay API"
    VERSION: str = "2.0.0"
    
    ALLOWED_ORIGINS: List[str] = ["http://localhost:5173", "https://www.remote-pay.co.za"]
    
    ADMIN_KEY: str = "remote-pay-admin-2026"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
