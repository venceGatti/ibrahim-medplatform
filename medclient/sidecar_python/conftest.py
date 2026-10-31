"""Conftest for sidecar-python ensuring src namespace includes sidecar-python/src."""
import os
import sys

sidecar_dir = os.path.abspath(os.path.dirname(__file__))
sidecar_src = os.path.join(sidecar_dir, "src")

while sidecar_dir in sys.path:
    sys.path.remove(sidecar_dir)
sys.path.insert(0, sidecar_dir)

if "src" in sys.modules:
    src_module = sys.modules["src"]
    if hasattr(src_module, "__path__") and sidecar_src not in src_module.__path__:
        src_module.__path__.insert(0, sidecar_src)
