"""
Funzioni di hashing crittografico e serializzazione canonica per il packaging .medpack (ROA-06, ROA-19).
"""

import hashlib
import json
from pathlib import Path
from typing import Dict, Any
import blake3


def compute_file_blake3_hash(file_path: Path) -> str:
    """Calcola l'hash BLAKE3 a 64 caratteri esadecimali in streaming."""
    hasher = blake3.blake3()
    with open(file_path, "rb") as stream_handle:
        while stream_chunk := stream_handle.read(65536):
            hasher.update(stream_chunk)
    return hasher.hexdigest()


def compute_file_sha256_hash(file_path: Path) -> str:
    """Calcola l'hash SHA-256 a 64 caratteri esadecimali in streaming."""
    hasher = hashlib.sha256()
    with open(file_path, "rb") as stream_handle:
        while stream_chunk := stream_handle.read(65536):
            hasher.update(stream_chunk)
    return hasher.hexdigest()


def serialize_canonical_manifest_for_signing(manifest_dictionary: Dict[str, Any]) -> bytes:
    """
    Restituisce i byte UTF-8 del JSON canonico (sort_keys=True, separatori compatti)
    con signature_ed25519 impostato a stringa vuota "".
    """
    signing_copy = dict(manifest_dictionary)
    signing_copy["signature_ed25519"] = ""
    return json.dumps(signing_copy, sort_keys=True, separators=(",", ":")).encode("utf-8")
