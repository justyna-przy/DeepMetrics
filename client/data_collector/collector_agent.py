# collector_agent.py
import threading
import time
import logging
from queue import Queue
from typing import Any, Dict, Callable

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
        logger: logging.Logger = None
    ):
        super().__init__()
        self.collector = collector
        self.output_queue = output_queue
        self.interval = interval
        self.stop_event = threading.Event()
        self.logger = logger or logging.getLogger(__name__)

    def run(self):
        self.logger.info(
            "[CollectorAgent] Starting collectors for %(collector)s",
            {"collector": self.collector.__class__.__name__}
        )
        while not self.stop_event.is_set():
            try:
                metrics = self.collector.collect_metrics()
                if metrics:
                    self.output_queue.put(metrics)
                    self.logger.debug(
                        "[CollectorAgent] Enqueued metrics: %(metrics)s", 
                        {"metrics": metrics}
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
