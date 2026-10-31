#[cfg(windows)]
use windows_sys::Win32::Foundation::{CloseHandle, HANDLE, INVALID_HANDLE_VALUE};
#[cfg(windows)]
use windows_sys::Win32::System::JobObjects::{
    AssignProcessToJobObject, CreateJobObjectW, JobObjectExtendedLimitInformation,
    QueryInformationJobObject, SetInformationJobObject, JOBOBJECT_EXTENDED_LIMIT_INFORMATION,
    JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE,
};
#[cfg(windows)]
use windows_sys::Win32::System::Threading::{OpenProcess, PROCESS_SET_QUOTA, PROCESS_TERMINATE};

use crate::interfaces::traits::IJobSupervisor;

pub struct Win32JobSupervisor {
    #[cfg(windows)]
    job_handle: HANDLE,
}

unsafe impl Send for Win32JobSupervisor {}
unsafe impl Sync for Win32JobSupervisor {}

impl Win32JobSupervisor {
    pub fn new() -> Result<Self, String> {
        #[cfg(windows)]
        unsafe {
            let job = CreateJobObjectW(std::ptr::null_mut(), std::ptr::null());
            if job.is_null() || job == INVALID_HANDLE_VALUE {
                return Err("Creazione del Win32 Job Object fallita".to_string());
            }

            let mut extended_info: JOBOBJECT_EXTENDED_LIMIT_INFORMATION = std::mem::zeroed();
            extended_info.BasicLimitInformation.LimitFlags = JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE;

            let win32_system_status = SetInformationJobObject(
                job,
                JobObjectExtendedLimitInformation,
                &extended_info as *const _ as *const std::ffi::c_void,
                std::mem::size_of::<JOBOBJECT_EXTENDED_LIMIT_INFORMATION>() as u32,
            );

            if win32_system_status == 0 {
                CloseHandle(job);
                return Err(
                    "Configurazione JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE fallita".to_string(),
                );
            }

            Ok(Self { job_handle: job })
        }
        #[cfg(not(windows))]
        {
            Ok(Self {})
        }
    }

    pub fn assign_process(&self, process_handle: usize) -> Result<(), String> {
        if process_handle == 0 {
            return Err("Handle di processo nullo (0) non valido".to_string());
        }
        #[cfg(windows)]
        unsafe {
            let win32_system_status =
                AssignProcessToJobObject(self.job_handle, process_handle as HANDLE);
            if win32_system_status == 0 {
                return Err("Assegnazione processo a Job Object fallita".to_string());
            }
            Ok(())
        }
        #[cfg(not(windows))]
        {
            Ok(())
        }
    }

    pub fn assign_process_by_id(&self, process_identifier: u32) -> Result<(), String> {
        if process_identifier == 0 {
            return Err("PID 0 (System Idle) non assegnabile al Job Object".to_string());
        }
        #[cfg(windows)]
        unsafe {
            let process_handle = OpenProcess(
                PROCESS_SET_QUOTA | PROCESS_TERMINATE,
                0,
                process_identifier,
            );
            if process_handle.is_null() || process_handle == INVALID_HANDLE_VALUE {
                return Err(format!(
                    "Apertura handle processo {} fallita",
                    process_identifier
                ));
            }

            let win32_system_status = AssignProcessToJobObject(self.job_handle, process_handle);
            CloseHandle(process_handle);

            if win32_system_status == 0 {
                return Err(format!(
                    "Assegnazione PID {} a Job Object fallita",
                    process_identifier
                ));
            }
            Ok(())
        }
        #[cfg(not(windows))]
        {
            Ok(())
        }
    }

    pub fn query_job_peak_memory_mb(&self) -> Result<u64, String> {
        #[cfg(windows)]
        unsafe {
            if !self.is_active() {
                return Err("Job Object non attivo".to_string());
            }
            let mut extended_info: JOBOBJECT_EXTENDED_LIMIT_INFORMATION = std::mem::zeroed();
            let mut return_length: u32 = 0;
            let query_status = QueryInformationJobObject(
                self.job_handle,
                JobObjectExtendedLimitInformation,
                &mut extended_info as *mut _ as *mut std::ffi::c_void,
                std::mem::size_of::<JOBOBJECT_EXTENDED_LIMIT_INFORMATION>() as u32,
                &mut return_length,
            );
            if query_status == 0 {
                return Err("QueryInformationJobObject fallita".to_string());
            }
            let peak_bytes = extended_info
                .PeakJobMemoryUsed
                .max(extended_info.PeakProcessMemoryUsed);
            Ok((peak_bytes / (1024 * 1024)) as u64)
        }
        #[cfg(not(windows))]
        {
            Ok(0)
        }
    }

    pub fn is_active(&self) -> bool {
        #[cfg(windows)]
        {
            !self.job_handle.is_null() && self.job_handle != INVALID_HANDLE_VALUE
        }
        #[cfg(not(windows))]
        {
            true
        }
    }
}

impl IJobSupervisor for Win32JobSupervisor {
    fn assign_process(&self, process_handle: usize) -> Result<(), String> {
        self.assign_process(process_handle)
    }

    fn assign_process_by_id(&self, process_identifier: u32) -> Result<(), String> {
        self.assign_process_by_id(process_identifier)
    }

    fn is_active(&self) -> bool {
        self.is_active()
    }
}

impl Drop for Win32JobSupervisor {
    fn drop(&mut self) {
        #[cfg(windows)]
        unsafe {
            if !self.job_handle.is_null() && self.job_handle != INVALID_HANDLE_VALUE {
                CloseHandle(self.job_handle);
            }
        }
    }
}
