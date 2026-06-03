"""RemotePay FastAPI Application Entry Point"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from backend.api import health, auth, merchants, transactions, subscriptions, webhooks
from backend.middleware.error_handler import error_handler_middleware
from backend.middleware.rate_limit import rate_limit_middleware
from backend.config import settings
from backend.database import database

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle manager"""
    # Startup
    logger.info("Starting RemotePay application")
    await database.connect()
    logger.info("Database connection established")
    yield
    # Shutdown
    logger.info("Shutting down RemotePay application")
    await database.disconnect()
    logger.info("Database connection closed")


# Create FastAPI application
app = FastAPI(
    title="RemotePay API",
    description="Production-grade payment processing system integrated with PayGate",
    version="1.0.0",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS
)

app.middleware("http")(error_handler_middleware)
app.middleware("http")(rate_limit_middleware)

# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(merchants.router, prefix="/api/v1/merchants", tags=["Merchants"])
app.include_router(transactions.router, prefix="/api/v1/transactions", tags=["Transactions"])
app.include_router(subscriptions.router, prefix="/api/v1/subscriptions", tags=["Subscriptions"])
app.include_router(webhooks.router, prefix="/api/v1/webhooks", tags=["Webhooks"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
