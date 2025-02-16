# aggregator.py
import time
import logging
from queue import Queue
from typing import List
import requests 
from dataclasses import asdict  # For converting dataclass to dict
from .snapshot import Snapshot, Device
import json

class Aggregator:
    """
    Periodically reads all items from the queue and merges them
    into a single Snapshot object.
    """
    def __init__(self, input_queue: Queue, interval: float = 10.0, logger: logging.Logger = None):
        self.input_queue = input_queue
        self.interval = interval
        self.logger = logger or logging.getLogger(__name__)
        self._stop = False

    def run_forever(self):
        """
        Continuously aggregate data from the queue at regular intervals.
        This is typically run in the main thread or its own thread.
        """
        self.logger.info("Aggregator started.")
        try:
            while not self._stop:
                time.sleep(self.interval)
                snapshot = self.aggregate()

                if snapshot.devices:
                    self.logger.info(
                        "[Aggregator] New Snapshot: %(snapshot)s",
                        {"snapshot": snapshot}
                    )

                    # Convert to dictionary
                    snapshot_data = asdict(snapshot)

                    try:
                        payload = json.dumps(snapshot_data, default=str)  # convert datetime -> string
                        response = requests.post(
                            "http://localhost:8000/api/snapshots",
                            data=payload,  # pass as raw data
                            headers={"Content-Type": "application/json"},
                            timeout=5
                        )
                        response.raise_for_status()
                        self.logger.info(
                            "Successfully sent snapshot to backend. Response: %s", 
                            response.text
                        )
                    except requests.RequestException as e:
                        self.logger.error("Failed to send snapshot: %s", e)
                else:
                    self.logger.debug("[Aggregator] No devices to aggregate.")

        except KeyboardInterrupt:
            self.logger.info("Aggregator interrupted by user.")
        finally:
            self.logger.info("Aggregator stopped.")

    def aggregate(self) -> Snapshot:
        device_dict = {} # Ensures each device only occurs once by overridding old data

        while not self.input_queue.empty():
            item = self.input_queue.get()
            if isinstance(item, Device):
                device_dict[item.device_name] = item
            else:
                self.logger.warning(
                    "[Aggregator] Non-Device item in queue: %(item)s",
                    {"item": item}
                )

        return Snapshot(devices=list(device_dict.values()))
        
    def stop(self):
        """
        Gracefully stops the aggregator loop.
        """
        self._stop = True

    