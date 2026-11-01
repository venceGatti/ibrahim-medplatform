"""
srs_generator/gemini_client.py

Client Asincrono per l'orchestrazione con Google Gemini API (Google AI Studio Free Tier).
Implementa controllo di concorrenza tramite asyncio.Semaphore(2), rispetto dei limiti RPM (15 RPM)
e backoff esponenziale automatico per garantire il vincolo di costo zero assoluto (0,00 €).
"""

from __future__ import annotations

import asyncio
import os
import random
import sys
from typing import Optional

from srs_catalog.models import SRSModuleDefinition
from srs_generator.synthesis_engine import DeterministicSynthesisEngine


class AsyncGeminiOrchestrator:
    """Orchestratore asincrono resiliente per le chiamate API Gemini a costo zero."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: str = "gemini-2.5-flash",
        max_concurrent_workers: int = 2,
    ) -> None:
        self.api_key: str = (api_key or os.environ.get("GEMINI_API_KEY", "")).strip()
        self.model_name: str = model_name
        self.semaphore = asyncio.Semaphore(max_concurrent_workers)
        self.is_offline_mode: bool = not bool(self.api_key)

    async def generate_chapter_dual_pass(self, module_def: SRSModuleDefinition) -> str:
        """
        Esegue il Dual-Pass per il capitolo:
        - Se offline o senza API key: sintesi deterministica ad alta fedeltà.
        - Se online con API key: sintesi tramite Gemini Free Tier con rate limiting e fallback resiliente.
        """
        if self.is_offline_mode:
            return DeterministicSynthesisEngine.generate_module_specification(module_def)

        async with self.semaphore:
            # Pausa fisiologica stocastica per non superare mai i 15 RPM del Free Tier
            await asyncio.sleep(random.uniform(4.0, 6.0))
            return await self._call_gemini_with_backoff(module_def)

    async def _call_gemini_with_backoff(self, module_def: SRSModuleDefinition, attempt: int = 1) -> str:
        """Invoca l'API Gemini con retry e backoff esponenziale in caso di 429 / 503."""
        if attempt > 3:
            sys.stderr.write(
                f"[GEMINI-CLIENT] Quota esaurita dopo {attempt} tentativi per Modulo {module_def.module_code}. "
                "Attivazione del fallback di sintesi deterministica offline.\n"
            )
            return DeterministicSynthesisEngine.generate_module_specification(module_def)

        try:
            # Tentativo di importazione del client Google GenAI ufficiale
            from google import genai
            client = genai.Client(api_key=self.api_key)

            prompt_content = (
                f"Agisci come Principal Medical Systems Architect & Sentinel QA Auditor per la Piattaforma Medica Ibrida.\n"
                f"Redigi la specifica tecnica formale ingegneristica per: '{module_def.titolo_capitolo}'.\n"
                f"Direttive vincolanti da sviluppare:\n{module_def.direttive}\n\n"
                f"Assunzioni Operative obbligatorie: {', '.join(module_def.applicable_roas)}.\n"
                "Vincoli: Markdown formale IEEE/ISO, schemi DDL SQLite STRICT, formule KaTeX, contratti Pydantic v2.\n"
                "Nessun mock, nessun convenevole, solo ingegneria pura e analisi dei rischi."
            )

            # Esecuzione nel threadpool per chiamate sincrone dell'SDK
            loop = asyncio.get_running_loop()
            response = await loop.run_in_executor(
                None,
                lambda: client.models.generate_content(
                    model=self.model_name,
                    contents=prompt_content,
                )
            )

            if hasattr(response, "text") and response.text:
                return response.text.strip()
            return DeterministicSynthesisEngine.generate_module_specification(module_def)

        except Exception as exc:
            err_msg = str(exc).lower()
            if any(marker in err_msg for marker in ["429", "quota", "resource_exhausted", "503", "overloaded"]):
                wait_time = (2 ** attempt) * 15 + random.uniform(1.0, 5.0)
                sys.stderr.write(
                    f"[GEMINI-CLIENT] Rate limit rilevato ({exc}). Backoff di {wait_time:.1f}s (Tentativo {attempt}/3)...\n"
                )
                await asyncio.sleep(wait_time)
                return await self._call_gemini_with_backoff(module_def, attempt + 1)

            sys.stderr.write(f"[GEMINI-CLIENT] Errore imprevisto ({exc}). Fallback su sintesi deterministica.\n")
            return DeterministicSynthesisEngine.generate_module_specification(module_def)
