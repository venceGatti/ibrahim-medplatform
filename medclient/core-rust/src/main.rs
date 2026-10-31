#![deny(warnings)]

use medclient_core::base::models::{MediaVaultConfig, ThrottlingState};
use medclient_core::implementations::host_lifecycle::HostProcessLifecycle;
use medclient_core::implementations::jemalloc_tuner::{JemallocMemoryTuner, MemoryTunerConfig};
use medclient_core::implementations::sidecar::allocate_ephemeral_port_and_token;
use medclient_core::implementations::supervisor::Win32JobSupervisor;
use medclient_core::implementations::throttling::SystemResourceSupervisor;
use medclient_core::interfaces::traits::{IDpapiVault, IJobSupervisor};
use medclient_core::protocols::asset_protocol::handle_med_asset_request;
use medclient_core::security::dpapi_vault::DpapiSecretVault;

fn main() {
    println!("MedClient Core Rust Engine Initialized.");

    let handshake_configuration = allocate_ephemeral_port_and_token()
        .expect("Impossibile allocare configurazione handshake");
    println!("Ephemeral Port: {}", handshake_configuration.ephemeral_port);
    println!("Token UUID: {}", handshake_configuration.token);
    println!(
        "TLV Handshake Buffer bytes: {}",
        handshake_configuration.ipc_message_buffer.len()
    );

    let job_supervisor =
        Win32JobSupervisor::new().expect("Impossibile inizializzare Win32 Job Supervisor");
    let is_job_active = IJobSupervisor::is_active(&job_supervisor);
    println!(
        "Win32 Job Supervisor attivo (JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE): {}",
        is_job_active
    );

    let mut resource_supervisor = SystemResourceSupervisor::new(300);
    let initial_throttling_state = resource_supervisor.evaluate_memory_state(45);
    println!(
        "Stato iniziale di Throttling: {:?}",
        initial_throttling_state
    );
    if initial_throttling_state == ThrottlingState::Normal {
        println!("Condizione di memoria nominale confermata.");
    }

    let media_probe_config = MediaVaultConfig::new(std::path::PathBuf::from("media"));
    let probe_outcome = handle_med_asset_request(
        &media_probe_config,
        "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
    );
    println!(
        "Probe med-asset status: {:?}",
        probe_outcome.map(|response| response.status_code)
    );

    let mut memory_tuner = JemallocMemoryTuner::new(MemoryTunerConfig::default());
    if let Err(error_message) = memory_tuner.apply_tuning() {
        eprintln!("Avviso configurazione Memory Tuner: {}", error_message);
    } else {
        println!(
            "Memory Tuner configurato con dirty_decay_ms = {} (epoch = {})",
            memory_tuner.configuration().dirty_decay_ms,
            memory_tuner.purge_epoch_counter()
        );
    }

    let dpapi_vault = DpapiSecretVault::new();
    let secret_seed = b"medclient-ephemeral-vault-seed";
    match dpapi_vault.encrypt_secret(secret_seed) {
        Ok(encrypted_bytes) => {
            println!(
                "Windows DPAPI crittografia attiva (bytes: {})",
                encrypted_bytes.len()
            );
        }
        Err(error_message) => {
            eprintln!("Avviso DPAPI: {}", error_message);
        }
    }

    let mut host_lifecycle = HostProcessLifecycle::new();
    if let Err(error_message) = host_lifecycle.initialize_host() {
        eprintln!("Inizializzazione Host Lifecycle: {}", error_message);
    } else {
        println!(
            "Host Process Lifecycle inizializzato con successo: {:?}",
            host_lifecycle.phase()
        );
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use medclient_core::implementations::asset_protocol::acquire_shared_asset_handler;
    use medclient_core::implementations::sidecar::build_sidecar_command_args;
    use tempfile::Builder as SandboxDirectoryBuilder;

    #[test]
    fn test_handshake_tlv_serialization() {
        let handshake = allocate_ephemeral_port_and_token().unwrap();
        assert_eq!(handshake.ipc_message_buffer[0], 0xCA);
        assert_eq!(handshake.ipc_message_buffer[1], 0xFE);
        assert_eq!(handshake.ipc_message_buffer.len(), 46);
        assert_eq!(handshake.token.len(), 36);
        assert!(handshake.ephemeral_port > 0);
    }

    #[test]
    fn test_sidecar_argument_ordering() {
        let module_args = vec![
            "-m".to_string(),
            "medclient.sidecar_python.src.main".to_string(),
        ];
        let ordered = build_sidecar_command_args(&module_args, 54321);
        assert_eq!(
            ordered,
            vec![
                "-m".to_string(),
                "medclient.sidecar_python.src.main".to_string(),
                "--port=54321".to_string()
            ]
        );
    }

    #[test]
    fn test_system_resource_supervisor_and_hysteresis() {
        let mut supervisor = SystemResourceSupervisor::new(300);
        assert_eq!(
            supervisor.evaluate_memory_state(100),
            ThrottlingState::Normal
        );
        assert_eq!(
            supervisor.evaluate_memory_state(245),
            ThrottlingState::Constrained
        );
        // Hysteresis: dropping to 195 MB (>= 180 MB) stays Constrained
        assert_eq!(
            supervisor.evaluate_memory_state(195),
            ThrottlingState::Constrained
        );
        // Dropping below 180 MB recovers to Normal
        assert_eq!(
            supervisor.evaluate_memory_state(170),
            ThrottlingState::Normal
        );
        assert_eq!(
            supervisor.evaluate_memory_state(280),
            ThrottlingState::Critical
        );
    }

    #[test]
    fn test_asset_protocol_handler_with_persistent_cache_and_formats() {
        let isolated_sandbox_dir = SandboxDirectoryBuilder::new()
            .prefix("medclient_vault_")
            .tempdir()
            .unwrap();
        let base_path = isolated_sandbox_dir.path().to_path_buf();
        let config = MediaVaultConfig::new(base_path.clone());

        // Test hash non valido e path traversal
        let bad_request_response = handle_med_asset_request(&config, "/invalid-hash").unwrap();
        assert_eq!(bad_request_response.status_code, 400);

        let traversal_response =
            handle_med_asset_request(&config, "med-asset://../../windows/system32/cmd.exe")
                .unwrap();
        assert_eq!(traversal_response.status_code, 400);

        // Test risorsa inesistente
        let valid_hash = "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef";
        let not_found_response = handle_med_asset_request(&config, valid_hash).unwrap();
        assert_eq!(not_found_response.status_code, 404);

        // Test risorsa WebP esistente con mmap zero-copy e cache hit persistente
        let asset_file = base_path.join(format!("{}.webp", valid_hash));
        std::fs::write(&asset_file, b"RIFF....WEBPVP8 ").unwrap();

        let first_ok_response = handle_med_asset_request(&config, valid_hash).unwrap();
        assert_eq!(first_ok_response.status_code, 200);
        assert_eq!(first_ok_response.content_type, "image/webp");
        assert_eq!(first_ok_response.body, b"RIFF....WEBPVP8 ");

        let second_ok_response = handle_med_asset_request(&config, valid_hash).unwrap();
        assert_eq!(second_ok_response.status_code, 200);
        let shared_handler = acquire_shared_asset_handler(&config).unwrap();
        assert!(shared_handler.cache_hits() >= 1);

        // Test risorsa SVG (ROA-12 2D structure fallback) e PDB (3D structure)
        let svg_file = base_path.join(format!("{}.svg", valid_hash));
        std::fs::write(&svg_file, b"<svg xmlns='http://www.w3.org/2000/svg'></svg>").unwrap();
        let svg_response =
            handle_med_asset_request(&config, &format!("med-asset://molecules/{}.svg", valid_hash))
                .unwrap();
        assert_eq!(svg_response.status_code, 200);
        assert_eq!(svg_response.content_type, "image/svg+xml");

        let pdb_file = base_path.join(format!("{}.pdb", valid_hash));
        std::fs::write(&pdb_file, b"HEADER    MOLECULE\nEND\n").unwrap();
        let pdb_response = handle_med_asset_request(
            &config,
            &format!("med-asset://structures/{}.pdb", valid_hash),
        )
        .unwrap();
        assert_eq!(pdb_response.status_code, 200);
        assert_eq!(pdb_response.content_type, "chemical/x-pdb");
    }

    #[test]
    fn test_bounded_mmap_lru_cache_eviction() {
        use medclient_core::implementations::asset_protocol::BoundedMmapLruCache;

        let isolated_sandbox_dir = SandboxDirectoryBuilder::new()
            .prefix("medclient_lru_")
            .tempdir()
            .unwrap();
        let mut lru_cache = BoundedMmapLruCache::new(8);

        for file_index in 0..10 {
            let file_name = format!("{:064x}", file_index);
            let file_path = isolated_sandbox_dir
                .path()
                .join(format!("{}.webp", file_name));
            std::fs::write(
                &file_path,
                format!("IMAGE_STREAM_BYTES_{}", file_index).as_bytes(),
            )
            .unwrap();

            let file_descriptor = std::fs::File::open(&file_path).unwrap();
            let memory_map = unsafe { memmap2::Mmap::map(&file_descriptor).unwrap() };
            lru_cache.insert_and_retain(file_name, memory_map);
        }

        assert_eq!(lru_cache.active_map_count(), 8);
        assert!(lru_cache.acquire(&format!("{:064x}", 0)).is_none());
        assert!(lru_cache.acquire(&format!("{:064x}", 1)).is_none());
        assert!(lru_cache.acquire(&format!("{:064x}", 9)).is_some());
        assert_eq!(lru_cache.hit_count(), 1);
        assert_eq!(lru_cache.miss_count(), 2);
    }

    #[test]
    fn test_win32_job_supervisor_creation_and_accounting() {
        let supervisor = Win32JobSupervisor::new();
        assert!(supervisor.is_ok());
        let supervisor_instance = supervisor.unwrap();
        assert!(supervisor_instance.is_active());
        assert!(supervisor_instance.assign_process(0).is_err());
        assert!(supervisor_instance.assign_process_by_id(0).is_err());
        assert!(supervisor_instance.query_job_peak_memory_mb().is_ok());
    }

    #[test]
    fn test_jemalloc_memory_tuner_config() {
        let mut tuner = JemallocMemoryTuner::new(MemoryTunerConfig::default());
        assert_eq!(tuner.configuration().dirty_decay_ms, 1000);
        assert_eq!(tuner.configuration().muzzy_decay_ms, 2000);
        assert_eq!(tuner.configuration().target_rss_limit_mb, 25);
        assert!(tuner.apply_tuning().is_ok());
        assert!(tuner.is_tuned());
        assert_eq!(tuner.purge_epoch_counter(), 1);
        assert!(tuner.purge_dirty_pages().is_ok());
        assert_eq!(tuner.purge_epoch_counter(), 2);
    }

    #[test]
    fn test_windows_dpapi_roundtrip() {
        let dpapi_vault = DpapiSecretVault::new();
        let secret_input = b"authentic-pharmacology-api-secret-key-2026";

        #[cfg(windows)]
        {
            let encryption_outcome = dpapi_vault.protect_secret(secret_input);
            assert!(
                encryption_outcome.is_ok(),
                "Encryption failed: {:?}",
                encryption_outcome
            );
            let ciphertext = encryption_outcome.unwrap();
            assert_ne!(ciphertext.as_slice(), secret_input.as_slice());

            let decryption_outcome = dpapi_vault.unprotect_secret(&ciphertext);
            assert!(
                decryption_outcome.is_ok(),
                "Decryption failed: {:?}",
                decryption_outcome
            );
            let recovered_plaintext = decryption_outcome.unwrap();
            assert_eq!(recovered_plaintext.as_slice(), secret_input.as_slice());
        }

        #[cfg(not(windows))]
        {
            let _ = dpapi_vault;
            let _ = secret_input;
        }
    }

    #[test]
    fn test_host_process_lifecycle_transitions() {
        let mut lifecycle = HostProcessLifecycle::new();
        assert_eq!(
            lifecycle.phase(),
            medclient_core::base::models::HostLifecyclePhase::Uninitialized
        );

        let init_outcome = lifecycle.initialize_host();
        assert!(init_outcome.is_ok(), "Init failed: {:?}", init_outcome);
        assert_eq!(
            lifecycle.phase(),
            medclient_core::base::models::HostLifecyclePhase::Running
        );
        assert!(lifecycle.handshake_config().is_some());

        let expected_token = lifecycle.handshake_config().unwrap().token.clone();
        let unprotected_token = lifecycle.unprotect_handshake_token().unwrap();
        assert_eq!(unprotected_token, expected_token);

        let memory_check = lifecycle.evaluate_memory_pressure();
        assert!(memory_check.is_ok());

        let heal_check = lifecycle.verify_and_heal_sidecar();
        assert!(!heal_check.unwrap());

        let shutdown_outcome = lifecycle.shutdown_host();
        assert!(shutdown_outcome.is_ok());
        assert_eq!(
            lifecycle.phase(),
            medclient_core::base::models::HostLifecyclePhase::Terminated
        );
    }
}
