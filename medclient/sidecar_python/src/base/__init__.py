"""Base models, schemas, and custom exceptions for MedClient."""
from .exceptions import (
    MedClientError,
    DatabaseLockedError,
    DatabaseIntegrityError,
    HotSwapVerificationError,
    RedFlagsCriticalError,
    InvalidVitalsError,
    PharmacologySafetyViolationError,
    InvalidATCFormatError,
    NLIInferenceError,
    InvalidDAGTransitionError,
    AuthenticationError,
)

__all__ = [
    "MedClientError",
    "DatabaseLockedError",
    "DatabaseIntegrityError",
    "HotSwapVerificationError",
    "RedFlagsCriticalError",
    "InvalidVitalsError",
    "PharmacologySafetyViolationError",
    "InvalidATCFormatError",
    "NLIInferenceError",
    "InvalidDAGTransitionError",
    "AuthenticationError",
]
