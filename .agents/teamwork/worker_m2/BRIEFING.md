# BRIEFING — 2026-10-30T22:29:30Z

## Mission
Implement Milestone M2 (Features 13–15, 17–19) in `medclient/core-rust/`, fix compilation in supervisor.rs, implement Win32 Job Object, jemalloc tuning, memory throttling, ephemeral IPC handshake, med-asset:// mmap zero-copy streaming, and DPAPI encryption with zero warnings.

## 🔒 My Identity
- Archetype: implementer
- Roles: implementer, qa, specialist
- Working directory: c:\Users\vence\Downloads\projects\ibrahim\.agents\teamwork\worker_m2\
- Original parent: 123b80e3-ef7e-4eee-9c78-b41caaecc724
- Milestone: M2 (Features 13–15, 17–19)

## 🔒 Key Constraints
- Fix compilation failures in `medclient/core-rust/src/supervisor.rs` (compare HANDLE against null_mut and INVALID_HANDLE_VALUE).
- Structure `medclient/core-rust/` into `interfaces/`, `base/`, and `implementations/` (and `security/`) with strict 300-450 line limit.
- Pin all dependencies in `medclient/core-rust/Cargo.toml` to exact versions (`=x.y.z`).
- Eliminate unused imports and compiler warnings.
- Eliminate banned identifiers (`payload` -> `ipc_message_buffer`, `res` -> `win32_system_status`, etc.).
- Feature 13: Tauri v2 desktop host process lifecycle.
- Feature 14: Jemalloc memory tuner with `tikv-jemallocator` (`dirty_decay_ms = 1000`) keeping Rust RSS < 25MB.
- Feature 15: Win32 Job Object supervisor setting `JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE`.
- Feature 17: Memory throttling state machine (`Normal`, `Constrained`, `Critical`).
- Feature 18: Ephemeral IPC handshake: bind `127.0.0.1:0`, retrieve port, deliver UUIDv4 token via stdin line 1 without TOCTOU race conditions.
- Feature 19: Custom `med-asset://` protocol: true zero-copy mmap streaming using `memmap2::Mmap` (`MapViewOfFile`) with a bounded LRU cache (max 8 open maps).
- Windows DPAPI module in `security/` wrapping `CryptProtectData` and `CryptUnprotectData`.
- Strict write ownership: `medclient/core-rust/` exclusively. Do NOT edit `medfactory/`, `medclient/sidecar-python/`, or `tests/`.
- No mocks, no dummies, real genuine logic.

## Current Parent
- Conversation ID: 123b80e3-ef7e-4eee-9c78-b41caaecc724
- Updated: 2026-10-30T22:29:30Z

## Task Summary
- **What to build**: MedClient Core Rust features M2 (13-15, 17-19) + Win32 Job Object + DPAPI + Mmap streaming + Memory Throttle + Ephemeral IPC + Jemalloc tuning.
- **Success criteria**: cargo check, cargo clippy, and cargo test pass with zero warnings, all features implemented with clean modular architecture and unit tests.
- **Interface contracts**: PROJECT.md, AUDIT_AND_ASSUMPTIONS.md
- **Code layout**: interfaces/, base/, implementations/, security/

## Key Decisions Made
- All dependencies pinned to exact versions (`=x.y.z`) in `Cargo.toml`.
- Win32 Job Object supervisor fixed using pointer methods (`is_null()`, `INVALID_HANDLE_VALUE`), eliminating integer comparisons.
- Architecture modularized into `interfaces/`, `base/`, `implementations/`, `security/`, `supervisor/`, `protocols/`, `sidecar/`.
- Custom `med-asset://` zero-copy protocol implemented with bounded LRU cache (`BoundedMmapLruCache`, max 8 maps), wrapping `Mmap` in `AssetResponseBody::MmapSlice` with `Deref<Target = [u8]>`, completely avoiding heap allocation and `.to_vec()`.
- Windows DPAPI implemented via `CryptProtectData` and `CryptUnprotectData` using `CRYPT_INTEGER_BLOB` and `LocalFree`.
- Throttling state machine implemented querying physical Windows working set via `K32GetProcessMemoryInfo`.
- Ephemeral port handshake implemented with stdin token injection and TOCTOU elimination.
- All banned identifiers (`payload`, `res`, `data`, `item`, `val`, `mock`, etc.) eliminated.

## Artifact Index
- changes.md — Record of code modifications
- handoff.md — Final 5-component handoff report
- progress.md — Liveness heartbeat and progress log
- DISPATCH.md — Received dispatch instructions
- BRIEFING.md — Persistent context index

## Change Tracker
- **Files modified**:
  - `medclient/core-rust/Cargo.toml` — Exact pinned dependencies & added Windows cryptography/memory/process status features
  - `medclient/core-rust/src/lib.rs` — Exported modules with `#![deny(warnings)]`
  - `medclient/core-rust/src/main.rs` — Clean entrypoint & 8 comprehensive unit tests
  - `medclient/core-rust/src/supervisor.rs` — Fixed pointer comparison, Win32 Job Object
  - `medclient/core-rust/src/state.rs` — Re-exports throttling state machine
  - `medclient/core-rust/src/sidecar.rs` — Re-exports ephemeral handshake & process spawner
  - `medclient/core-rust/src/protocols/asset_protocol.rs` — Re-exports zero-copy asset handler
  - `medclient/core-rust/src/interfaces/traits.rs` — Interface traits (IJobSupervisor, IResourceSupervisor, etc.)
  - `medclient/core-rust/src/interfaces/mod.rs` — Interface module export
  - `medclient/core-rust/src/base/models.rs` — Core domain models & zero-copy AssetResponseBody
  - `medclient/core-rust/src/base/mod.rs` — Base module export
  - `medclient/core-rust/src/implementations/supervisor.rs` — Re-export of supervisor
  - `medclient/core-rust/src/implementations/jemalloc_tuner.rs` — Jemalloc tuner (dirty_decay_ms = 1000)
  - `medclient/core-rust/src/implementations/throttling.rs` — Working set query & 3-state throttling
  - `medclient/core-rust/src/implementations/sidecar.rs` — Port allocation, stdin injection, process spawn
  - `medclient/core-rust/src/implementations/asset_protocol.rs` — True zero-copy mmap & LRU cache (8 max)
  - `medclient/core-rust/src/implementations/dpapi.rs` — Win32 CryptProtectData / CryptUnprotectData wrapper
  - `medclient/core-rust/src/implementations/host_lifecycle.rs` — Tauri v2 desktop host lifecycle
  - `medclient/core-rust/src/implementations/mod.rs` — Implementations module export
  - `medclient/core-rust/src/security/dpapi_vault.rs` — DpapiSecretVault wrapper
  - `medclient/core-rust/src/security/mod.rs` — Security module export
- **Build status**: `cargo check`, `cargo clippy --all-targets -- -D warnings`, and `cargo test` ALL PASS with 0 warnings.
- **Pending issues**: None. All requirements satisfied.

## Quality Status
- **Build/test result**: PASS (8/8 unit tests pass)
- **Lint status**: 0 warnings under clippy -D warnings
- **Tests added/modified**: 8 comprehensive unit tests covering Job Object, Jemalloc tuner, DPAPI, LRU cache, Throttling, Handshake, Asset protocol, and Host lifecycle.

## Loaded Skills
- None
