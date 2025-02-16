import logging
import queue
from config.config import Config
from utils.logger import setup_logging
from data_collector.metric_collectors import LocalMetricsCollector, HuggingFaceCollector
from data_collector.collector_agent import CollectorAgent
from data_collector.aggregator import Aggregator

class Application:
    def __init__(self, config_path="config/config.json"):
        # 1. Load config
        self.config = Config.load_config(script_path=__file__, config_path=config_path)

        # 2. Setup logging
        setup_logging(self.config.logging_config)
        self.logger = logging.getLogger(__name__)

        # 3. Initialize collectors
        self.local_collector = LocalMetricsCollector()
        self.hf_collector = HuggingFaceCollector(self.config.collectors_config.huggingface_collector)
        # self.stock_collector = StockPriceCollector(self.config.collectors_config.stock_price_collector)

        # 4. Shared queue
        self.metric_queue = queue.Queue()

        # 5. Collector Agents
        self.local_agent = CollectorAgent(
            collector=self.local_collector,
            output_queue=self.metric_queue,
            interval=10,
            logger=self.logger,
            device_name="Justyna's Laptop"

        )
        self.hf_agent = CollectorAgent(
            collector=self.hf_collector,
            output_queue=self.metric_queue,
            interval=60,
            logger=self.logger,
            device_name="Hugging Face"
        )

        # 6. Aggregator
        self.aggregator = Aggregator(
            input_queue=self.metric_queue,
            interval=10,
            logger=self.logger
        )

    def start(self):
        """
        Starts the collector threads and aggregator
        """
        self.logger.info("[Application] Starting the local agent.")
        self.local_agent.start()
        self.hf_agent.start()

        try:
            # aggregator runs in the main thread to keep program alive
            self.aggregator.run_forever()
        except KeyboardInterrupt:
            self.logger.info("[Application] KeyboardInterrupt received. Shutting down...")
        finally:
            self.stop()

    def stop(self):
        self.logger.info("[Application] Stopping all components...")
        self.local_agent.stop()
        self.hf_agent.stop()
        self.aggregator.stop()
        self.logger.info("[Application] All components stopped.")

if __name__ == "__main__":
    app = Application()
    app.start()  


    