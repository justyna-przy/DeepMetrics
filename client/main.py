import time
import logging

# 1. Import the config and aggregator from your SDK
from metric_aggregator_sdk.config.config import Config
from metric_aggregator_sdk.aggregator_manager import AggregatorAPI
from metric_aggregator_sdk.collector_agent import CollectorAgent

# 2. Import your devices (LocalDevice, HuggingFaceDevice, etc.)
from client.devices import LocalDevice, HuggingFaceDevice

class Application:
    def __init__(self, script_path: str = __file__, config_path: str = "default_config.json"):
        """
        Demonstrates a client application that:
          - Loads SDK config (defaults or custom)
          - Sets up logging
          - Creates devices
          - Instantiates an aggregator
          - Optionally uses collector agents to gather metrics at intervals
        """
        # ---------------------------------------------------------
        # A) Load the SDK Config (which includes aggregator settings)
        # ---------------------------------------------------------
        # By default, it loads from "default_config.json".
        # If you want a custom config, just change config_path or pass your own path.
        self.sdk_config = Config(script_path=script_path, config_path=config_path)
        
        # B) Setup logging for the entire application using the config
        # This sets up both console and file logging if enabled.
        self.logger = self.sdk_config.setup_logging()

        # ---------------------------------------------------------
        # C) Create Device Instances
        # ---------------------------------------------------------
        # For example, a local device that collects system metrics
        self.local_device = LocalDevice("Justyna's Laptop")

        # And a Hugging Face device that queries the HF API
        # (Here we assume the HF device constructor takes some config object)
        hf_collector_config = self.sdk_config.device_config.huggingface
        self.hf_device = HuggingFaceDevice(
            config=hf_collector_config,
            name="Hugging Face Top Models"
        )

        # ---------------------------------------------------------
        # D) Instantiate the AggregatorAPI from the SDK
        # ---------------------------------------------------------
        # We only supply GUID and aggregator name. The aggregator will read:
        # - base_url
        # - interval
        # - retry_interval
        # from the aggregator SDK config automatically.
        self.aggregator = AggregatorAPI(
            guid="123e4567-e89b-12d3-a456-426655440000",
            name="My Aggregator",
            script_path=script_path,
            config_path=config_path,
            logger=self.logger
        )
        

        # Register devices with the aggregator (for command relaying if needed)
        self.aggregator.register_device(self.local_device)
        self.aggregator.register_device(self.hf_device)

        # ---------------------------------------------------------
        # E) Create Collector Agents for each device
        # ---------------------------------------------------------
        # Each collector agent runs on its own thread, collecting snapshots
        # at a specified interval, and calling aggregator.add_snapshot(...).
        self.local_agent = CollectorAgent(
            aggregator=self.aggregator,
            device=self.local_device,
            interval=10.0,  # e.g. collect local metrics every 10 seconds
            logger=self.logger.getChild("LocalCollector")
        )
        self.hf_agent = CollectorAgent(
            aggregator=self.aggregator,
            device=self.hf_device,
            interval=60.0,  # e.g. collect HF metrics every 60 seconds
            logger=self.logger.getChild("HFCollector")
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
    """
    Example usage:

    # By default, it loads aggregator settings from default_config.json
    app = Application(script_path=__file__, config_path="default_config.json")
    # If you want a custom config:
    # app = Application(script_path=__file__, config_path="my_custom_config.json")

    app.start()
    """
    app = Application()
    app.start()
