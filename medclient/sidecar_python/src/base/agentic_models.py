"""Pydantic V2 models for Agentic API endpoints."""
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field, ConfigDict, model_validator, model_serializer


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
        description="Typed parameters for the action",
    )

    @model_validator(mode="before")
    @classmethod
    def populate_action_parameters(cls, action_parameters: Any) -> Any:
        if isinstance(action_parameters, dict):
            if "payload" in action_parameters and "action_parameters" not in action_parameters:
                normalized_map = dict(action_parameters)
                normalized_map["action_parameters"] = normalized_map.pop("payload")
                return normalized_map
        return action_parameters


class AgentExecuteResponse(BaseModel):
    """Action execution outcome envelope."""
    model_config = ConfigDict(frozen=False, populate_by_name=True)

    success: bool
    action_type: str
    execution_outcome: Dict[str, Any] = Field(
        default_factory=dict,
        description="Execution outcome dictionary",
    )
    error_message: Optional[str] = None

    @model_serializer(mode="wrap")
    def serialize_outcome_envelope(self, serializer_handler: Any) -> Dict[str, Any]:
        serialized_envelope = serializer_handler(self)
        if "execution_outcome" in serialized_envelope:
            serialized_envelope["result"] = serialized_envelope["execution_outcome"]
        return serialized_envelope


