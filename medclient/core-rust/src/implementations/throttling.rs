use crate::base::models::ThrottlingState;
use crate::implementations::supervisor::Win32JobSupervisor;
use crate::interfaces::traits::IResourceSupervisor;

pub struct SystemResourceSupervisor {
    pub max_rss_mb: u64,
    pub current_state: ThrottlingState,
}

impl SystemResourceSupervisor {
    pub const DEFAULT_MAX_RSS_MB: u64 = 300;

    pub fn new(max_rss_mb: u64) -> Self {
        Self {
            max_rss_mb: max_rss_mb.max(1),
            current_state: ThrottlingState::Normal,
        }
    }

    pub fn evaluate_memory_state(&mut self, current_rss_mb: u64) -> ThrottlingState {
        let constrained_threshold = (self.max_rss_mb * 80) / 100;
        let critical_threshold = (self.max_rss_mb * 90) / 100;
        let hysteresis_recovery_threshold = (self.max_rss_mb * 60) / 100;

        if current_rss_mb >= critical_threshold {
            self.current_state = ThrottlingState::Critical;
        } else if current_rss_mb >= constrained_threshold
            || (self.current_state != ThrottlingState::Normal
                && current_rss_mb >= hysteresis_recovery_threshold)
        {
            self.current_state = ThrottlingState::Constrained;
        } else {
            self.current_state = ThrottlingState::Normal;
        }
        self.current_state
    }

    pub fn query_process_working_set_mb(&self) -> Result<u64, String> {
        #[cfg(windows)]
        unsafe {
            let process_handle = windows_sys::Win32::System::Threading::GetCurrentProcess();
            let mut memory_counters: windows_sys::Win32::System::ProcessStatus::PROCESS_MEMORY_COUNTERS_EX =
                std::mem::zeroed();
            let counters_struct_size = std::mem::size_of::<
                windows_sys::Win32::System::ProcessStatus::PROCESS_MEMORY_COUNTERS_EX,
            >() as u32;

            let query_status = windows_sys::Win32::System::ProcessStatus::K32GetProcessMemoryInfo(
                process_handle,
                &mut memory_counters as *mut _ as *mut _,
                counters_struct_size,
            );

            if query_status != 0 {
                let working_set_bytes = memory_counters.WorkingSetSize;
                let working_set_megabytes = (working_set_bytes / (1024 * 1024)) as u64;
                Ok(working_set_megabytes)
            } else {
                Err("K32GetProcessMemoryInfo query failed".to_string())
            }
        }
        #[cfg(not(windows))]
        {
            Ok(25)
        }
    }

    pub fn query_job_tree_memory_mb(
        &self,
        job_supervisor: Option<&Win32JobSupervisor>,
    ) -> Result<u64, String> {
        let host_working_set_mb = self.query_process_working_set_mb()?;
        if let Some(supervisor) = job_supervisor {
            if let Ok(job_peak_mb) = supervisor.query_job_peak_memory_mb() {
                return Ok(host_working_set_mb.max(job_peak_mb));
            }
        }
        Ok(host_working_set_mb)
    }

    pub fn update_runtime_state(&mut self) -> Result<ThrottlingState, String> {
        let current_megabytes = self.query_process_working_set_mb()?;
        Ok(self.evaluate_memory_state(current_megabytes))
    }

    pub fn update_runtime_state_with_job(
        &mut self,
        job_supervisor: Option<&Win32JobSupervisor>,
    ) -> Result<ThrottlingState, String> {
        let tree_megabytes = self.query_job_tree_memory_mb(job_supervisor)?;
        Ok(self.evaluate_memory_state(tree_megabytes))
    }
}

impl IResourceSupervisor for SystemResourceSupervisor {
    fn evaluate_memory_state(&mut self, current_rss_mb: u64) -> ThrottlingState {
        self.evaluate_memory_state(current_rss_mb)
    }

    fn get_current_rss_mb(&self) -> Result<u64, String> {
        self.query_process_working_set_mb()
    }

    fn current_state(&self) -> ThrottlingState {
        self.current_state
    }
}
