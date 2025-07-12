# DotA Coach Logging Configuration Module
# Centralized logging setup for the entire system
# Handles log formatting, rotation, and level configuration

import logging
import logging.handlers
from pathlib import Path
from typing import Optional

from .config import Config


def setup_logging(config: Config, log_file: Optional[str] = None) -> None:
    """
    Configure logging for the DotA Coach system.
    
    Args:
        config (Config): Configuration manager instance.
        log_file (Optional[str]): Override log file path.
    """
    # Get logging configuration
    log_level = config.get('logging.level', 'INFO')
    log_format = config.get('logging.format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    log_file_path = log_file or config.get('logging.file', 'logs/dota_coach.log')
    max_file_size = config.get('logging.max_file_size', '10MB')
    backup_count = config.get('logging.backup_count', 5)
    
    # Create logs directory if it doesn't exist
    log_path = Path(log_file_path)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Parse max file size
    if isinstance(max_file_size, str):
        if max_file_size.endswith('MB'):
            max_bytes = int(max_file_size[:-2]) * 1024 * 1024
        elif max_file_size.endswith('KB'):
            max_bytes = int(max_file_size[:-2]) * 1024
        else:
            max_bytes = int(max_file_size)
    else:
        max_bytes = max_file_size
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create formatter
    formatter = logging.Formatter(log_format)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, log_level.upper()))
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        log_file_path,
        maxBytes=max_bytes,
        backupCount=backup_count
    )
    file_handler.setLevel(getattr(logging, log_level.upper()))
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
    
    # Log the configuration
    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured - Level: {log_level}, File: {log_file_path}")


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name.
    
    Args:
        name (str): Logger name (typically __name__).
        
    Returns:
        logging.Logger: Configured logger instance.
    """
    return logging.getLogger(name)