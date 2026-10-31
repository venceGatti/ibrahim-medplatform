"""Custom domain exceptions for MedClient (ROA-24)."""


class MedClientError(ValueError):
    """Root exception for all MedClient domain and validation errors."""

    def __init__(self, message: str = "") -> None:
        super().__init__(message)


class DatabaseLockedError(MedClientError):
    """Raised when SQLite database cannot acquire lock within timeout."""

    def __init__(self, message: str = "SQLite database locked") -> None:
        super().__init__(message)


class DatabaseIntegrityError(MedClientError):
    """Raised when SQLite database fails PRAGMA integrity_check."""

    def __init__(self, message: str = "SQLite database integrity check failed") -> None:
        super().__init__(message)


class HotSwapVerificationError(MedClientError):
    """Raised when target database slot verification fails prior to atomic swap."""

    def __init__(self, message: str = "Database hot-swap verification failed") -> None:
        super().__init__(message)


class RedFlagsCriticalError(MedClientError):
    """Raised when patient vitals indicate critical physiological collapse."""

    def __init__(self, message: str = "Critical physiological red flags detected") -> None:
        super().__init__(message)


class InvalidVitalsError(MedClientError):
    """Raised when vital sign values fall outside physiologically possible ranges."""

    def __init__(self, message: str = "Vital signs out of valid physiological range") -> None:
        super().__init__(message)


class InvalidRenalParameterError(MedClientError):
    """Raised when renal calculator receives non-positive creatinine or invalid age."""

    def __init__(self, message: str = "Renal parameter must be strictly positive") -> None:
        super().__init__(message)


class PharmacologySafetyViolationError(MedClientError):
    """Raised when drug interaction constitutes an absolute contraindication."""

    def __init__(self, message: str = "Pharmacology safety constraint violated") -> None:
        super().__init__(message)


class InvalidATCFormatError(MedClientError):
    """Raised when an ATC code does not conform to the 7-character WHO specification."""

    def __init__(self, message: str = "Invalid ATC code format") -> None:
        super().__init__(message)


class NLIInferenceError(MedClientError):
    """Raised when Natural Language Inference evaluation fails."""

    def __init__(self, message: str = "NLI inference evaluation failure") -> None:
        super().__init__(message)


class InvalidDAGTransitionError(MedClientError):
    """Raised when an invalid action is attempted in a stateful clinical scenario."""

    def __init__(self, message: str = "Invalid stateful scenario DAG transition") -> None:
        super().__init__(message)


class SDUINodeNotFoundError(MedClientError):
    """Raised when an unknown SDUI block type is requested in the Dual Registry (ROA-02)."""

    def __init__(self, message: str = "Requested SDUI block type is not registered") -> None:
        super().__init__(message)


class AuthenticationError(MedClientError):
    """Raised when IPC authentication token is invalid or missing."""

    def __init__(self, message: str = "IPC token authentication failure") -> None:
        super().__init__(message)
