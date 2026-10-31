pub mod asset_protocol;
pub mod dpapi;
pub mod host_lifecycle;
pub mod jemalloc_tuner;
pub mod sidecar;
pub mod supervisor;
pub mod throttling;

pub use asset_protocol::{
    acquire_shared_asset_handler, handle_med_asset_request, BoundedMmapLruCache,
    ZeroCopyAssetProtocolHandler,
};
pub use dpapi::WindowsDpapiVault;
pub use host_lifecycle::HostProcessLifecycle;
pub use jemalloc_tuner::{JemallocMemoryTuner, MemoryTunerConfig};
pub use sidecar::{
    allocate_ephemeral_port_and_token, build_sidecar_command_args, inject_token_into_stream,
    spawn_sidecar_process,
};
pub use supervisor::Win32JobSupervisor;
pub use throttling::SystemResourceSupervisor;
