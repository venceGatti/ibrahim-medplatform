use crate::base::models::{AssetResponse, ThrottlingState};

pub trait IJobSupervisor: Send + Sync {
    fn assign_process(&self, process_handle: usize) -> Result<(), String>;
    fn assign_process_by_id(&self, process_identifier: u32) -> Result<(), String>;
    fn is_active(&self) -> bool;
}

pub trait IResourceSupervisor: Send + Sync {
    fn evaluate_memory_state(&mut self, current_rss_mb: u64) -> ThrottlingState;
    fn get_current_rss_mb(&self) -> Result<u64, String>;
    fn current_state(&self) -> ThrottlingState;
}

pub trait IAssetProtocolHandler: Send + Sync {
    fn handle_request(&self, raw_path: &str) -> Result<AssetResponse, String>;
}

pub trait IDpapiVault: Send + Sync {
    fn encrypt_secret(&self, plaintext_secret: &[u8]) -> Result<Vec<u8>, String>;
    fn decrypt_secret(&self, encrypted_secret: &[u8]) -> Result<Vec<u8>, String>;
}

pub trait IHostLifecycle: Send + Sync {
    fn initialize_host(&mut self) -> Result<(), String>;
    fn start_sidecar(&mut self, executable_command: &str, argument_vector: &[String]) -> Result<(), String>;
    fn shutdown_host(&mut self) -> Result<(), String>;
}
