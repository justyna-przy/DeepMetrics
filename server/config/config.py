import json
import os
import logging
from dataclasses import dataclass
from typing import Dict, Any, List
from dotenv import load_dotenv
import colorlog
import logging.handlers
from pathlib import Path

@dataclass
class ServerConfig:
    allowed_origins: List[str]

class Config:
    """
    Loads server configuration from JSON and environment variables.
    Provides a method to set up structured logging.
    """
    server_settings: ServerConfig
    db_url: str
    uvicorn_log_config: Dict[str, Any]

    def __init__(self, config_path: str = "config/config.json"):
        load_dotenv()

        raw_config = self._load_config(config_path)

        self._replace_env_vars(raw_config)

        server_dict = raw_config.get("server_config", {})

        self.server_settings = ServerConfig(
            allowed_origins=server_dict.get("allowed_origins", ["*"])
        )

        self.db_url = os.getenv("DATABASE_URL")
        self.uvicorn_log_config = raw_config.get("uvicorn_log_config", {})

    def _load_config(self, config_path: str) -> dict:
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Config file not found: {config_path}, Current working directory: {os.getcwd()}")
        with open(config_path, "r") as f:
            return json.load(f)

    def _replace_env_vars(self, config: dict) -> None:
        """
        Recursively searches for string values that start with '${' and end with '}'
        and replaces them with the corresponding environment variable value.
        """
        for key, value in config.items():
            if isinstance(value, dict):
                self._replace_env_vars(value)
            elif isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                env_var = value[2:-1]
                env_value = os.getenv(env_var)
                if env_value is None:
                    raise ValueError(f"Environment variable {env_var} not found.")
                config[key] = env_value

 