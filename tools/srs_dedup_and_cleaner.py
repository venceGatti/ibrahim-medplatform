#!/usr/bin/env python3
"""
tools/srs_dedup_and_cleaner.py

Utility di bonifica e deduplicazione preliminare per SRS_MedClient_Architettura_Completa.md.
Esegue il backup crittografico del documento in .bak e rimuove la sequenza duplicata storica
presente nelle prime 1.254 righe (bozza preliminare dei Moduli 1.1 - 1.3 che riparte a riga 1.255).
"""

from __future__ import annotations

import hashlib
import shutil
import sys
from pathlib import Path


def calculate_sha256(file_path: Path) -> str:
    """Calcola l'hash crittografico SHA-256 di un file specificato."""
    hasher = hashlib.sha256()
    with open(file_path, "rb") as stream_handle:
        for chunk_buffer in iter(lambda: stream_handle.read(65536), b""):
            hasher.update(chunk_buffer)
    return hasher.hexdigest()


def execute_srs_deduplication(target_file_path: Path) -> int:
    """
    Ispeziona il file SRS, esegue il backup .bak e rimuove le prime 1.254 righe duplicate
    se la linea sentinella di restart del documento viene identificata con successo.
    """
    if not target_file_path.exists():
        sys.stderr.write(f"ERRORE: File target {target_file_path} non trovato.\n")
        return 1

    backup_file_path = target_file_path.with_suffix(".md.bak")
    shutil.copy2(target_file_path, backup_file_path)
    initial_sha = calculate_sha256(target_file_path)
    print(f"[SRS-CLEANER] Backup eseguito con successo: {backup_file_path}")
    print(f"[SRS-CLEANER] SHA-256 file originario: {initial_sha}")

    with open(target_file_path, "r", encoding="utf-8") as file_read_handle:
        raw_lines = file_read_handle.readlines()

    total_lines = len(raw_lines)
    print(f"[SRS-CLEANER] Conteggio totale righe rilevate: {total_lines}")

    # Verifica sentinella riga 1254-1255: cerca il secondo avvio di "## Modulo 1.1:"
    restart_index = -1
    for line_idx in range(500, min(2000, total_lines)):
        line_content = raw_lines[line_idx].strip()
        if line_content.startswith("## Modulo 1.1:"):
            restart_index = line_idx
            break

    if restart_index == -1:
        print("[SRS-CLEANER] Nessun punto di restart duplicato rilevato nell'intervallo 100-1500. Nessuna riga tagliata.")
        return 0

    print(f"[SRS-CLEANER] Punto di restart identificato alla riga {restart_index + 1}. Rimozione delle prime {restart_index - 8} righe duplicate interne.")
    cleaned_lines = raw_lines[:8] + ["\n"] + raw_lines[restart_index:]

    with open(target_file_path, "w", encoding="utf-8", newline="\n") as file_write_handle:
        file_write_handle.writelines(cleaned_lines)

    final_sha = calculate_sha256(target_file_path)
    print(f"[SRS-CLEANER] Bonifica completata. Nuove righe: {len(cleaned_lines)} (rimosse {restart_index} righe).")
    print(f"[SRS-CLEANER] SHA-256 file bonificato: {final_sha}")
    return 0


if __name__ == "__main__":
    srs_path = Path("SRS_MedClient_Architettura_Completa.md").resolve()
    exit_code = execute_srs_deduplication(srs_path)
    sys.exit(exit_code)
