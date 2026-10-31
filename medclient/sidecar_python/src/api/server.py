"""FastAPI Application Server Factory and Lifespan Manager."""
import os
import sys
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .agentic_routes import router as agentic_router
from .sdui_routes import router as sdui_router
from ..implementations.reverse_watchdog import ReverseWatchdog
from ..implementations.sqlite_pool import SqliteConnectionPool
from ..implementations.blue_green_swap import BlueGreenHotSwap
from ..implementations.red_flags import RedFlagsInterceptor
from ..implementations.symspell_checker import MedicalSymSpellChecker
from ..implementations.inverted_dictionary import InvertedLexicalDictionary
from ..implementations.csr_ranker import SparseCSRLogOddsRanker
from ..implementations.cyp450_engine import CYP450Engine


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Sidecar lifecycle: initializes reverse watchdog and SQLite pool."""
    # 1. Reverse watchdog setup
    parent_pid_env = os.environ.get("MEDCLIENT_PARENT_PID")
    if parent_pid_env:
        try:
            parent_pid = int(parent_pid_env)
            watchdog = ReverseWatchdog()
            watchdog.start(parent_pid)
            app.state.watchdog = watchdog
        except Exception as watchdog_startup_error:
            sys.stderr.write(f"[ServerLifespan] Failed to initialize reverse watchdog: {watchdog_startup_error}\n")

    # 2. Database hot swap & pool setup
    config_dir = os.environ.get("MEDCLIENT_CONFIG_DIR", os.path.expandvars(r"%LOCALAPPDATA%\MedPlatform\config"))
    pointer_path = os.path.join(config_dir, "active_db.json")
    hot_swap = BlueGreenHotSwap(pointer_path)
    app.state.hot_swap = hot_swap
    app.state.active_slot = hot_swap.get_active_slot()
    app.state.active_db_path = hot_swap.get_active_db_path()

    db_path = app.state.active_db_path
    if db_path and os.path.exists(db_path):
        app.state.db_pool = SqliteConnectionPool(db_path)
        ranker = SparseCSRLogOddsRanker()
        try:
            ranker.load_from_database(app.state.db_pool)
            app.state.csr_ranker = ranker
        except Exception as ranker_init_err:
            sys.stderr.write(f"[ServerLifespan] Failed to load CSR ranker from SQLite: {ranker_init_err}\n")
            app.state.csr_ranker = None
        app.state.cyp_engine = CYP450Engine(db_pool=app.state.db_pool)
    else:
        app.state.db_pool = None
        app.state.csr_ranker = None
        app.state.cyp_engine = CYP450Engine()

    # 3. Engines
    app.state.red_flags_interceptor = RedFlagsInterceptor()
    app.state.spellchecker = MedicalSymSpellChecker()
    app.state.inverted_dict = InvertedLexicalDictionary()
    app.state.alert_level = "NOMINAL"
    app.state.session_count = 0

    yield

    # Clean shutdown
    if getattr(app.state, "db_pool", None):
        app.state.db_pool.close_all()
    if getattr(app.state, "watchdog", None):
        app.state.watchdog.stop()


def create_app(ipc_token: str = "") -> FastAPI:
    """Create and configure FastAPI sidecar instance."""
    app = FastAPI(
        title="MedClient Sidecar Backend",
        version="1.0.0",
        description="High-performance offline medical knowledge, diagnostic, and pharmacology sidecar.",
        lifespan=lifespan,
    )

    app.state.ipc_token = ipc_token

    # Restrict to loopback CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://127.0.0.1", "http://localhost", "tauri://localhost"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(agentic_router)
    app.include_router(sdui_router)

    return app


app = create_app()
