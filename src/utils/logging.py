"""Logging configuration for ServiceNow MCP Server."""

import logging
import sys
from typing import Optional

from ..config.settings import ServerConfig


def setup_logging(config: Optional[ServerConfig] = None) -> logging.Logger:
    """Set up logging configuration for the ServiceNow MCP server.
    
    Args:
        config: Server configuration containing logging settings
        
    Returns:
        logging.Logger: Configured logger instance
    """
    if config is None:
        from ..config.settings import load_server_config
        config = load_server_config()
    
    # Create logger
    logger = logging.getLogger("src")
    logger.setLevel(getattr(logging, config.log_level))
    
    # Remove existing handlers to avoid duplicates
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create console handler
    #console_handler = logging.StreamHandler(sys.stdout) # causes [error] Unexpected non-whitespace character after JSON ...
    console_handler = logging.StreamHandler(sys.stderr) #fix
    console_handler.setLevel(getattr(logging, config.log_level))
    
    # Create formatter
    formatter = logging.Formatter(config.log_format)
    console_handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(console_handler)
    
    # Prevent propagation to root logger
    logger.propagate = False
    
    return logger


def get_logger(name: str = "src") -> logging.Logger:
    """Get a logger instance with the specified name.
    
    Args:
        name: Logger name (defaults to main src logger)
        
    Returns:
        logging.Logger: Logger instance
    """
    return logging.getLogger(name)