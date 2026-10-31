#[derive(Debug, Clone, PartialEq, Eq)]
pub struct MemoryTunerConfig {
    pub dirty_decay_ms: isize,
    pub muzzy_decay_ms: isize,
    pub target_rss_limit_mb: u64,
}

impl Default for MemoryTunerConfig {
    fn default() -> Self {
        Self {
            dirty_decay_ms: 1000,
            muzzy_decay_ms: 2000,
            target_rss_limit_mb: 25,
        }
    }
}

pub struct JemallocMemoryTuner {
    configuration: MemoryTunerConfig,
    is_tuned: bool,
    purge_epoch_counter: u64,
    active_dirty_decay_ms: isize,
    active_muzzy_decay_ms: isize,
}

impl JemallocMemoryTuner {
    pub fn new(mut configuration: MemoryTunerConfig) -> Self {
        configuration.dirty_decay_ms = configuration.dirty_decay_ms.max(0);
        configuration.muzzy_decay_ms = configuration.muzzy_decay_ms.max(0);
        let initial_dirty = configuration.dirty_decay_ms;
        let initial_muzzy = configuration.muzzy_decay_ms;
        Self {
            configuration,
            is_tuned: false,
            purge_epoch_counter: 0,
            active_dirty_decay_ms: initial_dirty,
            active_muzzy_decay_ms: initial_muzzy,
        }
    }

    pub fn apply_tuning(&mut self) -> Result<(), String> {
        let clamped_dirty = self.configuration.dirty_decay_ms.max(0);
        let clamped_muzzy = self.configuration.muzzy_decay_ms.max(0);
        self.active_dirty_decay_ms = clamped_dirty;
        self.active_muzzy_decay_ms = clamped_muzzy;
        self.purge_epoch_counter = self.purge_epoch_counter.saturating_add(1);

        #[cfg(windows)]
        unsafe {
            let current_process = windows_sys::Win32::System::Threading::GetCurrentProcess();
            let trim_status =
                windows_sys::Win32::System::ProcessStatus::K32EmptyWorkingSet(current_process);
            if trim_status == 0 {
                let win32_err = windows_sys::Win32::Foundation::GetLastError();
                return Err(format!(
                    "K32EmptyWorkingSet fallita durante apply_tuning (Win32 error {})",
                    win32_err
                ));
            }
        }

        self.is_tuned = true;
        Ok(())
    }

    pub fn configuration(&self) -> &MemoryTunerConfig {
        &self.configuration
    }

    pub fn is_tuned(&self) -> bool {
        self.is_tuned
    }

    pub fn purge_epoch_counter(&self) -> u64 {
        self.purge_epoch_counter
    }

    pub fn active_decay_thresholds(&self) -> (isize, isize) {
        (self.active_dirty_decay_ms, self.active_muzzy_decay_ms)
    }

    pub fn purge_dirty_pages(&mut self) -> Result<(), String> {
        self.purge_epoch_counter = self.purge_epoch_counter.saturating_add(1);
        #[cfg(windows)]
        unsafe {
            let current_process = windows_sys::Win32::System::Threading::GetCurrentProcess();
            let trim_status =
                windows_sys::Win32::System::ProcessStatus::K32EmptyWorkingSet(current_process);
            if trim_status == 0 {
                let win32_err = windows_sys::Win32::Foundation::GetLastError();
                return Err(format!(
                    "K32EmptyWorkingSet fallita durante purge_dirty_pages (Win32 error {})",
                    win32_err
                ));
            }
        }
        Ok(())
    }
}
