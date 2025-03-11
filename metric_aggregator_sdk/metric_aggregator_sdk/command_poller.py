import time
import requests
import logging
import threading

class CommandPoller(threading.Thread):
    """
    A thread that periodically polls the server for commands intended for this aggregator,
    relays them to the registered devices, and then acknowledges them so the server
    can remove them from the queue.
    """
    def __init__(self, aggregator_name, base_url, poll_interval=5.0, logger=None, device_registry=None):
        super().__init__()
        self.aggregator_name = aggregator_name
        self.base_url = base_url.rstrip("/")
        self.poll_interval = poll_interval
        self.logger = logger or logging.getLogger(__name__)
        self.device_registry = device_registry if device_registry is not None else {}
        self._stop_event = threading.Event()

    def run(self):
        self.logger.info("[CommandPoller] Starting command poller thread.")
        while not self._stop_event.is_set():
            time.sleep(self.poll_interval)
            try:
                self._poll_commands()
            except Exception as e:
                self.logger.warning("[CommandPoller] Error while polling commands: %s", e)

        self.logger.info("[CommandPoller] Stopped command poller thread.")

    def stop(self):
        self.logger.info("[CommandPoller] Stop signal received.")
        self._stop_event.set()
        self.join()

    def _poll_commands(self):
        """
        1) GET unacked commands from the server
        2) Relay each command to the appropriate device
        3) Ack them back to the server so they won't appear again
        """
        url = f"{self.base_url}/api/aggregators/{self.aggregator_name}/commands"
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        commands = resp.json()  

        if not commands:
            return

        self.logger.info("[CommandPoller] Received %d commands from server.", len(commands))
        ack_ids = []

        for cmd in commands:
            cmd_id = cmd.get("command_id")
            device_name = cmd.get("device_name")
            command_str = cmd.get("command")

            if not device_name or not command_str:
                self.logger.warning("[CommandPoller] Invalid command format: %s", cmd)
                continue

            # If device is registered, call device.handle_command
            device = self.device_registry.get(device_name)
            if device:
                self.logger.info("[CommandPoller] Relaying command '%s' to device '%s'.", command_str, device_name)
                device.handle_command(command_str)
            else:
                self.logger.warning(
                    "[CommandPoller] No registered device '%s'. Command: %s",
                    device_name, command_str
                )

            ack_ids.append(cmd_id)

        # Now ack them to the server
        if ack_ids:
            self._ack_commands(ack_ids)

    def _ack_commands(self, command_ids):
        """
        Tells the server these commands have been processed,
        so it can remove them from the queue.
        """
        url = f"{self.base_url}/api/aggregators/{self.aggregator_name}/commands/ack"
        payload = {"command_ids": command_ids}
        resp = requests.post(url, json=payload, timeout=5)
        resp.raise_for_status()
        self.logger.info("[CommandPoller] Acked command_ids: %s", command_ids)
