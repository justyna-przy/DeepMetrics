import time

from metric_aggregator_sdk.aggregator_api import AggregatorAPI
from metric_aggregator_sdk.collector_agent import CollectorAgent

from devices import LocalDevice, HuggingFaceDevice
from config.config import Config

class Application:
    def __init__(self):
        self.config = Config()
        self.logger = self.config.setup_logging()

        # Initialize devices
        self.local_device = LocalDevice("Local Device", logger=self.logger.getChild("LocalDevice"))

        hf_device_config = self.config.device_config.huggingface
        self.hf_device = HuggingFaceDevice(
            config=hf_device_config,
            name="Hugging Face Top Models",
            logger=self.logger.getChild("HuggingFaceDevice")
        )

        # Initialize aggregator
        self.aggregator = AggregatorAPI(
            guid=self.config.aggregator_config.guid,
            name=self.config.aggregator_config.name,
            logger = self.logger.getChild("AggregatorAPI")
        )

        # Register devices with the aggregator to receive commands
        self.aggregator.register_device(self.local_device)
        self.aggregator.register_device(self.hf_device)

        # Initialize collector agents with distinct intervals
        self.local_agent = CollectorAgent(
            aggregator=self.aggregator,
            device=self.local_device,
            interval=10.0, 
            logger = self.logger.getChild("LocalCollectorAgent")
        )
        self.hf_agent = CollectorAgent(
            aggregator=self.aggregator,
            device=self.hf_device,
            interval=60.0,  
            logger = self.logger.getChild("HuggingFaceCollectorAgent")
        )

    def start(self):
        """
        Start everything (aggregator thread + collector agents).
        """
        self.logger.info("[Application] Starting aggregator thread.")
        self.aggregator.start()

        self.logger.info("[Application] Starting collector agents.")
        self.local_agent.start()
        self.hf_agent.start()

        self.logger.info("[Application] Application is now running. Press Ctrl+C to stop.")
        try:
            while True:
                time.sleep(1)  # Just keep the main thread alive
        except KeyboardInterrupt:
            self.logger.info("[Application] KeyboardInterrupt received. Shutting down...")
        finally:
            self.stop()

    def stop(self):
        """
        Gracefully stop all threads and log final message.
        """
        self.logger.info("[Application] Stopping all components...")
        self.local_agent.stop()
        self.hf_agent.stop()
        self.aggregator.stop()
        self.logger.info("[Application] All components stopped.")

if __name__ == "__main__":
    app = Application()
    app.start()
