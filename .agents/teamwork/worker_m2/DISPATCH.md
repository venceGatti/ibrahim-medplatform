## 2026-10-30T22:06:53Z
You are `worker_m2` (Role: MedClient Core Rust Engineer).

Your working directory is:
`c:\Users\vence\Downloads\projects\ibrahim\.agents\teamwork\worker_m2\`

You MUST read the original request before starting:
`c:\Users\vence\Downloads\projects\ibrahim\.agents\teamwork\ORIGINAL_REQUEST.md`

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Scope & Write Ownership:
You own `medclient/core-rust/` exclusively. You must NOT edit any files in `medfactory/`, `medclient/sidecar-python/`, or `tests/`.

Key References to read:
1. `c:\Users\vence\Downloads\projects\ibrahim\PROJECT.md`
2. `c:\Users\vence\Downloads\projects\ibrahim\.agents\teamwork\AUDIT_AND_ASSUMPTIONS.md`
3. `c:\Users\vence\Downloads\projects\ibrahim\.agents\teamwork\explorer_audit_1\code_audit.md`
4. `c:\Users\vence\Downloads\projects\ibrahim\.agents\teamwork\spec_miner_1\spec_inventory.md`

Toolchain:
Rust 1.95.0, `cargo`, `rustc`.

Your Objectives (Milestone M2 - Features 13–15, 17–19):
1. Fix the compilation failures in `medclient/core-rust/src/supervisor.rs`:
   - Fix type mismatch at lines 20 and 68: compare `HANDLE` (`*mut c_void`) against `std::ptr::null_mut()` and `winapi::um::handleapi::INVALID_HANDLE_VALUE`, eliminating `usize` literal checks.
2. Structure `medclient/core-rust/` into `interfaces/`, `base/`, and `implementations/` with strict 300-450 line limit per file:
   - Pin all dependencies in `medclient/core-rust/Cargo.toml` to exact versions (`=x.y.z`).
   - Eliminate unused imports and warnings.
   - Eliminate banned identifiers (`payload` -> `ipc_message_buffer`, `res` -> `win32_system_status`).
3. Fully implement Features 13–15, 17–19:
   - Feature 13: Tauri v2 desktop host process lifecycle.
   - Feature 14: Jemalloc memory tuner with `tikv-jemallocator` (`dirty_decay_ms = 1000`) keeping Rust RSS < 25MB.
   - Feature 15: Win32 Job Object supervisor setting `JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE` so child processes are killed within 500ms if Tauri crashes.
   - Feature 17: Memory throttling state machine (`Normal`, `Constrained`, `Critical`).
   - Feature 18: Ephemeral IPC handshake: bind `127.0.0.1:0`, retrieve port, deliver UUIDv4 token via line 1 of stdin to the Python sidecar without TOCTOU race conditions.
   - Feature 19: Custom `med-asset://` protocol: true zero-copy mmap streaming using `memmap2::Mmap` (`MapViewOfFile`) with a bounded LRU cache (max 8 open maps), passing raw memory slices to WebView2 without `to_vec()` heap copies.
4. Implement Windows DPAPI module (`security/`):
   - Wrap Win32 `CryptProtectData` and `CryptUnprotectData` to safely encrypt and decrypt tokens and secrets.
5. Run `cargo check` and `cargo test` in `medclient/core-rust/`, verifying passing tests and clean compilation with zero warnings.
6. Write your detailed report in `c:\Users\vence\Downloads\projects\ibrahim\.agents\teamwork\worker_m2\changes.md` and handoff report in `c:\Users\vence\Downloads\projects\ibrahim\.agents\teamwork\worker_m2\handoff.md`.
7. Send a message to your caller when finished. Remember you MUST use send_message.
