"""Pydantic V2 models for Agentic API endpoints."""
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field, ConfigDict, AliasChoices


class AgentHealthResponse(BaseModel):
    """Runtime health and memory telemetry."""
    model_config = ConfigDict(frozen=True)

    status: str = "healthy"
    rss_mb: float
    db_active: str
    uptime_seconds: float


class AgentStateResponse(BaseModel):
    """Full serialized application state."""
    model_config = ConfigDict(frozen=True)

    active_slot: str
    active_db_path: str
    pool_stats: Dict[str, Any]
    session_count: int
    system_alert_level: str


class AgentExecuteRequest(BaseModel):
    """Action execution request specification."""
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    action_type: str = Field(description="Action name, e.g. 'EVALUATE_DIAGNOSTIC'")
    action_parameters: Dict[str, Any] = Field(
        default_factory=dict,
        validation_alias=AliasChoices("action_parameters", "payload"),
        serialization_alias="action_parameters",
        description="Typed parameters for the action",
    )


class AgentExecuteResponse(BaseModel):
    """Action execution outcome envelope."""
    model_config = ConfigDict(frozen=True, populate_by_name=True)

    success: bool
    action_type: str
    execution_outcome: Dict[str, Any] = Field(
        default_factory=dict,
        validation_alias=AliasChoices("execution_outcome", "result"),
        serialization_alias="execution_outcome",
        description="Execution outcome dictionary",
    )
    error_message: Optional[str] = None

