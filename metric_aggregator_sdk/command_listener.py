import threading
import time
import requests
import logging

class AggregatorCommandListener(threading.Thread):
    """
    A background thread that polls the server for commands targeted at this aggregator.
    When commands are received (as JSON objects), it calls the provided callback function.
    """
    def __init__(self, base_url: str, aggregator_id: str, command_callback, interval: float = 5.0, logger: logging.Logger = None):
        """
        Args:
            base_url (str): The base URL of your server.
            aggregator_id (str): Unique identifier for this aggregator.
            command_callback (callable): A function that will be called with each received command (as a dict).
            interval (float): Polling interval in seconds (default: 5 seconds).
            logger (logging.Logger): Optional logger instance.
        """
        super().__init__(daemon=True)
        self.base_url = base_url.rstrip("/")
        self.aggregator_id = aggregator_id
        self.command_callback = command_callback
        self.interval = interval
        self.logger = logger or logging.getLogger(__name__)
        self._stop_event = threading.Event()

    def run(self):
        while not self._stop_event.is_set():
            try:
                url = f"{self.base_url}/api/commands"
                params = {"aggregator_id": self.aggregator_id}
                self.logger.debug("Polling for commands at %s with params %s", url, params)
                response = requests.get(url, params=params, timeout=5)
                response.raise_for_status()
                # Expecting a list of command dictionaries, e.g.,
                # [ { "device_name": "DeviceA", "command": "restart_collector" }, ... ]
                commands = response.json()
                if commands:
                    self.logger.info("Received commands: %s", commands)
                    for command in commands:
                        self.command_callback(command)
            except Exception as e:
                self.logger.warning("Error while polling for commands: %s", e)
            time.sleep(self.interval)

    def stop(self):
        self._stop_event.set()
