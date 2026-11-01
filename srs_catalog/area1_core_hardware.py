"""
srs_catalog/area1_core_hardware.py

Area 1: Fondamenta Hardware, OS, Storage & Core Engine (Moduli 1.1 - 1.5).
Copertura vincolante: ROA-01, ROA-05, ROA-06, ROA-07, ROA-08, ROA-09, ROA-13, ROA-18, ROA-19, ROA-20, ROA-22, ROA-23, ROA-24, ROA-25.
"""

from __future__ import annotations

from typing import List
from srs_catalog.models import SRSModuleDefinition


AREA1_MODULES: List[SRSModuleDefinition] = [
    SRSModuleDefinition(
        module_code="1.1",
        titolo_capitolo="Modulo 1.1: Profilazione Hardware Target, Asimmetria MedFactory/MedClient e Limiti di Risorse",
        area_name="Area 1: Fondamenta Hardware, OS & Core Engine",
        applicable_roas=["ROA-01", "ROA-08", "ROA-22"],
        direttive="""
Redigere la specifica tecnica ingegneristica per il Modulo 1.1: Profilazione Hardware e Asimmetria del Sistema.
Direttive vincolanti da sviluppare in dettaglio:
1. Systems Architect:
   - Definire i profili hardware asimmetrici: MedFactory (Build-Time su GPU NVIDIA RTX 4050 6GB VRAM, CPU AMD Ryzen 7) e MedClient (Run-Time su CPU Intel Core i7, 8-16 GB RAM condivisa UMA, NESSUNA GPU dedicata).
   - Fissare i vincoli operativi rigidi sul MedClient: budget RAM resident set size (RSS) < 300 MB complessivi tramite Win32 Job Object, latenza di risposta alle query < 50 ms.
   - Spiegare perché il paradigma client-server domestico asincrono (WAN tra PC personali) e stato scartato a favore della totale disconnessione runtime con distribuzione a pacchetti statici (.medpack).
2. Medical AI Specialist:
   - Dimostrare l'incompatibilita dei modelli LLM generativi locali sul client per la generazione di schede cliniche (collasso RAM a 4.94GB, lentezza >15s, allucinazioni posologiche letali).
   - Definire il ruolo dell'AI sul client: inferenza deterministica, ricerca semantica ultraleggera e modelli discriminativi NLI compilati in ONNX Runtime.
3. QA Critic:
   - Analizzare i punti di rottura hardware: scenari di esaurimento memoria (RAM bloat) su macchine con 8 GB condivisi con grafica integrata Iris Xe.
   - Definire i protocolli di throttling automatico e le policy di degradazione delle prestazioni in caso di esecuzione su batteria o carico di sistema > 80%.
4. Technical Writer:
   - Redigere in Markdown formale con tabelle comparative hardware, vincoli prestazionali e requisiti funzionali/non-funzionali misurabili conformi a ROA-01 e ROA-22.
""",
    ),
    SRSModuleDefinition(
        module_code="1.2",
        titolo_capitolo="Modulo 1.2: Packaging .medpack, Compressione Zstd a Doppio Livello e Firma Ed25519",
        area_name="Area 1: Fondamenta Hardware, OS & Core Engine",
        applicable_roas=["ROA-05", "ROA-06", "ROA-18", "ROA-19"],
        direttive="""
Redigere la specifica tecnica ingegneristica per il Modulo 1.2: Pipeline di Packaging, Compressione Zstd e Verifica Crittografica.
Direttive vincolanti da sviluppare in dettaglio:
1. Systems Architect:
   - Definire l'anatomia interna del container `.medpack`: framing esterno .tar.zst privo di dizionario (dictionary-free, ROA-18) compresso a Livello 19 per evitare deadlock di decompressione circolare.
   - Dettagliare il dizionario Zstandard specializzato `zstd.dict` addestrato sul 10% del corpus medico con dimensione binaria esatta di 114.688 Byte (112 KB, ROA-05) per la decompressione interna a > 1.2 GB/s.
   - Specificare la pipeline deterministica e riproducibile: normalizzazione timestamp a Unix Epoch 0, ordinamento lessicografico dei file, deframmentazione SQLite con VACUUM INTO.
2. Medical AI Specialist:
   - Specificare il contenuto del pacchetto: `manifest.json`, `manifest.sig`, `zstd.dict` (114.688 B), `database/module_kb.sqlite`, `vector_index/index.bin`, `media/{sha256}.webp` e `.svg`.
   - Modello canonico `MedPackManifest` con dual-alias formale (ROA-19) e calcolo della firma Ed25519 sul payload JSON canonico normalizzato.
3. QA Critic:
   - Analizzare i rischi di corruzione dati, race condition durante l'estrazione e manomissione di pacchetti non firmati.
   - Definire la validazione fail-closed: verifica crittografica sia dell'hash BLAKE3 (velocita di streaming) sia dell'hash SHA-256 (audit e compliance, ROA-06) con verifica firma Ed25519.
4. Technical Writer:
   - Includere lo schema JSON completo del `manifest.json`, diagrammi di flusso ASCII del packaging e tabelle dei benchmark di compressione Zstd Level 19.
""",
    ),
    SRSModuleDefinition(
        module_code="1.3",
        titolo_capitolo="Modulo 1.3: Host Engine Tauri/Rust, Protocollo Zero-Copy med-asset:// e Sicurezza Loopback",
        area_name="Area 1: Fondamenta Hardware, OS & Core Engine",
        applicable_roas=["ROA-08", "ROA-22", "ROA-23", "ROA-25"],
        direttive="""
Redigere la specifica tecnica per il Modulo 1.3: Architettura Host Tauri/Rust, Protocollo Custom Asset e Sicurezza IPC.
Direttive vincolanti da sviluppare in dettaglio:
1. Systems Architect:
   - Dettagliare l'accoppiamento tra il core Rust (Tauri 2.x), il frontend React/TypeScript e il sidecar Python (FastAPI).
   - Implementazione del Custom Asset Protocol nativo in Rust (`med-asset://`): mappatura della memoria virtuale via `memmap2` direttamente dallo storage su disco alla texture GPU della WebView2 a zero copie di memoria (ROA-22).
   - Divieto assoluto di trasporto Base64 e divieto di invocazione di `.to_vec()` o riallocazioni nell'heap Rust.
   - Allocazione dinamica della porta TCP su loopback locale (127.0.0.1) e generazione all'avvio di un token crittografico effimero UUIDv4 passato via stdin, con validazione dell'header `X-Tauri-IPC-Secret` in tempo costante (ROA-08, ROA-23).
2. Medical AI Specialist:
   - Bando assoluto di connessioni esterne a runtime per strutture molecolari o immagini (ROA-25): fruizione locale da `assets/pdb/*.pdb` e `media/{sha256}.svg` tramite `med-asset://`.
   - Preservazione del profilo colore sRGB e conversione WebP near-lossless per preparati istologici e dermatologici.
3. QA Critic:
   - Identificazione di vulnerabilita SSRF/CSRF locali: protezione fail-closed per cui qualsiasi richiesta priva di `X-Tauri-IPC-Secret` riceve HTTP 401/403 (ROA-23).
   - Prevenzione TOCTOU sulla porta TCP e verifica della latenza IPC end-to-end (< 15 ms).
4. Technical Writer:
   - Fornire il diagramma di sequenza IPC dell'handshake di avvio, le firme dei metodi Rust e i contratti HTTP/REST.
""",
    ),
    SRSModuleDefinition(
        module_code="1.4",
        titolo_capitolo="Modulo 1.4: Architettura SQLite WAL a Doppio Livello, Schema STRICT e Blue/Green Swap via JSON Pointer",
        area_name="Area 1: Fondamenta Hardware, OS & Core Engine",
        applicable_roas=["ROA-07", "ROA-09", "ROA-13", "ROA-20"],
        direttive="""
Redigere la specifica tecnica per il Modulo 1.4: Persistenza Relazionale SQLite a Doppio Livello e Resilienza Atomica.
Direttive vincolanti da sviluppare in dettaglio:
1. Systems Architect:
   - Separazione fisica assoluta dei due database locali (ROA-13): `module_kb.sqlite` (Knowledge Layer immutabile, read-only con PRAGMA query_only = ON) e `user_state.sqlite` (User Layer mutabile per metriche FSRS, note personali e log esami).
   - Titolarita esclusiva del database in capo al sidecar Python (ROA-09): Rust non apre connessioni concorrenti, azzerando i conflitti `SQLITE_BUSY` ed `ERROR_SHARING_VIOLATION`.
   - Procedura di Blue/Green Atomic Swap su Windows tramite file puntatore `active_db.json` con `ReplaceFileW` / `MoveFileExW` senza symlink NTFS (ROA-07).
   - Configurazione PRAGMA di sicurezza: PRAGMA journal_mode = WAL;, PRAGMA synchronous = NORMAL;, PRAGMA busy_timeout = 5000;.
2. Medical AI Specialist:
   - Adozione obbligatoria della clausola SQLite `STRICT` su tutte le tabelle relazionali (ROA-20).
   - Schemi DDL completi per `module_kb.sqlite` (`diseases`, `symptoms`, `substances`, `interactions`, `cyp_profiles`, `exam_items`) e `user_state.sqlite` (`fsrs_cards`, `review_logs`, `exam_sessions`, `user_bookmarks`).
3. QA Critic:
   - Analisi della resilienza a crash di alimentazione (Self-Healing Boot con PRAGMA quick_check e recovery automatico WAL).
   - Assicurare che durante il Blue/Green swap lo `user_state.sqlite` non venga MAI sovrascritto ne alterato (ROA-13).
4. Technical Writer:
   - Includere gli script DDL SQL completi con vincoli STRICT, indici compositi e diagramma ER relazionale a due livelli.
""",
    ),
    SRSModuleDefinition(
        module_code="1.5",
        titolo_capitolo="Modulo 1.5: Meccanismo di Reverse Watchdog Bidirezionale, Job Objects Win32 e Prevenzione Processi Zombie",
        area_name="Area 1: Fondamenta Hardware, OS & Core Engine",
        applicable_roas=["ROA-08", "ROA-22", "ROA-24"],
        direttive="""
Redigere la specifica tecnica per il Modulo 1.5: Supervisione dei Processi, Reverse Watchdog e Isolamento Win32 Job Object.
Direttive vincolanti da sviluppare in dettaglio:
1. Systems Architect:
   - Architettura del supervisore di processo Win32 Job Object in Rust: associazione di Tauri e del sidecar Python a un singolo Job Object con flag `JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE`.
   - Monitoraggio continuo dell'impronta di memoria tramite `QueryInformationJobObject` per garantire che la somma del Working Set rimanga rigorosamente < 300 MB RSS (ROA-22).
   - Implementazione del Reverse Watchdog in Python: thread daemon in background che interroga il PID genitore tramite `kernel32.WaitForSingleObject` e termina istantaneamente il sidecar con `os._exit(0)` se Tauri collassa o viene chiuso forzatamente (ROA-08).
2. Medical AI Specialist:
   - Gestione delle terminazioni pulite: flushing dei log di studio e delle metriche FSRS pendenti su `user_state.sqlite` prima del completamento dell'uscita.
   - Standardizzazione delle eccezioni di sistema: gerarchia formale `MedClientError(ValueError)` per gestire crash di runtime (ROA-24).
3. QA Critic:
   - Stress test di terminazione anomala: kill forzato del processo padre da Task Manager e verifica dell'azzeramento di processi orfani / zombie in < 200 ms.
   - Gestione delle condizioni di stallo IPC (deadlock socket o loop bloccanti) con timer di grace period a 500 ms e SIGKILL forzato.
4. Technical Writer:
   - Fornire il codice di implementazione Win32 Rust/Python per il Job Object e il Reverse Watchdog con diagrammi di stato del ciclo di vita.
""",
    ),
]

