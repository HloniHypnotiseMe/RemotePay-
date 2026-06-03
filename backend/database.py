"""Database Connection Management"""
import databases
import sqlalchemy as sa
from backend.config import settings

# Database instance
database = databases.Database(settings.DATABASE_URL)

# SQLAlchemy metadata
metadata = sa.MetaData()


# Helper functions
async def connect():
    """Connect to database"""
    await database.connect()


async def disconnect():
    """Disconnect from database"""
    await database.disconnect()
