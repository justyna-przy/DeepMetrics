import logging
import time
from config.config import Config
from utils.logger import setup_logging
from client.data_collector.devices import LocalDevice, HuggingFaceDevice

from metric_aggregator_sdk.aggregator_api import AggregatorAPI

class Application:
    def __init__(self, config_path="config/config.json"):
        # 1. Load configuration
        self.config = Config.load_config(script_path=__file__, config_path=config_path)

        # 2. Setup logging
        setup_logging(self.config.logging_config)
        self.logger = logging.getLogger(__name__)

        # 3. Create device instances (for now, we create just LocalDevice)
        self.local_device = LocalDevice("Justyna's Laptop")
        self.hf_device = HuggingFaceDevice(config=self.config.collectors_config.huggingface_collector, name="Hugging Face Top Models")

        # 4. Instantiate the AggregatorAPI from your SDK
        self.aggregator = AggregatorAPI(
            guid="123e4567-e89b-12d3-a456-426655440000",
            name="My Aggregator",
            base_url="http://localhost:8000",
            interval=10.0,
            retry_interval=30.0,
            logger=self.logger
        )

        # 5. Register devices with the aggregator
        self.aggregator.register_device(self.local_device)
        self.aggregator.register_device(self.hf_device)  

    def start(self):
        """
        Start the aggregator in its own thread and run a simple loop to periodically
        collect snapshots from each device and send them to the aggregator.
        """
        self.logger.info("[Application] Starting aggregator.")
        self.aggregator.start()

        try:
            while True:
                # Collect snapshot from LocalDevice and send to aggregator
                local_snapshot = self.local_device.collect_metrics()
                self.aggregator.add_snapshot(local_snapshot)
                
                # If using additional devices, collect and add their snapshots here:
                hf_snapshot = self.hf_device.collect_metrics()
                self.aggregator.add_snapshot(hf_snapshot)
                
                time.sleep(10)  # Adjust the frequency as needed.
        except KeyboardInterrupt:
            self.logger.info("[Application] KeyboardInterrupt received. Shutting down...")
        finally:
            self.stop()

    def stop(self):
        self.logger.info("[Application] Stopping all components...")
        self.aggregator.stop()
        self.logger.info("[Application] All components stopped.")

if __name__ == "__main__":
    app = Application()
    app.start()