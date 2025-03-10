import logging
import psutil
import requests
import GPUtil
from typing import Dict

from metric_aggregator_sdk.device import Device
from metric_aggregator_sdk.dto_models import DeviceSnapshot, Numeric

class LocalDevice(Device):
    """
    A concrete device class for collecting local system metrics.
    """
    def __init__(self, name: str = "Local Device", logger: logging.Logger = logging.getLogger("__name__")):
        super().__init__(name)
        self.logger = logger

    def handle_command(self, command: str):
        self.logger.info("LocalDevice received command: %s", command)
        if command == "restart_collector":
            self.restart_collector()

    def restart_collector(self):
        self.logger.info("Restarting collector on LocalDevice...")
        # TODO: Implement collector restart logic here.

    def collect_metrics(self) -> DeviceSnapshot:
        """
        Collects system metrics (CPU, RAM, disk, GPU) and returns a DeviceSnapshot.
        """
        try:
            cpu_usage = psutil.cpu_percent(interval=None)
            memory_info = psutil.virtual_memory()
            ram_usage_percent = memory_info.percent
            disk_info = psutil.disk_usage('/')
            disk_usage_percent = disk_info.percent

            # Attempt to collect GPU metrics
            gpu_metrics = {}
            try:
                gpus = GPUtil.getGPUs()
                for gpu in gpus:
                    gpu_id = gpu.id
                    gpu_metrics[f"GPU {gpu_id} usage (%)"] = gpu.load * 100
                    gpu_metrics[f"GPU {gpu_id} temperature (°C)"] = gpu.temperature
                    gpu_metrics[f"GPU {gpu_id} total memory (MB)"] = gpu.memoryTotal
                    gpu_metrics[f"GPU {gpu_id} used memory (MB)"] = gpu.memoryUsed
                    gpu_metrics[f"GPU {gpu_id} memory usage (%)"] = (
                        (gpu.memoryUsed / gpu.memoryTotal) * 100 if gpu.memoryTotal > 0 else 0.0
                    )
            except Exception as gpu_exc:
                self.logger.warning("LocalDevice: Could not gather GPU metrics: %s", gpu_exc)

            # Combine metrics into one dictionary
            metrics: Dict[str, Numeric] = {
                "CPU usage (%)": cpu_usage,
                "RAM usage (%)": ram_usage_percent,
                "Disk usage (%)": disk_usage_percent,
            }
            metrics.update(gpu_metrics)
            self.logger.info("LocalDevice collected metrics: %s", metrics)

            # Create and return a DeviceSnapshot
            snapshot = DeviceSnapshot(device_name=self.name, metrics=metrics)
            return snapshot

        except Exception as exc:
            self.logger.error("LocalDevice failed to collect metrics: %s", exc, exc_info=True)
            return DeviceSnapshot(device_name=self.name, metrics={})


class HuggingFaceDevice(Device):
    """
    A concrete device class for collecting metrics from the Hugging Face API.
    """

    def __init__(self, config, name: str = "Hugging Face Top Models", logger: logging.Logger = logging.getLogger("__name__")):
        """
        :param config: A configuration object/dictionary for Hugging Face (e.g., containing base_url, endpoint, params, and num_models).
        """
        super().__init__(name)
        self.logger = logger
        self.config = config
        self.base_url = config.base_url
        self.endpoint = config.endpoint
        self.params = config.params
        self.num_models = config.num_models

    def handle_command(self, command: str):
        """
        Handle a command sent from the aggregator.
        """
        self.logger.info("HuggingFaceDevice received command: %s", command)

    def collect_metrics(self) -> DeviceSnapshot:
        """
        Fetches data from the Hugging Face models API and returns a DeviceSnapshot with relevant metrics.
        """
        url = f"{self.base_url}{self.endpoint}"
        try:
            self.logger.debug("HuggingFaceDevice fetching data from %s with params %s", url, self.params)
            response = requests.get(url, params=self.params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if not isinstance(data, list):
                self.logger.warning("HuggingFaceDevice: Unexpected data format (expected a list).")
                return DeviceSnapshot(device_name=self.name, metrics={})

            top_models = data[:self.num_models]
            metrics = {}
            for _, model in enumerate(top_models, start=1):
                metrics[model.get("modelId")] = model.get("downloads")

            self.logger.info("HuggingFaceDevice collected metrics: %s", metrics)
            return DeviceSnapshot(device_name=self.name, metrics=metrics)

        except Exception as exc:
            self.logger.error("HuggingFaceDevice failed to collect metrics: %s", exc, exc_info=True)
            return DeviceSnapshot(device_name=self.name, metrics={})