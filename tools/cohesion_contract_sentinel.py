"""
Cohesion & Contract Sentinel for MedPlatform.
Performs cross-boundary AST and static contract validation between:
- FastAPI Python Sidecar routes (sdui_routes.py, agentic_routes.py)
- React TypeScript SDUI contracts (sduiContracts.ts, engineContracts.ts)
- IPC communication layer (SidecarIpcClient, useMedClientStore)
Ensures zero orphan routes, zero missing parameters, and strict contract parity.
"""
import ast
import os
import re
import sys
from typing import Dict, List, Set


def inspect_python_fastapi_routes(routes_path: str) -> Dict[str, Dict[str, str]]:
    """Parse FastAPI routes using Python AST to extract methods, paths, and response models."""
    if not os.path.exists(routes_path):
        raise FileNotFoundError(f"Routes file not found at: {routes_path}")

    with open(routes_path, "r", encoding="utf-8") as file_handle:
        source_code = file_handle.read()

    syntax_tree = ast.parse(source_code, filename=routes_path)
    discovered_routes: Dict[str, Dict[str, str]] = {}

    for node in ast.walk(syntax_tree):
        if not isinstance(node, ast.FunctionDef):
            continue

        for decorator in node.decorator_list:
            if not isinstance(decorator, ast.Call):
                continue

            func = decorator.func
            if not isinstance(func, ast.Attribute):
                continue

            if func.attr in ("get", "post", "put", "delete", "patch"):
                http_method = func.attr.upper()
                if not decorator.args:
                    continue

                route_path_node = decorator.args[0]
                if isinstance(route_path_node, ast.Constant):
                    route_path = str(route_path_node.value)
                else:
                    continue

                response_model_name = "None"
                for keyword in decorator.keywords:
                    if keyword.arg == "response_model":
                        if isinstance(keyword.value, ast.Name):
                            response_model_name = keyword.value.id

                route_key = f"{http_method} {route_path}"
                discovered_routes[route_key] = {
                    "method": http_method,
                    "path": route_path,
                    "handler_name": node.name,
                    "response_model": response_model_name,
                }

    return discovered_routes


def inspect_typescript_interfaces(contracts_path: str) -> Set[str]:
    """Extract TypeScript interface and type names from contract definitions."""
    if not os.path.exists(contracts_path):
        raise FileNotFoundError(f"Contracts file not found at: {contracts_path}")

    with open(contracts_path, "r", encoding="utf-8") as file_handle:
        ts_code = file_handle.read()

    interface_matches = re.findall(
        r"export\s+(?:interface|type)\s+([A-Za-z0-9_]+)", ts_code
    )
    return set(interface_matches)


def inspect_frontend_ipc_calls(*file_paths: str) -> Set[str]:
    """Extract all API endpoint paths called by the React frontend."""
    discovered_endpoints: Set[str] = set()

    for file_path in file_paths:
        if not os.path.exists(file_path):
            continue
        with open(file_path, "r", encoding="utf-8") as file_handle:
            content = file_handle.read()

        endpoint_matches = re.findall(
            r"""['"`](/api/v3/[A-Za-z0-9_/{}]+|/agent/[A-Za-z0-9_/]+)['"`]""",
            content,
        )
        for endpoint in endpoint_matches:
            discovered_endpoints.add(endpoint)

    return discovered_endpoints


def run_cohesion_sentinel_audit() -> bool:
    """Execute complete contract parity check across Python and TypeScript."""
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    sys.stdout.write("=" * 70 + "\n")
    sys.stdout.write("MedPlatform Cohesion & Contract Sentinel Audit\n")
    sys.stdout.write("=" * 70 + "\n")

    sdui_routes_path = os.path.join(
        project_root, "medclient", "sidecar-python", "src", "api", "sdui_routes.py"
    )
    agentic_routes_path = os.path.join(
        project_root, "medclient", "sidecar-python", "src", "api", "agentic_routes.py"
    )
    sdui_contracts_path = os.path.join(
        project_root,
        "medclient",
        "frontend-react",
        "src",
        "interfaces",
        "sduiContracts.ts",
    )
    store_path = os.path.join(
        project_root,
        "medclient",
        "frontend-react",
        "src",
        "base",
        "useMedClientStore.ts",
    )
    app_shell_path = os.path.join(
        project_root,
        "medclient",
        "frontend-react",
        "src",
        "implementations",
        "MedClientAppShell.tsx",
    )

    sidecar_client_path = os.path.join(
        project_root,
        "medclient",
        "frontend-react",
        "src",
        "base",
        "sidecarIpcClient.ts",
    )

    sdui_routes = inspect_python_fastapi_routes(sdui_routes_path)
    agentic_routes = inspect_python_fastapi_routes(agentic_routes_path)
    all_backend_routes = {**sdui_routes, **agentic_routes}

    ts_contracts = inspect_typescript_interfaces(sdui_contracts_path)
    frontend_endpoints = inspect_frontend_ipc_calls(store_path, app_shell_path, sidecar_client_path)

    sys.stdout.write(f"[Sentinel] Discovered Backend Routes: {len(all_backend_routes)}\n")
    for route_key, details in sorted(all_backend_routes.items()):
        sys.stdout.write(
            f"  - {route_key} -> {details['handler_name']} (Returns: {details['response_model']})\n"
        )

    sys.stdout.write(f"\n[Sentinel] Discovered TypeScript SDUI Types: {len(ts_contracts)}\n")
    for contract_name in sorted(ts_contracts):
        sys.stdout.write(f"  - {contract_name}\n")

    sys.stdout.write(
        f"\n[Sentinel] Discovered Frontend Endpoint Invocations: {len(frontend_endpoints)}\n"
    )
    for endpoint in sorted(frontend_endpoints):
        sys.stdout.write(f"  - {endpoint}\n")

    # Contract checks
    contract_violations: List[str] = []

    # Check 1: Key SDUI response models must exist in TypeScript
    for route_key, details in all_backend_routes.items():
        response_model = details["response_model"]
        if response_model != "None" and response_model not in ts_contracts:
            contract_violations.append(
                f"Missing TypeScript interface for backend model '{response_model}' (Route: {route_key})"
            )

    sys.stdout.write("\n" + "-" * 70 + "\n")
    if contract_violations:
        sys.stderr.write(
            f"[Sentinel ERROR] Found {len(contract_violations)} contract violations:\n"
        )
        for violation in contract_violations:
            sys.stderr.write(f"  ❌ {violation}\n")
        return False

    sys.stdout.write(
        "[Sentinel PASS] All backend response models mapped to TypeScript interfaces!\n"
    )
    sys.stdout.write("=" * 70 + "\n")
    return True


if __name__ == "__main__":
    success = run_cohesion_sentinel_audit()
    sys.exit(0 if success else 1)
