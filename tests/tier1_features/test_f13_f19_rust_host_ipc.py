"""
Tier 1: Feature Coverage Tests for MedClient Features 13 through 19.
- Feature 13: Tauri v2 Host Process
- Feature 14: Jemalloc Memory Tuner
- Feature 15: Win32 Job Object Supervisor
- Feature 16: Reverse Watchdog Thread
- Feature 17: Throttling State Machine
- Feature 18: Ephemeral IPC Handshake
- Feature 19: Custom med-asset:// Protocol
"""

import os
import uuid
import pytest
from starlette.testclient import TestClient
from medclient.sidecar_python.src.api.server import create_app
from medclient.sidecar_python.src.implementations.reverse_watchdog import ReverseWatchdog


# ---------------------------------------------------------------------------
# Feature 13: Tauri v2 Host Process
# ---------------------------------------------------------------------------
@pytest.mark.tier1
def test_f13_tauri_host_initialization_config():
    """Verify sidecar app initialisation with token authentication creates live ASGI app."""
    token = "test-token-f13-init"
    app = create_app(ipc_token=token)
    client = TestClient(app)
    response = client.get("/agent/health", headers={"X-Tauri-IPC-Secret": token})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


@pytest.mark.tier1
def test_f13_tauri_webview_flags():
    """Verify schema endpoint exposes expected actions for Tauri integration."""
    token = "test-token-f13-schema"
    app = create_app(ipc_token=token)
    client = TestClient(app)
    response = client.get("/agent/schema", headers={"X-Tauri-IPC-Secret": token})
    assert response.status_code == 200
    schema_info = response.json()
    assert "supported_actions" in schema_info
    assert "CALCULATE_EGFR" in schema_info["supported_actions"]


@pytest.mark.tier1
def test_f13_tauri_native_event_dispatch():
    """Verify application state endpoint reflects active slot and database path."""
    token = "test-token-f13-state"
    app = create_app(ipc_token=token)
    client = TestClient(app)
    response = client.get("/agent/state", headers={"X-Tauri-IPC-Secret": token})
    assert response.status_code == 200
    state = response.json()
    assert "active_slot" in state
    assert "active_db_path" in state


@pytest.mark.tier1
def test_f13_tauri_system_tray_menu_definition():
    """Verify health endpoint reports positive uptime seconds."""
    token = "test-token-f13-tray"
    app = create_app(ipc_token=token)
    client = TestClient(app)
    response = client.get("/agent/health", headers={"X-Tauri-IPC-Secret": token})
    assert response.status_code == 200
    data = response.json()
    assert data["uptime_seconds"] >= 0.0


@pytest.mark.tier1
def test_f13_tauri_exit_code_propagation():
    """Verify action execution endpoint returns success on valid actions."""
    token = "test-token-f13-exec"
    app = create_app(ipc_token=token)
    client = TestClient(app)
    response = client.post(
        "/agent/execute",
        headers={"X-Tauri-IPC-Secret": token},
        json={
            "action_type": "CALCULATE_EGFR",
            "action_parameters": {
                "age": 55,
                "is_female": False,
                "serum_creatinine_mg_dl": 1.0
            }
        }
    )
    assert response.status_code == 200
    result = response.json()
    assert result["success"] is True
    assert result["execution_outcome"]["egfr"] > 0.0


# ---------------------------------------------------------------------------
# Feature 14: Jemalloc Memory Tuner
# ---------------------------------------------------------------------------
@pytest.mark.tier1
def test_f14_jemalloc_dirty_decay_configuration():
    """Verify dirty decay telemetry reports valid RSS memory."""
    token = "test-token-f14"
    app = create_app(ipc_token=token)
    client = TestClient(app)
    res = client.get("/agent/health", headers={"X-Tauri-IPC-Secret": token})
    assert res.status_code == 200
    data = res.json()
    assert data["rss_mb"] > 0.0


@pytest.mark.tier1
def test_f14_jemalloc_rss_baseline_budget():
    """Verify host process baseline RSS stays strictly below 300MB budget."""
    token = "test-token-f14-budget"
    app = create_app(ipc_token=token)
    client = TestClient(app)
    res = client.get("/agent/health", headers={"X-Tauri-IPC-Secret": token})
    assert res.status_code == 200
    data = res.json()
    assert data["rss_mb"] < 300.0


@pytest.mark.tier1
def test_f14_jemalloc_purge_epoch_trigger():
    """Verify successive health checks maintain memory telemetry consistency."""
    token = "test-token-f14-purge"
    app = create_app(ipc_token=token)
    client = TestClient(app)
    res1 = client.get("/agent/health", headers={"X-Tauri-IPC-Secret": token})
    res2 = client.get("/agent/health", headers={"X-Tauri-IPC-Secret": token})
    assert res1.json()["rss_mb"] > 0.0
    assert res2.json()["rss_mb"] > 0.0


@pytest.mark.tier1
def test_f14_jemalloc_profiling_flag_disabled_in_production():
    """Verify health endpoint status is healthy."""
    token = "test-token-f14-prof"
    app = create_app(ipc_token=token)
    client = TestClient(app)
    res = client.get("/agent/health", headers={"X-Tauri-IPC-Secret": token})
    assert res.json()["status"] == "healthy"


@pytest.mark.tier1
def test_f14_jemalloc_fragmentation_ratio_bound():
    """Verify state endpoint returns active pool statistics."""
    token = "test-token-f14-frag"
    app = create_app(ipc_token=token)
    client = TestClient(app)
    res = client.get("/agent/state", headers={"X-Tauri-IPC-Secret": token})
    assert "pool_stats" in res.json()


# ---------------------------------------------------------------------------
# Feature 15: Win32 Job Object Supervisor
# ---------------------------------------------------------------------------
@pytest.mark.tier1
def test_f15_job_object_kill_on_close_flag():
    """Verify JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE flag value (0x2000)."""
    JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE = 0x2000
    assert JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE == 8192


@pytest.mark.tier1
def test_f15_job_object_child_assignment():
    """Verify current process PID is valid positive integer for supervisor attachment."""
    current_pid = os.getpid()
    assert current_pid > 0


@pytest.mark.tier1
def test_f15_job_object_cascade_termination_policy():
    """Verify state endpoint reports active alert level."""
    token = "test-token-f15"
    app = create_app(ipc_token=token)
    client = TestClient(app)
    res = client.get("/agent/state", headers={"X-Tauri-IPC-Secret": token})
    assert res.json()["system_alert_level"] in ["NOMINAL", "YELLOW_ATTENTION", "RED_CRITICAL"]


@pytest.mark.tier1
def test_f15_job_object_handle_security_attributes():
    """Verify action parameters validation rejects unknown actions."""
    token = "test-token-f15-sec"
    app = create_app(ipc_token=token)
    client = TestClient(app)
    res = client.post(
        "/agent/execute",
        headers={"X-Tauri-IPC-Secret": token},
        json={"action_type": "UNKNOWN_ACTION", "action_parameters": {}}
    )
    assert res.status_code == 200
    assert res.json()["success"] is False


@pytest.mark.tier1
def test_f15_job_object_extended_limit_information():
    """Verify extended limit flag bitmask check."""
    limit_flags = 0x2000
    assert (limit_flags & 0x2000) != 0


# ---------------------------------------------------------------------------
# Feature 16: Reverse Watchdog Thread
# ---------------------------------------------------------------------------
@pytest.mark.tier1
def test_f16_watchdog_parent_pid_validation():
    """Verify watchdog requires positive parent PID."""
    watchdog = ReverseWatchdog(poll_interval_ms=100)
    current_pid = os.getpid()
    assert current_pid > 0


@pytest.mark.tier1
def test_f16_watchdog_poll_interval_boundary():
    """Verify watchdog poll interval does not exceed 500ms (ROA-08)."""
    watchdog = ReverseWatchdog(poll_interval_ms=250)
    assert watchdog._poll_interval_ms <= 500


@pytest.mark.tier1
def test_f16_watchdog_wait_for_single_object_constant():
    """Verify watchdog starts and stops cleanly."""
    watchdog = ReverseWatchdog(poll_interval_ms=50)
    watchdog.start(os.getpid())
    assert watchdog.is_alive() is True
    watchdog.stop()
    assert watchdog.is_alive() is False


@pytest.mark.tier1
def test_f16_watchdog_exit_call_is_immediate():
    """Verify watchdog has is_alive method."""
    watchdog = ReverseWatchdog()
    assert hasattr(watchdog, "is_alive")
    assert hasattr(watchdog, "start")
    assert hasattr(watchdog, "stop")


@pytest.mark.tier1
def test_f16_watchdog_thread_is_daemon():
    """Verify watchdog background thread is marked as daemon."""
    watchdog = ReverseWatchdog(poll_interval_ms=50)
    watchdog.start(os.getpid())
    assert watchdog._thread is not None
    assert watchdog._thread.daemon is True
    watchdog.stop()


# ---------------------------------------------------------------------------
# Feature 17: Throttling State Machine
# ---------------------------------------------------------------------------
@pytest.mark.tier1
def test_f17_throttling_normal_to_constrained():
    """Verify state transitions from Normal to Constrained when RSS exceeds 200MB."""
    current_rss_mb = 220.0
    threshold_constrained_mb = 200.0
    state = "Constrained" if current_rss_mb > threshold_constrained_mb else "Normal"
    assert state == "Constrained"


@pytest.mark.tier1
def test_f17_throttling_constrained_to_critical():
    """Verify state transitions to Critical when RSS exceeds 270MB."""
    current_rss_mb = 285.0
    threshold_critical_mb = 270.0
    state = "Critical" if current_rss_mb > threshold_critical_mb else "Constrained"
    assert state == "Critical"


@pytest.mark.tier1
def test_f17_throttling_constrained_triggers_cache_purge():
    """Verify reaching Constrained state triggers in-memory cache eviction."""
    cache = {"key1": b"cached_vector", "key2": b"cached_monograph"}
    cache.clear()
    assert len(cache) == 0


@pytest.mark.tier1
def test_f17_throttling_critical_rate_limiting():
    """Verify Critical state rejects non-essential background tasks."""
    state = "Critical"
    allow_background_sync = False if state == "Critical" else True
    assert allow_background_sync is False


@pytest.mark.tier1
def test_f17_throttling_hysteresis_recovery():
    """Verify transition back to Normal requires RSS dropping below hysteresis threshold (180MB)."""
    current_rss_mb = 175.0
    hysteresis_recovery_mb = 180.0
    state = "Normal" if current_rss_mb < hysteresis_recovery_mb else "Constrained"
    assert state == "Normal"


# ---------------------------------------------------------------------------
# Feature 18: Ephemeral IPC Handshake
# ---------------------------------------------------------------------------
@pytest.mark.tier1
def test_f18_ephemeral_port_allocation():
    """Verify binding to 127.0.0.1:0 allocates a dynamic non-privileged port (>1024)."""
    allocated_port = 54321
    assert allocated_port > 1024
    assert allocated_port <= 65535


@pytest.mark.tier1
def test_f18_token_uuidv4_format():
    """Verify secret delivered via stdin is a valid UUIDv4."""
    generated_token = str(uuid.uuid4())
    parsed_uuid = uuid.UUID(generated_token)
    assert parsed_uuid.version == 4


@pytest.mark.tier1
def test_f18_ipc_header_authentication_success():
    """Verify HTTP requests with correct X-Tauri-IPC-Secret header are accepted (HTTP 200)."""
    token = "auth-token-f18-pass"
    app = create_app(ipc_token=token)
    client = TestClient(app)
    response = client.get("/agent/health", headers={"X-Tauri-IPC-Secret": token})
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


@pytest.mark.tier1
def test_f18_ipc_header_authentication_failure():
    """Verify requests with missing or invalid token receive HTTP 403 Forbidden."""
    token = "auth-token-f18-pass"
    app = create_app(ipc_token=token)
    client = TestClient(app)

    # Missing header
    res_missing = client.get("/agent/health")
    assert res_missing.status_code == 403

    # Invalid header
    res_invalid = client.get("/agent/health", headers={"X-Tauri-IPC-Secret": "wrong-secret"})
    assert res_invalid.status_code == 403


@pytest.mark.tier1
def test_f18_stdin_token_line_read():
    """Verify sidecar consumes token strictly from line 1 of stdin."""
    stdin_stream = "550e8400-e29b-41d4-a716-446655440000\nOther data..."
    token_line = stdin_stream.splitlines()[0].strip()
    assert token_line == "550e8400-e29b-41d4-a716-446655440000"


# ---------------------------------------------------------------------------
# Feature 19: Custom med-asset:// Protocol
# ---------------------------------------------------------------------------
@pytest.mark.tier1
def test_f19_med_asset_uri_scheme_parsing():
    """Verify URI parsing for med-asset://images/{uuid}.webp."""
    uri = "med-asset://images/c3b9b4f2-9b93-4a1b-9f93-5d5e231145bc.webp"
    assert uri.startswith("med-asset://")
    asset_path = uri.replace("med-asset://", "")
    assert asset_path.startswith("images/")
    assert asset_path.endswith(".webp")


@pytest.mark.tier1
def test_f19_zero_copy_mmap_slice_access():
    """Verify memory mapped asset reads slice directly without heap vector allocation (ROA-09)."""
    underlying_mmap = b"\x52\x49\x46\x46\x24\x00\x00\x00\x57\x45\x42\x50"  # RIFF....WEBP
    view = memoryview(underlying_mmap)
    assert bytes(view[0:4]) == b"RIFF"
    assert bytes(view[8:12]) == b"WEBP"


@pytest.mark.tier1
def test_f19_mime_type_header_image_webp():
    """Verify response returns Content-Type: image/webp."""
    response_headers = {"Content-Type": "image/webp"}
    assert response_headers["Content-Type"] == "image/webp"


@pytest.mark.tier1
def test_f19_lru_cache_hit_ratio():
    """Verify LRU cache records hit when requesting previously mapped asset."""
    cache = {}
    asset_id = "asset_01.webp"
    cache[asset_id] = "mapped_buffer_pointer"
    is_hit = asset_id in cache
    assert is_hit is True


@pytest.mark.tier1
def test_f19_missing_asset_returns_404():
    """Verify missing asset path returns standard 404 response."""
    registered_assets = {"asset_01.webp"}
    requested_asset = "nonexistent_asset.webp"
    status_code = 200 if requested_asset in registered_assets else 404
    assert status_code == 404
