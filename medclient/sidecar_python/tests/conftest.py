"""Conftest for sidecar-python tests adding root src to sys.path and sys.modules."""
import os
import sys

sidecar_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sidecar_src = os.path.join(sidecar_dir, "src")

while sidecar_dir in sys.path:
    sys.path.remove(sidecar_dir)
sys.path.insert(0, sidecar_dir)

if "src" not in sys.modules:
    import src
else:
    src_module = sys.modules["src"]
    if hasattr(src_module, "__path__") and sidecar_src not in src_module.__path__:
        src_module.__path__.insert(0, sidecar_src)
