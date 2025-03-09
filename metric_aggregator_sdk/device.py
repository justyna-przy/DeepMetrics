from abc import ABC, abstractmethod
import logging

class Device(ABC):
    """
    Abstract base class for devices. Client code should subclass this
    and implement the handle_command() method.
    """
    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(f"Device.{name}") # TODO: fix loggers and config

    @abstractmethod
    def handle_command(self, command: str):
        """
        Handle a command sent from the aggregator.
        
        Args:
            command (str): A command string (e.g., "restart_collector")
        """
        pass

    @abstractmethod
    def collect_metrics(self):
        """
        Collect metrics and return a DeviceSnapshot object.
        """
        pass