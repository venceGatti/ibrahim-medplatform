"""
Main CLI Entrypoint for MedClient Python Sidecar.
Parses --port, reads ephemeral IPC token from stdin, and starts Uvicorn.
"""
import os
import sys
import argparse
import uvicorn
from src.api.server import create_app


def parse_arguments() -> argparse.Namespace:
    """Parse explicit command-line flags."""
    parser = argparse.ArgumentParser(
        description="MedClient High-Performance Python Sidecar Backend"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Ephemeral loopback port allocated by Tauri host",
    )
    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Loopback binding address (strictly 127.0.0.1)",
    )
    return parser.parse_args()


def read_stdin_ipc_token() -> str:
    """
    Read ephemeral IPC secret token from line 1 of stdin piped by Rust host.
    Falls back to MEDCLIENT_IPC_TOKEN environment variable if stdin is a tty.
    """
    ipc_token = ""
    if not sys.stdin.isatty():
        first_line = sys.stdin.readline()
        if first_line:
            ipc_token = first_line.strip()

    if not ipc_token:
        ipc_token = os.environ.get("MEDCLIENT_IPC_TOKEN", "")

    return ipc_token


def main() -> None:
    """Initialize application and start ASGI server."""
    arguments = parse_arguments()
    ipc_token = read_stdin_ipc_token()

    # Pass token to factory to set on app.state.ipc_token
    application = create_app(ipc_token=ipc_token)

    uvicorn.run(
        application,
        host=arguments.host,
        port=arguments.port,
        log_level="info",
        access_log=False,
    )


if __name__ == "__main__":
    main()
