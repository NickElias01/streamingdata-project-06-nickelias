# utils_logger.py

import logging

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(message)s',
    level=logging.INFO
)

def get_logger(name):
    """Get a logger instance."""
    return logging.getLogger(name)
