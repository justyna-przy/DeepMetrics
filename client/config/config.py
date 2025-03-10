import json
import os
import logging
from dataclasses import dataclass
from pydantic.dataclasses import dataclass as pydantic_dataclass
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv
import colorlog
import logging.handlers
from pathlib import Path

@dataclass
class BaseOutput:
    enabled: bool
    level: str
    format: str
    date_format: str

    def get_level(self) -> int:
        return getattr(logging, self.level.upper())

@dataclass
class ConsoleOutput(BaseOutput):
    log_colors: Dict[str, str]

@dataclass
class FileOutput(BaseOutput):
    log_dir: str
    filename: str
    max_bytes: int
    backup_count: int

@dataclass
class LoggingConfig:
    console_output: ConsoleOutput
    file_output: FileOutput

@dataclass
class HuggingFaceConfig:
    base_url: str
    endpoint: str
    params: Dict[str, Any]
    num_models: int

@dataclass
class DeviceConfig:
    huggingface: HuggingFaceConfig

@pydantic_dataclass
class Config:
    logging_config: LoggingConfig
    device_config: DeviceConfig

    @staticmethod
    def set_working_directory(script_path: str) -> str:
        """
        Sets the working directory to the directory containing the calling script.
        This helps load files (like the config file) using relative paths.
        """
        script_dir = os.path.dirname(os.path.abspath(script_path))
        os.chdir(script_dir)
        return script_dir

    def __init__(self, script_path: Optional[str] = None, config_path: str = "config.json"):
        """
        Loads config from a JSON file, validates it with Pydantic, and stores the config sections.
        Args:
            script_path: The __file__ value from the calling script.
            config_path: Path to the JSON configuration file.
        """
        load_dotenv()  # Load env variables from .env if present

        if script_path:
            self.set_working_directory(script_path)

        raw_config = self._load_config(config_path)

        self._replace_env_vars(raw_config)

        # Explicitly create nested configuration objects for strong typing.
        self.logging_config = LoggingConfig(
            console_output=ConsoleOutput(**raw_config.get("logging_config", {}).get("console_output", {})),
            file_output=FileOutput(**raw_config.get("logging_config", {}).get("file_output", {}))
        )
        self.device_config = DeviceConfig(
            huggingface=HuggingFaceConfig(**raw_config.get("device_config", {}).get("huggingface", {}))
        )

    def _load_config(self, config_path: str) -> dict:
        """
        Loads the JSON configuration file and returns its contents as a dictionary.
        """
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Config file not found: {config_path}")
        with open(config_path, 'r') as f:
            return json.load(f)

    @staticmethod
    def _replace_env_vars(config: dict) -> None:
        """
        Recursively searches for string values that start with "${" and end with "}"
        and replaces them with the corresponding environment variable value.
        """
        for key, value in config.items():
            if isinstance(value, dict):
                Config._replace_env_vars(value)
            elif isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                env_var = value[2:-1]
                env_value = os.getenv(env_var)
                if env_value is None:
                    raise ValueError(f"Environment variable {env_var} not found")
                config[key] = env_value

    def setup_logging(self) -> logging.Logger:
        """
        Sets up logging configuration based on the logging_config section.
        Returns a configured root logger.
        Creates log directories, clears existing handlers,
        and configures both console and file handlers.
        """
        # Create logs directory if file output is enabled
        if self.logging_config.file_output.enabled:
            os.makedirs(self.logging_config.file_output.log_dir, exist_ok=True)

        # Get the root logger
        logger = logging.getLogger()

        # Set base filtering level to the lowest level of enabled handlers.
        enabled_levels = []
        if self.logging_config.console_output.enabled:
            enabled_levels.append(self.logging_config.console_output.get_level())
        if self.logging_config.file_output.enabled:
            enabled_levels.append(self.logging_config.file_output.get_level())
        root_level = min(enabled_levels) if enabled_levels else logging.WARNING
        logger.setLevel(root_level)

        # Clear any existing handlers
        logger.handlers.clear()

        # Add console handler if enabled
        if self.logging_config.console_output.enabled:
            console_handler = logging.StreamHandler()
            console_formatter = colorlog.ColoredFormatter(
                fmt='%(log_color)s' + self.logging_config.console_output.format,
                datefmt=self.logging_config.console_output.date_format,
                reset=True,
                log_colors=self.logging_config.console_output.log_colors
            )
            console_handler.setFormatter(console_formatter)
            console_handler.setLevel(self.logging_config.console_output.get_level())
            logger.addHandler(console_handler)

        # Add file handler if enabled
        if self.logging_config.file_output.enabled:
            file_path = os.path.join(self.logging_config.file_output.log_dir, self.logging_config.file_output.filename)
            file_handler = logging.handlers.RotatingFileHandler(
                file_path,
                maxBytes=self.logging_config.file_output.max_bytes,
                backupCount=self.logging_config.file_output.backup_count
            )
            file_formatter = logging.Formatter(
                fmt=self.logging_config.file_output.format,
                datefmt=self.logging_config.file_output.date_format
            )
            file_handler.setFormatter(file_formatter)
            file_handler.setLevel(self.logging_config.file_output.get_level())
            logger.addHandler(file_handler)

        return logger
