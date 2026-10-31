"""Data models for SQLite connection pool and Blue/Green swap."""
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class ActiveDbPointer(BaseModel):
    """Schema representing active_db.json pointer on disk."""
    model_config = ConfigDict(frozen=True)

    active_slot: str = Field(description="'blue' or 'green'")
    active_path: str = Field(description="Absolute path to active sqlite database")
    updated_at_utc: str = Field(description="ISO 8601 UTC timestamp")


class PoolStats(BaseModel):
    """Telemetry metrics for SQLite connection pool."""
    model_config = ConfigDict(frozen=True)

    active_connections: int
    idle_connections: int
    max_pool_size: int
    database_path: str
    active_slot: str
    mmap_size_bytes: int
