import json
import os
import logging
from dataclasses import dataclass
from pydantic.dataclasses import dataclass as pydantic_dataclass
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv

@dataclass
class DatabaseConfig:
    host: str
    port: int

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
    log_colors: dict[str, str]

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
class HuggingFaceCollectorConfig:
    base_url: str
    endpoint: str
    params: Dict[str, Any]
    num_models: int

@dataclass
class StockPriceCollectorConfig:
    base_url: str
    api_key: str
    companies: List[str]

@dataclass
class CollectorsConfig:
    huggingface_collector: HuggingFaceCollectorConfig
    stock_price_collector: StockPriceCollectorConfig

@pydantic_dataclass
class Config:
    database_config: DatabaseConfig
    logging_config: LoggingConfig
    collectors_config: CollectorsConfig

    @staticmethod
    def set_working_directory(script_path: str) -> str:
        script_dir = os.path.dirname(os.path.abspath(script_path))
        os.chdir(script_dir)
        return script_dir

    @classmethod
    def load_config(cls, script_path: Optional[str] = None, config_path: str = "config.json") -> "Config":
        """
        Loads config from a JSON file and returns a Pydantic-validated Config instance.
        """

        load_dotenv()

        if script_path:
            cls.set_working_directory(script_path)
        
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Config file not found: {config_path}")
        
        with open(config_path, 'r') as f:
            data = json.load(f)
        
        cls._replace_env_vars(data)

        # **data passes the keys directly to Config(database=..., logging_config=...)
        return cls(**data)
    
    @staticmethod
    def _replace_env_vars(config: dict) -> None:
        """Recursively replace environment variables in config values."""
        for key, value in config.items():
            if isinstance(value, dict):
                Config._replace_env_vars(value)
            elif isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                env_var = value[2:-1]
                env_value = os.getenv(env_var)
                if env_value is None:
                    raise ValueError(f"Environment variable {env_var} not found")
                config[key] = env_value
