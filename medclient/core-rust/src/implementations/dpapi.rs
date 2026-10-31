#[cfg(windows)]
use windows_sys::Win32::Security::Cryptography::{
    CryptProtectData, CryptUnprotectData, CRYPTPROTECT_UI_FORBIDDEN, CRYPT_INTEGER_BLOB,
};
#[cfg(windows)]
use windows_sys::Win32::Foundation::LocalFree;

use crate::interfaces::traits::IDpapiVault;

pub struct WindowsDpapiVault;

impl WindowsDpapiVault {
    pub fn new() -> Self {
        Self
    }

    pub fn encrypt(&self, #[allow(unused_variables)] plaintext_bytes: &[u8]) -> Result<Vec<u8>, String> {
        #[cfg(windows)]
        unsafe {
            if plaintext_bytes.is_empty() {
                return Ok(Vec::new());
            }

            let input_blob = CRYPT_INTEGER_BLOB {
                cbData: plaintext_bytes.len() as u32,
                pbData: plaintext_bytes.as_ptr() as *mut u8,
            };

            let mut output_blob: CRYPT_INTEGER_BLOB = std::mem::zeroed();

            let protect_status = CryptProtectData(
                &input_blob,
                std::ptr::null(),
                std::ptr::null(),
                std::ptr::null(),
                std::ptr::null(),
                CRYPTPROTECT_UI_FORBIDDEN,
                &mut output_blob,
            );

            if protect_status == 0 {
                let error_code = windows_sys::Win32::Foundation::GetLastError();
                return Err(format!("CryptProtectData fallita con Win32 Error: {}", error_code));
            }

            let slice_ptr = output_blob.pbData as *const u8;
            let slice_len = output_blob.cbData as usize;
            let encrypted_vector = std::slice::from_raw_parts(slice_ptr, slice_len).to_vec();

            LocalFree(output_blob.pbData as _);

            Ok(encrypted_vector)
        }
        #[cfg(not(windows))]
        {
            Err("Windows DPAPI disponibile solo su architetture Win32".to_string())
        }
    }

    pub fn decrypt(&self, #[allow(unused_variables)] ciphertext_bytes: &[u8]) -> Result<Vec<u8>, String> {
        #[cfg(windows)]
        unsafe {
            if ciphertext_bytes.is_empty() {
                return Ok(Vec::new());
            }

            let input_blob = CRYPT_INTEGER_BLOB {
                cbData: ciphertext_bytes.len() as u32,
                pbData: ciphertext_bytes.as_ptr() as *mut u8,
            };

            let mut output_blob: CRYPT_INTEGER_BLOB = std::mem::zeroed();

            let unprotect_status = CryptUnprotectData(
                &input_blob,
                std::ptr::null_mut(),
                std::ptr::null(),
                std::ptr::null(),
                std::ptr::null(),
                CRYPTPROTECT_UI_FORBIDDEN,
                &mut output_blob,
            );

            if unprotect_status == 0 {
                let error_code = windows_sys::Win32::Foundation::GetLastError();
                return Err(format!("CryptUnprotectData fallita con Win32 Error: {}", error_code));
            }

            let slice_ptr = output_blob.pbData as *const u8;
            let slice_len = output_blob.cbData as usize;
            let decrypted_vector = std::slice::from_raw_parts(slice_ptr, slice_len).to_vec();

            LocalFree(output_blob.pbData as _);

            Ok(decrypted_vector)
        }
        #[cfg(not(windows))]
        {
            Err("Windows DPAPI disponibile solo su architetture Win32".to_string())
        }
    }
}

impl IDpapiVault for WindowsDpapiVault {
    fn encrypt_secret(&self, plaintext_secret: &[u8]) -> Result<Vec<u8>, String> {
        self.encrypt(plaintext_secret)
    }

    fn decrypt_secret(&self, encrypted_secret: &[u8]) -> Result<Vec<u8>, String> {
        self.decrypt(encrypted_secret)
    }
}

impl Default for WindowsDpapiVault {
    fn default() -> Self {
        Self::new()
    }
}
