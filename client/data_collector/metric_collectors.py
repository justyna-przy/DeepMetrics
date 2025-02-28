# collectors.py
import logging
import requests
import psutil
import GPUtil
from typing import Dict, Any
from config.config import HuggingFaceCollectorConfig


# ======================= Local System Collector =======================
class LocalMetricsCollector:
    """
    Collects local system metrics using psutil (CPU, RAM usage, etc.).
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__) 

    def collect_metrics(self) -> Dict[str, Any]:
        """
        Collects GPU, GPU temperature, GPU memory, CPU, disk usage, and RAM usage metrics
        from the local system. Returns a dict of metrics. If an error occurs,
        logs the exception and returns an empty dict.
        """
        try:
            # CPU usage (%)
            cpu_usage = psutil.cpu_percent(interval=None)

            # RAM usage (%)
            memory_info = psutil.virtual_memory()
            ram_usage_percent = memory_info.percent

            # Disk usage (% of root or main partition)
            disk_info = psutil.disk_usage('/')
            disk_usage_percent = disk_info.percent

            # GPU metrics 
            gpu_metrics = {}
            try:
                gpus = GPUtil.getGPUs()
                for gpu in gpus:
                    gpu_id = gpu.id
                    gpu_metrics[f"gpu_{gpu_id}_usage_percent"] = gpu.load * 100
                    gpu_metrics[f"gpu_{gpu_id}_temperature_celsius"] = gpu.temperature
                    gpu_metrics[f"gpu_{gpu_id}_memory_total_mb"] = gpu.memoryTotal
                    gpu_metrics[f"gpu_{gpu_id}_memory_used_mb"] = gpu.memoryUsed
                    gpu_metrics[f"gpu_{gpu_id}_memory_usage_percent"] = (
                        (gpu.memoryUsed / gpu.memoryTotal) * 100 
                        if gpu.memoryTotal > 0 else 0.0
                    )
            except Exception as gpu_exc:
                # If GPU collection fails, warn but continue with other metrics
                self.logger.warning(
                    "[Local] Could not gather GPU metrics: %(error)s", 
                    {"error": gpu_exc}
                )

            # Combine everything into one dictionary
            metrics = {
                "cpu_usage_percent": cpu_usage,
                "ram_usage_percent": ram_usage_percent,
                "disk_usage_percent": disk_usage_percent,
            }
            metrics.update(gpu_metrics)
            self.logger.info(
                "[Local] Collected metrics: %(metrics)s", 
                {"metrics": metrics}
            )

            return metrics

        except Exception as exc:
            self.logger.error(f"[Local] Failed to collect system metrics: {exc}", exc_info=True)
            return {}


# ======================= Hugging Face Collector =======================
class HuggingFaceCollector:
    """
    Collects top trending models from Hugging Face's API.
    """

    def __init__(self, config: HuggingFaceCollectorConfig):
        """
        :param config: A config dictionary specific to Hugging Face collector.
                       e.g. {
                           "base_url": "https://huggingface.co",
                           "endpoint": "/api/models",
                           "params": {
                               "sort": "downloads",
                               "direction": "desc",
                               "limit": 10
                           }
                       }
        """
        self.config = config
        self.logger = logging.getLogger(__name__)

        self.base_url = config.base_url
        self.endpoint = config.endpoint
        self.params = config.params
        self.num_models = config.num_models


    def collect_metrics(self) -> Dict[str, Any]:
        """
        Fetches data from the Hugging Face models API and returns a dictionary
        of relevant metrics, e.g. top downloaded models.
        """
        url = f"{self.base_url}{self.endpoint}"
        try:
            self.logger.debug(
                "[HuggingFace] Fetching data from %(url)s with params=%(params)s",
                  {"url": url, "params": self.params}
                )
            response = requests.get(url, params=self.params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if not isinstance(data, list):
                self.logger.warning("[HuggingFace] Unexpected data format (expected a list).")
                return {}

            top_models = data[:self.num_models]
            metrics = {}
            for i, model in enumerate(top_models, start=1):
                metrics[f"model_{i}_name"] = model.get("modelId")
                metrics[f"model_{i}_downloads"] = model.get("downloads")

            self.logger.debug(
                "[HuggingFace] Collected metrics: %(metrics)s",
                  {"metrics": metrics}
                )
            return metrics

        except Exception as exc:
            self.logger.error(
                "[HuggingFace] Failed to fetch or parse data: %(error)s", 
                {"error": exc}
            )
            return {}
