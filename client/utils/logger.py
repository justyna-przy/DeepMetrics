# Implement logging class
# Add colors and a format from config

import logging
import logging.handlers
import colorlog
from pathlib import Path
import os
from config.config import LoggingConfig

def setup_logging(logging_config: LoggingConfig) -> logging.Logger:
    """
    Sets up logging configuration based on the provided config
    
    Args:
        logging_config: Configuration for both console and file logging
    
    Returns:
        Configured root logger
    """
    # Create logs directory if needed and file output is enabled
    if logging_config.file_output.enabled:
        os.makedirs(logging_config.file_output.log_dir, exist_ok=True)

    # Gets the root logger
    logger = logging.getLogger()

    # Set base filtering level
    enabled_levels = []
    if logging_config.console_output.enabled:
        enabled_levels.append(logging_config.console_output.get_level())
    if logging_config.file_output.enabled:
        enabled_levels.append(logging_config.file_output.get_level())
        
    root_level = min(enabled_levels) if enabled_levels else logging.WARNING
    logger.setLevel(root_level)

    # Clear existing handlers
    logger.handlers.clear()
    
    # Setup console handler
    if logging_config.console_output.enabled:
        console_handler = logging.StreamHandler()
        console_formatter = colorlog.ColoredFormatter(
            fmt=logging_config.console_output.format,
            datefmt=logging_config.console_output.date_format,
            reset=True,
            log_colors=logging_config.console_output.log_colors
        )
        console_handler.setFormatter(console_formatter)
        console_handler.setLevel(logging_config.console_output.get_level())
        logger.addHandler(console_handler)
    
    # Setup file handler
    if logging_config.file_output.enabled:
        file_path = Path(logging_config.file_output.log_dir) / logging_config.file_output.filename
        file_handler = logging.handlers.RotatingFileHandler(
            file_path,
            maxBytes=logging_config.file_output.max_bytes,
            backupCount=logging_config.file_output.backup_count
        )
        file_formatter = logging.Formatter(
            fmt=logging_config.file_output.format,
            datefmt=logging_config.file_output.date_format
        )
        file_handler.setFormatter(file_formatter)
        file_handler.setLevel(logging_config.file_output.get_level())
        logger.addHandler(file_handler)
    
    return logger

