"""Interface for Reverse Watchdog thread."""
from abc import ABC, abstractmethod


class IReverseWatchdog(ABC):
    """Monitors parent process PID and forces termination if parent exits."""

    @abstractmethod
    def start(self, parent_pid: int) -> None:
        """Start the background watchdog thread monitoring parent_pid."""
        raise NotImplementedError("Subclasses must implement start")

    @abstractmethod
    def stop(self) -> None:
        """Stop the watchdog monitoring."""
        raise NotImplementedError("Subclasses must implement stop")

    @abstractmethod
    def is_alive(self) -> bool:
        """Check if watchdog thread is active."""
        raise NotImplementedError("Subclasses must implement is_alive")
