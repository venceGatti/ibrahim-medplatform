use std::process::Child;
use std::time::{Duration, Instant};

use crate::base::models::{HostLifecyclePhase, SidecarHandshakeConfig, ThrottlingState};
use crate::implementations::dpapi::WindowsDpapiVault;
use crate::implementations::jemalloc_tuner::{JemallocMemoryTuner, MemoryTunerConfig};
use crate::implementations::sidecar::{allocate_ephemeral_port_and_token, spawn_sidecar_process};
use crate::implementations::supervisor::Win32JobSupervisor;
use crate::implementations::throttling::SystemResourceSupervisor;
use crate::interfaces::traits::{IHostLifecycle, IJobSupervisor};
#[cfg(windows)]
use crate::interfaces::traits::IDpapiVault;

pub struct HostProcessLifecycle {
    phase: HostLifecyclePhase,
    job_supervisor: Option<Win32JobSupervisor>,
    resource_supervisor: SystemResourceSupervisor,
    memory_tuner: JemallocMemoryTuner,
    #[allow(dead_code)]
    dpapi_vault: WindowsDpapiVault,
    #[allow(dead_code)]
    protected_token_blob: Option<Vec<u8>>,
    sidecar_process: Option<Child>,
    handshake_config: Option<SidecarHandshakeConfig>,
    last_executable_command: Option<String>,
    last_argument_vector: Vec<String>,
    self_healing_restart_count: u32,
    diagnostic_log: Vec<String>,
}

impl HostProcessLifecycle {
    pub fn new() -> Self {
        Self {
            phase: HostLifecyclePhase::Uninitialized,
            job_supervisor: None,
            resource_supervisor: SystemResourceSupervisor::new(
                SystemResourceSupervisor::DEFAULT_MAX_RSS_MB,
            ),
            memory_tuner: JemallocMemoryTuner::new(MemoryTunerConfig::default()),
            dpapi_vault: WindowsDpapiVault::new(),
            protected_token_blob: None,
            sidecar_process: None,
            handshake_config: None,
            last_executable_command: None,
            last_argument_vector: Vec::new(),
            self_healing_restart_count: 0,
            diagnostic_log: Vec::new(),
        }
    }

    pub fn phase(&self) -> HostLifecyclePhase {
        self.phase
    }

    pub fn diagnostic_log(&self) -> &[String] {
        &self.diagnostic_log
    }

    pub fn self_healing_restart_count(&self) -> u32 {
        self.self_healing_restart_count
    }

    pub fn initialize_host(&mut self) -> Result<(), String> {
        let supervisor = Win32JobSupervisor::new()
            .map_err(|e| format!("Inizializzazione Win32 Job Object fallita: {}", e))?;
        self.job_supervisor = Some(supervisor);

        self.memory_tuner
            .apply_tuning()
            .map_err(|e| format!("Configurazione Memory Tuner fallita: {}", e))?;

        let handshake = allocate_ephemeral_port_and_token()
            .map_err(|e| format!("Allocazione handshake sidecar fallita: {}", e))?;

        #[cfg(windows)]
        {
            let encrypted_token = self
                .dpapi_vault
                .encrypt_secret(handshake.token.as_bytes())
                .map_err(|e| format!("Cifratura DPAPI token IPC fallita: {}", e))?;
            self.protected_token_blob = Some(encrypted_token);
        }

        self.handshake_config = Some(handshake);
        self.phase = HostLifecyclePhase::Running;
        Ok(())
    }

    pub fn unprotect_handshake_token(&self) -> Result<String, String> {
        #[cfg(windows)]
        {
            let encrypted_blob = self
                .protected_token_blob
                .as_ref()
                .ok_or_else(|| "Nessun token protetto presente nel vault DPAPI".to_string())?;
            let decrypted_bytes = self.dpapi_vault.decrypt_secret(encrypted_blob)?;
            String::from_utf8(decrypted_bytes)
                .map_err(|e| format!("Decodifica UTF-8 token DPAPI fallita: {}", e))
        }
        #[cfg(not(windows))]
        {
            self.handshake_config
                .as_ref()
                .map(|cfg| cfg.token.clone())
                .ok_or_else(|| "Handshake non inizializzato".to_string())
        }
    }

    pub fn start_sidecar(
        &mut self,
        executable_command: &str,
        argument_vector: &[String],
    ) -> Result<(), String> {
        if self.phase != HostLifecyclePhase::Running {
            return Err("Host non inizializzato o non in stato Running".to_string());
        }

        let handshake = self
            .handshake_config
            .as_ref()
            .ok_or_else(|| "Configurazione handshake assente".to_string())?;

        let supervisor_ref = self
            .job_supervisor
            .as_ref()
            .map(|s| s as &dyn IJobSupervisor);

        let child = spawn_sidecar_process(
            executable_command,
            argument_vector,
            handshake,
            supervisor_ref,
        )?;

        self.last_executable_command = Some(executable_command.to_string());
        self.last_argument_vector = argument_vector.to_vec();
        self.sidecar_process = Some(child);
        Ok(())
    }

    pub fn verify_and_heal_sidecar(&mut self) -> Result<bool, String> {
        if self.phase != HostLifecyclePhase::Running {
            return Ok(false);
        }

        let needs_restart = match self.sidecar_process.as_mut() {
            Some(active_child) => match active_child.try_wait() {
                Ok(Some(exit_status)) => {
                    self.diagnostic_log.push(format!(
                        "Sidecar terminato inaspettatamente con status: {}",
                        exit_status
                    ));
                    true
                }
                Ok(None) => false,
                Err(wait_err) => {
                    return Err(format!("Errore ispezione stato sidecar: {}", wait_err));
                }
            },
            None => false,
        };

        if needs_restart {
            let executable_command = self
                .last_executable_command
                .clone()
                .ok_or_else(|| "Comando sidecar non registrato per self-healing".to_string())?;
            let arguments = self.last_argument_vector.clone();
            let renewed_handshake = allocate_ephemeral_port_and_token()?;
            self.handshake_config = Some(renewed_handshake);
            self.start_sidecar(&executable_command, &arguments)?;
            self.self_healing_restart_count = self.self_healing_restart_count.saturating_add(1);
            return Ok(true);
        }

        Ok(false)
    }

    pub fn evaluate_memory_pressure(&mut self) -> Result<ThrottlingState, String> {
        let evaluated_state = self
            .resource_supervisor
            .update_runtime_state_with_job(self.job_supervisor.as_ref())?;
        if evaluated_state == ThrottlingState::Critical {
            self.memory_tuner.purge_dirty_pages()?;
        }
        Ok(evaluated_state)
    }

    pub fn shutdown_host(&mut self) -> Result<(), String> {
        self.phase = HostLifecyclePhase::ShuttingDown;

        if let Some(mut child) = self.sidecar_process.take() {
            let start_time = Instant::now();
            let graceful_timeout = Duration::from_millis(500);

            let mut terminated = false;
            while start_time.elapsed() < graceful_timeout {
                match child.try_wait() {
                    Ok(Some(exit_status)) => {
                        self.diagnostic_log
                            .push(format!("Sidecar terminato con successo: {}", exit_status));
                        terminated = true;
                        break;
                    }
                    Ok(None) => {
                        std::thread::sleep(Duration::from_millis(20));
                    }
                    Err(wait_error) => {
                        self.diagnostic_log.push(format!(
                            "Avviso durante try_wait in shutdown: {}",
                            wait_error
                        ));
                        break;
                    }
                }
            }

            if !terminated {
                if let Err(kill_error) = child.kill() {
                    self.diagnostic_log.push(format!(
                        "Notifica terminazione forzata child.kill(): {}",
                        kill_error
                    ));
                }
                if let Err(wait_error) = child.wait() {
                    self.diagnostic_log.push(format!(
                        "Notifica raccolta exit status child.wait(): {}",
                        wait_error
                    ));
                }
            }
        }

        self.phase = HostLifecyclePhase::Terminated;
        Ok(())
    }

    pub fn handshake_config(&self) -> Option<&SidecarHandshakeConfig> {
        self.handshake_config.as_ref()
    }
}

impl Default for HostProcessLifecycle {
    fn default() -> Self {
        Self::new()
    }
}

impl IHostLifecycle for HostProcessLifecycle {
    fn initialize_host(&mut self) -> Result<(), String> {
        self.initialize_host()
    }

    fn start_sidecar(
        &mut self,
        executable_command: &str,
        argument_vector: &[String],
    ) -> Result<(), String> {
        self.start_sidecar(executable_command, argument_vector)
    }

    fn shutdown_host(&mut self) -> Result<(), String> {
        self.shutdown_host()
    }
}
