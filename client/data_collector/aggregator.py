# aggregator.py
import time
import logging
from queue import Queue
from typing import List
import requests 
from dataclasses import asdict  # For converting dataclass to dict
from .snapshot import DeviceSnapshot, AggregatorData
import json

class Aggregator:
    """
    Periodically reads all items from the queue and merges them
    into a single Snapshot object.
    """
    def __init__(self, 
                 input_queue: Queue, 
                 interval: float = 10.0, 
                 logger: logging.Logger = None,
                 guid: str = "123e4567-e89b-12d3-a456-426655440000", 
                 name: str = "Justyna's Aggregator"):
        self.input_queue = input_queue
        self.interval = interval
        self.logger = logger or logging.getLogger(__name__)
        self.guid = guid
        self.name = name
        self._stop = False

    def run_forever(self):
        self.logger.info("Aggregator started.")
        try:
            while not self._stop:
                time.sleep(self.interval)
                aggregator_data = self.aggregate()

                if aggregator_data.device_snapshots:
                    self.logger.info("[Aggregator] New aggregator data: %s", aggregator_data)

                    # Convert to dictionary
                    data_dict = asdict(aggregator_data)
                    try:
                        payload = json.dumps(data_dict, default=str)  # Convert datetime to string
                        response = requests.post(
                            "http://localhost:8000/api/snapshots",
                            data=payload,
                            headers={"Content-Type": "application/json"},
                            timeout=5
                        )
                        response.raise_for_status()
                        self.logger.info("Successfully sent aggregator data. Response: %s", response.text)
                    except requests.RequestException as e:
                        self.logger.error("Failed to send aggregator data: %s", e)
                else:
                    self.logger.debug("[Aggregator] No device snapshots to send.")

        except KeyboardInterrupt:
            self.logger.info("Aggregator interrupted by user.")
        finally:
            self.logger.info("Aggregator stopped.")

    def aggregate(self) -> AggregatorData:
        """
        Collect all DeviceSnapshot items from the queue
        and merge them into a single AggregatorData object.
        """
        device_snapshots_dict = {}

        while not self.input_queue.empty():
            item = self.input_queue.get()
            if isinstance(item, DeviceSnapshot):
                device_snapshots_dict[item.device_name] = item
            else:
                self.logger.warning("[Aggregator] Non-DeviceSnapshot item in queue: %s", item)

        # Convert the dict to a list of DeviceSnapshot
        device_snapshots_list = list(device_snapshots_dict.values())

        return AggregatorData(
            guid=self.guid,
            name=self.name,
            device_snapshots=device_snapshots_list
        )

    def stop(self):
        """Gracefully stops the aggregator loop."""
        self._stop = True

    