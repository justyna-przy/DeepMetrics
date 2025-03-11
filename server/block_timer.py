# blocktimer.py
import time
import logging

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
