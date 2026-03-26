# ============================================================
# AI-Guardian - MongoDB Database Connection
# ============================================================

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from pymongo.database import Database
from typing import Optional
import os

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://admin:ai_guardian_secure_pass_2024@localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "ai_guardian")

_client_async: Optional[AsyncIOMotorClient] = None
_client_sync: Optional[MongoClient] = None
_db_async: Optional[Database] = None


def get_async_client() -> AsyncIOMotorClient:
    """Get async MongoDB client (singleton)."""
    global _client_async
    if _client_async is None:
        _client_async = AsyncIOMotorClient(MONGODB_URL)
    return _client_async


def get_sync_client() -> MongoClient:
    """Get sync MongoDB client (singleton)."""
    global _client_sync
    if _client_sync is None:
        _client_sync = MongoClient(MONGODB_URL)
    return _client_sync


def get_database() -> Database:
    """Get async database instance."""
    global _db_async
    if _db_async is None:
        _db_async = get_async_client()[DATABASE_NAME]
    return _db_async


async def get_db():
    """FastAPI dependency for database access."""
    return get_database()


class DatabaseCollections:
    """Convenience wrapper for all database collections."""

    def __init__(self, db: Database):
        self._db = db

    @property
    def sensor_logs(self):
        return self._db.sensor_logs

    @property
    def alerts(self):
        return self._db.alerts

    @property
    def incidents(self):
        return self._db.incidents

    @property
    def actuator_logs(self):
        return self._db.actuator_logs

    @property
    def camera_alerts(self):
        return self._db.camera_alerts

    @property
    def settings(self):
        return self._db.settings

    @property
    def system_stats(self):
        return self._db.system_stats


def get_collections() -> DatabaseCollections:
    """Get all collections wrapper."""
    return DatabaseCollections(get_database())


async def close_connections():
    """Close all database connections."""
    global _client_async, _client_sync
    if _client_async:
        _client_async.close()
        _client_async = None
    if _client_sync:
        _client_sync.close()
        _client_sync = None
