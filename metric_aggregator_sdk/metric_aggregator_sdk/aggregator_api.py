# my_resilient_sdk/aggregator_manager.py

import time
import json
import logging
import threading
import requests
from dataclasses import asdict
from typing import Optional
from metric_aggregator_sdk.config.config import Config

from .dto_models import DeviceSnapshot, AggregatorData
from .retry_queue import RetryQueue
from .device import Device

class AggregatorAPI(threading.Thread):
    """
    A resilient aggregator that merges DeviceSnapshots, uploads them,
    manages a retry queue for failed uploads, and maintains a device registry
    to relay commands to registered devices.
    """
    def __init__(
        self, 
        guid: str, 
        name: str, 
        script_path: Optional[str] = None, 
        config_path: str = "default_config.json",
        logger: Optional[logging.Logger] = None
    ):
        super().__init__()
        sdk_config = Config(script_path=script_path, config_path=config_path)
        aggregator_cfg = sdk_config.aggregatorSDK
        self.guid = guid
        self.name = name
        self.base_url = aggregator_cfg.base_url.rstrip("/")
        self.snapshots_endpoint = aggregator_cfg.snapshots_endpoint
        self.interval = aggregator_cfg.interval
        self.retry_interval = aggregator_cfg.retry_interval
        self.logger = logger or logging.getLogger(__name__)
        self._stop_event = threading.Event()
        self._snapshot_buffer = {}  # device_name -> DeviceSnapshot
        self._snapshot_lock = threading.Lock()
        self.retry_queue = RetryQueue(logger=self.logger)
        self.device_registry = {}

    def register_device(self, device: Device):
        """
        Register a device so that the aggregator can relay commands to it.
        """
        self.device_registry[device.name] = device
        self.logger.info("Registered device '%s'.", device.name)

    def run(self):
        self.logger.info("[AggregatorAPI] Starting aggregator thread.")
        last_upload_time = time.time()
        last_retry_time = time.time()

        while not self._stop_event.is_set():
            time.sleep(0.5)  # Polling interval to check for stop signal

            current_time = time.time()
            if current_time - last_upload_time >= self.interval:
                self._upload_merged_data()
                last_upload_time = current_time

            if current_time - last_retry_time >= self.retry_interval:
                self._flush_retry_queue()
                last_retry_time = current_time

        self.logger.info("[AggregatorAPI] Aggregator thread stopped.")

    def stop(self):
        self.logger.info("[AggregatorAPI] Stop signal received.")
        self._stop_event.set()
        self.join()

    def add_snapshot(self, snapshot: DeviceSnapshot):
        """
        Adds new snapshot data to the buffer and merges it with existing data if present.
        """
        with self._snapshot_lock:
            if snapshot.device_name in self._snapshot_buffer:
                existing = self._snapshot_buffer[snapshot.device_name]
                existing.merge(snapshot)  
                self.logger.debug("Merged snapshot for device '%s'.", snapshot.device_name)
            else:
                self._snapshot_buffer[snapshot.device_name] = snapshot
                self.logger.debug("Added new snapshot for device '%s'.", snapshot.device_name)

    def _upload_merged_data(self):
        """
        Merge buffered snapshots into an AggregatorData object and attempt to upload.
        On failure (i.e. connection issues), enqueue snapshots for retry.
        """
        with self._snapshot_lock:
            if not self._snapshot_buffer:
                self.logger.debug("[AggregatorAPI] No snapshots to upload.")
                return
            device_names = list(self._snapshot_buffer.keys())
            self.logger.info("[AggregatorAPI] Preparing to upload snapshots for devices: %s", device_names)
            device_snapshots = list(self._snapshot_buffer.values())
            self._snapshot_buffer.clear()

        aggregator_data = AggregatorData(
            guid=self.guid,
            name=self.name,
            device_snapshots=device_snapshots
        )

        queue_size = self.retry_queue.size()
        self.logger.info("[AggregatorAPI] Current retry queue size: %d", queue_size)

        if not self._upload(aggregator_data):
            for snap in device_snapshots:
                self.retry_queue.enqueue(snap)

    def _flush_retry_queue(self):
        """
        Attempt to re-upload snapshots from the retry queue.
        """
        items = self.retry_queue.dequeue_all()
        if not items:
            return

        self.logger.info("[AggregatorAPI] Retrying %d queued snapshots.", len(items))
        aggregator_data = AggregatorData(
            guid=self.guid,
            name=self.name,
            device_snapshots=items
        )

        if not self._upload(aggregator_data):
            for snap in items:
                self.retry_queue.enqueue(snap)

    def _upload(self, aggregator_data: AggregatorData) -> bool:
        """
        Upload the given aggregator data to the specified endpoint.
        Differentiates between connection failures and server-side errors.
        Returns True for successful uploads (or when dropping bad data),
        and False if the connection failed (to trigger a retry).
        """
        payload = json.dumps(asdict(aggregator_data), default=str)
        url = f"{self.base_url}{self.snapshots_endpoint}"
        device_names = [snap.device_name for snap in aggregator_data.device_snapshots]
        self.logger.info("[AggregatorAPI] Attempting to upload data for devices: %s", device_names)
        connected_successfully = False

        try:
            response = requests.post(
                url,
                data=payload,
                headers={"Content-Type": "application/json"},
                timeout=5
            )
            connected_successfully = True
            response.raise_for_status()
            self.logger.info("[AggregatorAPI] Successfully uploaded aggregator data for devices %s. Server response: %s", device_names, response.text)
            return True
        except requests.RequestException as e:
            if connected_successfully:
                self.logger.critical("[AggregatorAPI] Server-side error for devices %s. Dropping snapshot. Error: %s", device_names, e)
                return True  # Drop the snapshot to avoid retrying bad data.
            else:
                self.logger.warning("[AggregatorAPI] Connection failure for devices %s. Will retry later. Error: %s", device_names, e)
                return False

    def _handle_command(self, command: dict):
        """
        Handle a command received from the server.
        Expected command format:
            { "device_name": "DeviceA", "command": "restart_collector" }
        Looks up the device in the registry and calls its handle_command() method.
        """
        device_name = command.get("device_name")
        if not device_name:
            self.logger.warning("Received command with no device_name: %s", command)
            return

        device = self.device_registry.get(device_name)
        if device:
            self.logger.info("Relaying command '%s' to device '%s'.", command.get("command"), device_name)
            device.handle_command(command)
        else:
            self.logger.warning("No registered device found for '%s'. Command: %s", device_name, command)
