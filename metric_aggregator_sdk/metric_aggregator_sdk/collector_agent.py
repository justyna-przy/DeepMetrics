import threading
import time
import logging
from typing import Optional
from .device import Device
from .aggregator_api import AggregatorAPI 

class CollectorAgent(threading.Thread):
    """
    Runs in its own thread. Periodically collects snapshots from a Device at a specified interval
    and passes them to the AggregatorAPI for merging and upload.
    """
    def __init__(
        self,
        aggregator: AggregatorAPI,
        device: Device,
        interval: float = 30.0,
        logger: Optional[logging.Logger] = None
    ):
        super().__init__()
        self.aggregator = aggregator
        self.device = device
        self.interval = interval
        self.logger = logger or logging.getLogger(__name__)
        self._stop_event = threading.Event()

    def run(self):
        self.logger.info("[CollectorAgent] Started for device '%s' at interval=%.1f sec", 
                         self.device.name, self.interval)
        while not self._stop_event.is_set():
            try:
                snapshot = self.device.collect_snapshot()
                if snapshot:
                    self.aggregator.add_snapshot(snapshot)
                    self.logger.debug("[CollectorAgent] Snapshot from '%s' added to aggregator.", 
                                      self.device.name)
            except Exception as e:
                self.logger.error("[CollectorAgent] Error collecting snapshot for '%s': %s", 
                                  self.device.name, e)

            time.sleep(self.interval)

        self.logger.info("[CollectorAgent] Stopped for device '%s'", self.device.name)

    def stop(self):
        self.logger.info("[CollectorAgent] Stop signal received for device '%s'", self.device.name)
        self._stop_event.set()
        self.join()
