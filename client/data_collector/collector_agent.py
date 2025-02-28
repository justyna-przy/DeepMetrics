# collector_agent.py
import threading
import time
import logging
from queue import Queue
from typing import Any, Dict, Callable
from .snapshot import DeviceSnapshot

class CollectorAgent(threading.Thread):
    """
    A threaded agent that periodically runs a collector's `collect_metrics()`
    method and places the resulting data into a shared queue.
    """

    def __init__(
        self,
        collector: Callable[[], Dict[str, Any]],
        output_queue: Queue,
        interval: float = 10.0,
        logger: logging.Logger = None,
        device_name: str = "UnknownDevice"
    ):
        super().__init__()
        self.collector = collector
        self.output_queue = output_queue
        self.interval = interval
        self.stop_event = threading.Event()
        self.logger = logger or logging.getLogger(__name__)
        self.device_name = device_name  

    def run(self):
        self.logger.info(
            "[CollectorAgent] Starting collectors for %(collector)s as device '%(dev)s'",
            {"collector": self.collector.__class__.__name__, "dev": self.device_name}
        )
        while not self.stop_event.is_set():
            try:
                metrics = self.collector.collect_metrics()

                if metrics:
                    device_obj = DeviceSnapshot(device_name=self.device_name, metrics=metrics)
                    self.output_queue.put(device_obj)
                    self.logger.debug(
                        "[CollectorAgent] Enqueued device: %(device)s",
                        {"device": device_obj}
                    )
                else:
                    self.logger.debug(
                        "[CollectorAgent] No metrics returned from %(collector)s",
                        {"collector": self.collector.__class__.__name__}
                    )
            except Exception as e:
                self.logger.error(
                    "[CollectorAgent] Error in %(collector)s: %(error)s",
                    {"collector": self.collector.__class__.__name__, "error": e}
                )

            time.sleep(self.interval)

        self.logger.info(
            "[CollectorAgent] Collector agent for %(collector)s stopped",
            {"collector": self.collector.__class__.__name__}
        )

    def stop(self):
        self.logger.info(
            "[CollectorAgent] Stop signal received for %(collector)s",
            {"collector": self.collector.__class__.__name__}
        )
        self.stop_event.set()
        self.join()
