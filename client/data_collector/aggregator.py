# aggregator.py
import time
import logging
from queue import Queue
from typing import Dict, Any
from .snapshot import Snapshot

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

                if snapshot.metrics:
                    # If you have metrics, do something with them: log, send to DB, etc.
                    self.logger.info(
                        "[Aggregator] New Snapshot: %(snapshot)s", 
                        {"snapshot": snapshot}
                    )
                else:
                    self.logger.debug("[Aggregator] No metrics to aggregate.")
        except KeyboardInterrupt:
            self.logger.info("Aggregator interrupted by user.")
        finally:
            self.logger.info("Aggregator stopped.")

    def aggregate(self) -> Snapshot:
        """
        Drains the queue, merges all metric dictionaries into one,
        and returns a Snapshot.
        """
        merged_metrics: Dict[str, Any] = {}
        while not self.input_queue.empty():
            item = self.input_queue.get()
            if isinstance(item, dict):
                merged_metrics.update(item)
            else:
                self.logger.warning(
                    "[Aggregator] Non-dict item in queue: %(item)s",
                    {"item": item}
                )

        if merged_metrics:
            snapshot = Snapshot(metrics=merged_metrics)

            return snapshot
        else:
            return Snapshot()  # empty metrics

    def stop(self):
        """
        Gracefully stops the aggregator loop.
        """
        self._stop = True

    