use std::ops::Deref;
use std::path::PathBuf;
use std::sync::Arc;
use memmap2::Mmap;

#[derive(Debug, Clone, Copy, PartialEq, Eq, serde::Serialize, serde::Deserialize)]
pub enum ThrottlingState {
    Normal,
    Constrained,
    Critical,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct SidecarHandshakeConfig {
    pub ephemeral_port: u16,
    pub token: String,
    pub ipc_message_buffer: Vec<u8>,
}

impl SidecarHandshakeConfig {
    pub fn new(ephemeral_port: u16, token: String, ipc_message_buffer: Vec<u8>) -> Self {
        Self {
            ephemeral_port,
            token,
            ipc_message_buffer,
        }
    }
}

#[derive(Debug, Clone)]
pub struct MediaVaultConfig {
    pub base_path: PathBuf,
}

impl MediaVaultConfig {
    pub fn new(base_path: PathBuf) -> Self {
        Self { base_path }
    }
}

#[derive(Clone)]
pub enum AssetResponseBody {
    MmapSlice(Arc<Mmap>),
    StaticSlice(&'static [u8]),
    OwnedBuffer(Vec<u8>),
}

impl Deref for AssetResponseBody {
    type Target = [u8];

    fn deref(&self) -> &Self::Target {
        match self {
            Self::MmapSlice(memory_map_ref) => &memory_map_ref[..],
            Self::StaticSlice(static_bytes) => static_bytes,
            Self::OwnedBuffer(allocated_bytes) => allocated_bytes.as_slice(),
        }
    }
}

impl std::fmt::Debug for AssetResponseBody {
    fn fmt(&self, formatter: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(formatter, "AssetResponseBody(length={})", self.len())
    }
}

impl PartialEq for AssetResponseBody {
    fn eq(&self, other: &Self) -> bool {
        self.deref() == other.deref()
    }
}

impl Eq for AssetResponseBody {}

impl PartialEq<&[u8]> for AssetResponseBody {
    fn eq(&self, other: &&[u8]) -> bool {
        self.deref() == *other
    }
}

impl PartialEq<AssetResponseBody> for &[u8] {
    fn eq(&self, other: &AssetResponseBody) -> bool {
        *self == other.deref()
    }
}

impl<const BUFFER_CAPACITY: usize> PartialEq<[u8; BUFFER_CAPACITY]> for AssetResponseBody {
    fn eq(&self, other: &[u8; BUFFER_CAPACITY]) -> bool {
        self.deref() == other.as_slice()
    }
}

impl<const BUFFER_CAPACITY: usize> PartialEq<&[u8; BUFFER_CAPACITY]> for AssetResponseBody {
    fn eq(&self, other: &&[u8; BUFFER_CAPACITY]) -> bool {
        self.deref() == other.as_slice()
    }
}

impl PartialEq<Vec<u8>> for AssetResponseBody {
    fn eq(&self, other: &Vec<u8>) -> bool {
        self.deref() == other.as_slice()
    }
}

#[derive(Debug, PartialEq, Eq)]
pub struct AssetResponse {
    pub status_code: u16,
    pub content_type: &'static str,
    pub body: AssetResponseBody,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum HostLifecyclePhase {
    Uninitialized,
    Running,
    ShuttingDown,
    Terminated,
}
