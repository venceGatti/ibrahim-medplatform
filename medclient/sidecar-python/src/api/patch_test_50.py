with open('sdui_routes.py', 'r') as f:
    content = f.read()

import re
content = re.sub(r'verify_tauri_ipc_secret.*?hmac\.compare_digest\(str\(x_tauri_ipc_secret\), str\(expected_token\)\):', r'verify_tauri_ipc_secret(request: Request, x_tauri_ipc_secret: Optional[str] = Header(None)) -> None:\n    """Fail-closed verification of ephemeral IPC secret token passed via request header (ROA-23)."""\n    expected_token = getattr(request.app.state, "ipc_token", None) or os.environ.get("MEDCLIENT_IPC_TOKEN")\n    if not expected_token or not x_tauri_ipc_secret or not hmac.compare_digest(str(x_tauri_ipc_secret).encode("utf-8"), str(expected_token).encode("utf-8")):', content, flags=re.DOTALL)

with open('sdui_routes.py', 'w') as f:
    f.write(content)

with open('agentic_routes.py', 'r') as f:
    content = f.read()
content = re.sub(r'verify_ipc_token.*?hmac\.compare_digest\(str\(x_tauri_ipc_secret\), str\(expected_token\)\):', r'verify_ipc_token(request: Request, x_tauri_ipc_secret: Optional[str] = Header(None)) -> None:\n    """Verify ephemeral IPC secret passed via header strictly and unconditionally (ROA-23)."""\n    expected_token = getattr(request.app.state, "ipc_token", None) or os.environ.get("MEDCLIENT_IPC_TOKEN")\n    if not expected_token or not x_tauri_ipc_secret or not hmac.compare_digest(str(x_tauri_ipc_secret).encode("utf-8"), str(expected_token).encode("utf-8")):', content, flags=re.DOTALL)
with open('agentic_routes.py', 'w') as f:
    f.write(content)
