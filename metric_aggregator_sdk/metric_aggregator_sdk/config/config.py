import json
import os
from dataclasses import dataclass
from typing import Optional

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
        Sets working directory to the location of the calling script.
        This is used only when a custom config is provided.
        """
        script_dir = os.path.dirname(os.path.abspath(script_path))
        os.chdir(script_dir)
        return script_dir

    def __init__(self, script_path: Optional[str] = None, config_path: str = "default_config.json"):
        """
        Loads config from a JSON file.
        If the client uses a custom config (i.e. config_path != "default_config.json") and
        supplies a script_path, the working directory is set to that script's directory.
        Otherwise, the default config (default_config.json) is loaded from the SDK's config folder.
        """
        if config_path != "default_config.json" and script_path:
            # Custom config: change cwd to the calling script's directory.
            self.set_working_directory(script_path)
        else:
            # Use the default config shipped with the SDK, located relative to this file.
            config_path = os.path.join(os.path.dirname(__file__), config_path)

        self._config = self._load_config(config_path)
        self.aggregatorSDK = AggregatorSDKConfig(**self._config["aggregator_sdk_config"])

    def _load_config(self, config_path: str) -> dict:
        """
        Loads a JSON config file and returns its contents as a dictionary.
        """
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Config file not found: {config_path}, Current working directory: {os.getcwd()}")
        with open(config_path, 'r') as f:
            return json.load(f)
