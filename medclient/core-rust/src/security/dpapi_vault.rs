use crate::implementations::dpapi::WindowsDpapiVault;
use crate::interfaces::traits::IDpapiVault;

pub struct DpapiSecretVault {
    vault_backend: WindowsDpapiVault,
}

impl DpapiSecretVault {
    pub fn new() -> Self {
        Self {
            vault_backend: WindowsDpapiVault::new(),
        }
    }

    pub fn protect_secret(&self, plaintext_secret: &[u8]) -> Result<Vec<u8>, String> {
        self.vault_backend.encrypt_secret(plaintext_secret)
    }

    pub fn unprotect_secret(&self, encrypted_secret: &[u8]) -> Result<Vec<u8>, String> {
        self.vault_backend.decrypt_secret(encrypted_secret)
    }
}

impl Default for DpapiSecretVault {
    fn default() -> Self {
        Self::new()
    }
}

impl IDpapiVault for DpapiSecretVault {
    fn encrypt_secret(&self, plaintext_secret: &[u8]) -> Result<Vec<u8>, String> {
        self.protect_secret(plaintext_secret)
    }

    fn decrypt_secret(&self, encrypted_secret: &[u8]) -> Result<Vec<u8>, String> {
        self.unprotect_secret(encrypted_secret)
    }
}
