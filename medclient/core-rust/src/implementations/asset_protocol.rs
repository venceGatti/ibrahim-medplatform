use std::collections::{HashMap, VecDeque};
use std::fs::File;
use std::path::PathBuf;
use std::sync::atomic::{AtomicU64, Ordering};
use std::sync::{Arc, Mutex, OnceLock};
use memmap2::Mmap;

use crate::base::models::{AssetResponse, AssetResponseBody, MediaVaultConfig};
use crate::interfaces::traits::IAssetProtocolHandler;

const MAXIMUM_LRU_MAPS: usize = 8;

pub struct BoundedMmapLruCache {
    capacity_limit: usize,
    open_maps: HashMap<String, Arc<Mmap>>,
    access_order: VecDeque<String>,
    hit_counter: u64,
    miss_counter: u64,
}

impl BoundedMmapLruCache {
    pub fn new(capacity_limit: usize) -> Self {
        let bounded_capacity = capacity_limit.max(1);
        Self {
            capacity_limit: bounded_capacity,
            open_maps: HashMap::with_capacity(bounded_capacity),
            access_order: VecDeque::with_capacity(bounded_capacity),
            hit_counter: 0,
            miss_counter: 0,
        }
    }

    pub fn acquire(&mut self, asset_key: &str) -> Option<Arc<Mmap>> {
        if let Some(existing_map) = self.open_maps.get(asset_key) {
            let cloned_reference = Arc::clone(existing_map);
            self.access_order.retain(|element| element != asset_key);
            self.access_order.push_back(asset_key.to_string());
            self.hit_counter = self.hit_counter.saturating_add(1);
            Some(cloned_reference)
        } else {
            self.miss_counter = self.miss_counter.saturating_add(1);
            None
        }
    }

    pub fn insert_and_retain(&mut self, asset_key: String, memory_map: Mmap) -> Arc<Mmap> {
        if self.open_maps.len() >= self.capacity_limit && !self.open_maps.contains_key(&asset_key) {
            if let Some(least_recently_used_key) = self.access_order.pop_front() {
                self.open_maps.remove(&least_recently_used_key);
            }
        }

        let shared_reference = Arc::new(memory_map);
        self.open_maps
            .insert(asset_key.clone(), Arc::clone(&shared_reference));
        self.access_order.retain(|element| element != &asset_key);
        self.access_order.push_back(asset_key);
        shared_reference
    }

    pub fn active_map_count(&self) -> usize {
        self.open_maps.len()
    }

    pub fn hit_count(&self) -> u64 {
        self.hit_counter
    }

    pub fn miss_count(&self) -> u64 {
        self.miss_counter
    }
}

pub struct ZeroCopyAssetProtocolHandler {
    config: MediaVaultConfig,
    cache: Mutex<BoundedMmapLruCache>,
    cache_hits: AtomicU64,
    cache_misses: AtomicU64,
}

impl ZeroCopyAssetProtocolHandler {
    pub fn new(config: MediaVaultConfig) -> Self {
        Self {
            config,
            cache: Mutex::new(BoundedMmapLruCache::new(MAXIMUM_LRU_MAPS)),
            cache_hits: AtomicU64::new(0),
            cache_misses: AtomicU64::new(0),
        }
    }

    pub fn cache_hits(&self) -> u64 {
        self.cache_hits.load(Ordering::Relaxed)
    }

    pub fn cache_misses(&self) -> u64 {
        self.cache_misses.load(Ordering::Relaxed)
    }

    fn resolve_extension_and_mime(candidate: &str) -> Result<(&str, &str, &'static str), ()> {
        if let Some(stem) = candidate.strip_suffix(".webp") {
            return Ok((stem, "webp", "image/webp"));
        }
        if let Some(stem) = candidate.strip_suffix(".svg") {
            return Ok((stem, "svg", "image/svg+xml"));
        }
        if let Some(stem) = candidate.strip_suffix(".pdb") {
            return Ok((stem, "pdb", "chemical/x-pdb"));
        }
        if let Some(stem) = candidate.strip_suffix(".sdf") {
            return Ok((stem, "sdf", "chemical/x-mdl-sdfile"));
        }
        if candidate.contains('.') {
            return Err(());
        }
        Ok((candidate, "webp", "image/webp"))
    }

    pub fn handle_request(&self, raw_path: &str) -> Result<AssetResponse, String> {
        if raw_path.contains("..") || raw_path.contains('\\') {
            return Ok(AssetResponse {
                status_code: 400,
                content_type: "text/plain",
                body: AssetResponseBody::StaticSlice(b"Path traversal rejected"),
            });
        }

        let normalized_path = raw_path
            .trim_start_matches("med-asset://")
            .trim_start_matches('/');

        let stripped_candidate = normalized_path
            .strip_prefix("images/")
            .or_else(|| normalized_path.strip_prefix("image/"))
            .or_else(|| normalized_path.strip_prefix("molecules/"))
            .or_else(|| normalized_path.strip_prefix("structures/"))
            .unwrap_or(normalized_path);

        let (hash_segment, extension, mime_type) =
            match Self::resolve_extension_and_mime(stripped_candidate) {
                Ok(parsed) => parsed,
                Err(()) => {
                    return Ok(AssetResponse {
                        status_code: 400,
                        content_type: "text/plain",
                        body: AssetResponseBody::StaticSlice(b"Unsupported media extension"),
                    });
                }
            };

        // Convalida stringente: SHA-256 esadecimale (64 caratteri [0-9a-fA-F])
        if hash_segment.len() != 64 || !hash_segment.chars().all(|c| c.is_ascii_hexdigit()) {
            return Ok(AssetResponse {
                status_code: 400,
                content_type: "text/plain",
                body: AssetResponseBody::StaticSlice(b"Invalid media hash identifier"),
            });
        }

        let cache_key = format!("{}.{}", hash_segment.to_ascii_lowercase(), extension);

        // Verifica immediata nella cache LRU protetta da lock
        let maybe_cached_map = {
            let mut cache_guard = self
                .cache
                .lock()
                .map_err(|e| format!("Lock acquisizione fallito: {}", e))?;
            cache_guard.acquire(&cache_key)
        };

        if let Some(cached_map) = maybe_cached_map {
            self.cache_hits.fetch_add(1, Ordering::Relaxed);
            return Ok(AssetResponse {
                status_code: 200,
                content_type: mime_type,
                body: AssetResponseBody::MmapSlice(cached_map),
            });
        }

        self.cache_misses.fetch_add(1, Ordering::Relaxed);

        let asset_file_path = self.config.base_path.join(&cache_key);
        if !asset_file_path.exists() {
            return Ok(AssetResponse {
                status_code: 404,
                content_type: "text/plain",
                body: AssetResponseBody::StaticSlice(b"Clinical asset not found"),
            });
        }

        let physical_file = File::open(&asset_file_path)
            .map_err(|e| format!("Impossibile aprire il file del media: {}", e))?;

        let file_metadata = physical_file
            .metadata()
            .map_err(|e| format!("Impossibile leggere metadata del media: {}", e))?;
        if file_metadata.len() == 0 {
            return Ok(AssetResponse {
                status_code: 204,
                content_type: mime_type,
                body: AssetResponseBody::StaticSlice(b""),
            });
        }

        // Mappatura diretta in Virtual Memory tramite OS page cache senza allocazioni su heap
        let memory_map = unsafe {
            memmap2::MmapOptions::new()
                .map(&physical_file)
                .map_err(|e| format!("Mmap failed: {}", e))?
        };

        let active_map = {
            let mut cache_guard = self
                .cache
                .lock()
                .map_err(|e| format!("Lock inserimento fallito: {}", e))?;
            cache_guard.insert_and_retain(cache_key, memory_map)
        };

        Ok(AssetResponse {
            status_code: 200,
            content_type: mime_type,
            body: AssetResponseBody::MmapSlice(active_map),
        })
    }
}

impl IAssetProtocolHandler for ZeroCopyAssetProtocolHandler {
    fn handle_request(&self, raw_path: &str) -> Result<AssetResponse, String> {
        self.handle_request(raw_path)
    }
}

static SHARED_HANDLER_REGISTRY: OnceLock<
    Mutex<HashMap<PathBuf, Arc<ZeroCopyAssetProtocolHandler>>>,
> = OnceLock::new();

pub fn acquire_shared_asset_handler(
    config: &MediaVaultConfig,
) -> Result<Arc<ZeroCopyAssetProtocolHandler>, String> {
    let registry_mutex = SHARED_HANDLER_REGISTRY.get_or_init(|| Mutex::new(HashMap::new()));
    let mut registry_guard = registry_mutex
        .lock()
        .map_err(|e| format!("Lock registro condiviso med-asset fallito: {}", e))?;
    let handler_arc = registry_guard
        .entry(config.base_path.clone())
        .or_insert_with(|| Arc::new(ZeroCopyAssetProtocolHandler::new(config.clone())))
        .clone();
    Ok(handler_arc)
}

pub fn handle_med_asset_request(
    config: &MediaVaultConfig,
    raw_path: &str,
) -> Result<AssetResponse, String> {
    let shared_handler = acquire_shared_asset_handler(config)?;
    shared_handler.handle_request(raw_path)
}
