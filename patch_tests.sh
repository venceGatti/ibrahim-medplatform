cd medclient/sidecar-python/src/api
cat << 'INJECT' > fix_hmac.patch
--- agentic_routes.py
+++ agentic_routes.py
@@ -62,7 +62,7 @@
 def verify_ipc_token(request: Request, x_tauri_ipc_secret: Optional[str] = Header(None)) -> None:
     """Verify ephemeral IPC secret passed via header strictly and unconditionally (ROA-23)."""
     expected_token = getattr(request.app.state, "ipc_token", None) or os.environ.get("MEDCLIENT_IPC_TOKEN")
-    if not expected_token or not x_tauri_ipc_secret or not hmac.compare_digest(str(x_tauri_ipc_secret), str(expected_token)):
+    if not expected_token or not x_tauri_ipc_secret or not hmac.compare_digest(str(x_tauri_ipc_secret).encode("utf-8"), str(expected_token).encode("utf-8")):
         raise HTTPException(
             status_code=status.HTTP_403_FORBIDDEN,
             detail="Invalid or missing X-Tauri-IPC-Secret token",
INJECT
patch -p0 < fix_hmac.patch
