import json
import os
from dataclasses import dataclass


@dataclass
class AggregatorSDKConfig:
    base_url: str
    snapshots_endpoint: str
    interval: float
    retry_interval: float


class Config:
    aggregatorSDK: AggregatorSDKConfig

    @staticmethod
    def set_working_directory(script_path: str) -> str:
        """
        Sets working directory to the location of the calling script's path as supplied by __file__.
        Can be used to set the working directory to the location in which the config file is found
        without resorting to absolute paths.

        Args:
            script_path: The __file__ value from the calling script.
        Returns:
            The new working directory path.
        """
        script_dir = os.path.dirname(os.path.abspath(script_path))
        os.chdir(script_dir)
        return script_dir

    def __init__(self, script_path: str = None, config_path: str = "config.json"):
        """
        Loads config from a JSON file and returns a Config instance.

        Args:
            script_path: The __file__ value from the calling script.
            config_path: The path to the JSON config file.
        """
        if script_path:
            self.set_working_directory(script_path)
        self._config = self._load_config(config_path)
        # Create an AggregatorSDKConfig instance using values from the JSON.
        self.aggregatorSDK = AggregatorSDKConfig(**self._config["aggregator_sdk_config"])

    def _load_config(self, config_path: str) -> dict:
        """
        Loads a JSON config file and returns it as a dictionary.
        """
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Config file not found: {config_path}")
        with open(config_path, 'r') as f:
            return json.load(f)
