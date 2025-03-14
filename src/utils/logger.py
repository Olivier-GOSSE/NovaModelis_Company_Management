"""
Logger utility for the application.
"""
import os
import sys
import logging
from logging.handlers import RotatingFileHandler

# Add the parent directory to sys.path to allow imports
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + '/../..'))

import config


def setup_logger():
    """
    Set up the application logger.
    
    Returns:
        logging.Logger: The configured logger.
    """
    # Create logs directory if it doesn't exist
    os.makedirs(os.path.dirname(config.LOG_FILE), exist_ok=True)
    
    # Create logger
    logger = logging.getLogger("novamodelisapp")
    logger.setLevel(getattr(logging, config.LOG_LEVEL))
    
    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, config.LOG_LEVEL))
    console_handler.setFormatter(formatter)
    
    # Create file handler
    file_handler = RotatingFileHandler(
        config.LOG_FILE,
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5
    )
    file_handler.setLevel(getattr(logging, config.LOG_LEVEL))
    file_handler.setFormatter(formatter)
    
    # Add handlers to logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger


# Create and export logger
logger = setup_logger()
