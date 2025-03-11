import time
import logging
from datetime import datetime

class BlockTimer:
    """
    A simple RAII-style context manager for timing a block of code.
    Logs elapsed time when exiting the block.
    """
    def __init__(self, name: str, logger: logging.Logger = None):
        self.name = name
        self.logger = logger or logging.getLogger(__name__)
        self.start_time = None

    def __enter__(self):
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        elapsed = time.perf_counter() - self.start_time
        self.logger.info(f"[BlockTimer] {self.name} took {elapsed*1000:.2f} ms")

def format_timestamp(dt: datetime) -> str:
    """
    Format a Python datetime into D/M/Y then time (HH:MM:SS).
    Example: "11/03/2025 12:21:56"
    """
    if dt is None:
        return ""  
    
    # %d => zero-padded day, %m => zero-padded month, %Y => 4-digit year
    # %H:%M:%S => 24-hour time with zero-padded hours/minutes/seconds
    return dt.strftime("%d/%m/%Y %H:%M:%S")
