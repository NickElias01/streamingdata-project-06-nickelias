"""
Logging Utility
-------------

Custom logging system for the Energy Monitoring Suite.
Provides color-coded console output and separated log files
based on message severity.

This module provides logging functionality for:
    - Normal operations (DEBUG, INFO)
    - Alert conditions (WARNING)
    - Error conditions (ERROR, CRITICAL)
    - Color-coded console output
    - Rotating file handlers with size limits

Features:
    - Separate log files for different severity levels
    - Color-coded console output
    - Rotating log files with size limits
    - Thread-safe logging operations
    - Customizable message formatting
    - Automated log directory management

Author: Elias Analytics
Version: 1.0.0
License: MIT
"""

import logging
import os
import sys
from datetime import datetime
from logging.handlers import RotatingFileHandler
from colorama import init, Fore, Style

# Initialize colorama for Windows color support
init()

# Create log directories if they don't exist
LOG_DIR = 'logs'
NORMAL_LOG_DIR = os.path.join(LOG_DIR, 'normal')     # For DEBUG and INFO messages
ALERT_LOG_DIR = os.path.join(LOG_DIR, 'alerts')      # For WARNING messages
ERROR_LOG_DIR = os.path.join(LOG_DIR, 'errors')      # For ERROR and CRITICAL messages

# Ensure log directories exist
for directory in [NORMAL_LOG_DIR, ALERT_LOG_DIR, ERROR_LOG_DIR]:
    os.makedirs(directory, exist_ok=True)

# Log file configuration
current_date = datetime.now().strftime("%Y%m%d")
NORMAL_LOG_FILE = os.path.join(NORMAL_LOG_DIR, f'normal_{current_date}.log')
ALERT_LOG_FILE = os.path.join(ALERT_LOG_DIR, f'alerts_{current_date}.log')
ERROR_LOG_FILE = os.path.join(ERROR_LOG_DIR, f'errors_{current_date}.log')
MAX_BYTES = 10 * 1024 * 1024  # 10MB maximum file size
BACKUP_COUNT = 5               # Keep 5 backup files

class ColoredFormatter(logging.Formatter):
    """
    Custom formatter that adds colors to log levels in console output.
    
    Attributes:
        COLORS (dict): Mapping of log levels to their display colors
    """
    
    COLORS = {
        'DEBUG': Fore.BLUE,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.RED + Style.BRIGHT
    }

    def format(self, record):
        """
        Format log record with appropriate color for console display.
        
        Args:
            record (LogRecord): The log record to format
            
        Returns:
            str: Formatted log message with color codes
        """
        if record.levelname in self.COLORS:
            record.levelname = f"{self.COLORS[record.levelname]}{record.levelname}{Style.RESET_ALL}"
        return super().format(record)

class SeparatedLogger:
    """
    Custom logger that separates logs by severity level into different files.
    
    Provides methods for logging different types of messages and automatically
    routes them to appropriate log files based on severity.
    
    Attributes:
        logger (Logger): Base logger instance
    """
    
    def __init__(self, name):
        """
        Initialize logger with separated handlers for different severity levels.
        
        Args:
            name (str): Logger name, typically __name__ of calling module
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        if not self.logger.handlers:
            # Normal logs (INFO and DEBUG)
            normal_handler = RotatingFileHandler(
                NORMAL_LOG_FILE, maxBytes=MAX_BYTES, backupCount=BACKUP_COUNT
            )
            normal_handler.setLevel(logging.DEBUG)
            normal_filter = lambda record: record.levelno <= logging.INFO
            normal_handler.addFilter(normal_filter)
            
            # Alert logs (WARNING)
            alert_handler = RotatingFileHandler(
                ALERT_LOG_FILE, maxBytes=MAX_BYTES, backupCount=BACKUP_COUNT
            )
            alert_handler.setLevel(logging.WARNING)
            alert_filter = lambda record: record.levelno == logging.WARNING
            alert_handler.addFilter(alert_filter)
            
            # Error logs (ERROR and CRITICAL)
            error_handler = RotatingFileHandler(
                ERROR_LOG_FILE, maxBytes=MAX_BYTES, backupCount=BACKUP_COUNT
            )
            error_handler.setLevel(logging.ERROR)
            
            # Console handler with colors (all levels)
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.INFO)
            
            # Set formatters
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            console_formatter = ColoredFormatter(
                '%(asctime)s - %(levelname)s - %(message)s'
            )
            
            # Add all handlers
            for handler in [normal_handler, alert_handler, error_handler, console_handler]:
                handler.setFormatter(file_formatter if handler != console_handler else console_formatter)
                self.logger.addHandler(handler)

    def debug(self, msg): 
        """Log DEBUG level message."""
        self.logger.debug(msg)
        
    def info(self, msg): 
        """Log INFO level message."""
        self.logger.info(msg)
        
    def warning(self, msg): 
        """Log WARNING level message."""
        self.logger.warning(msg)
        
    def error(self, msg): 
        """Log ERROR level message."""
        self.logger.error(msg)
        
    def critical(self, msg): 
        """Log CRITICAL level message."""
        self.logger.critical(msg)

    def log_kafka_message(self, data, region):
        """
        Log Kafka message reception.
        
        Args:
            data (dict): Message data containing power and temperature readings
            region (str): Region name the data is from
        """
        self.info(f"Received data from {region}: Power={data['power_usage_kW']}kW, "
                 f"Temp={data['temperature_C']}°C")

    def log_alert(self, alert_type, region, value):
        """
        Log system alerts for threshold violations.
        
        Args:
            alert_type (str): Type of alert ('high_power', 'low_power', etc.)
            region (str): Region where alert occurred
            value (float): Value that triggered the alert
        """
        alert_messages = {
            'high_power': f"HIGH POWER USAGE in {region}: {value}kW",
            'low_power': f"LOW POWER USAGE in {region}: {value}kW",
            'high_temp': f"HIGH TEMPERATURE in {region}: {value}°C",
            'low_temp': f"LOW TEMPERATURE in {region}: {value}°C",
            'low_renewable': f"LOW RENEWABLE % in {region}: {value}%"
        }
        self.warning(alert_messages.get(alert_type, f"Unknown alert in {region}: {value}"))

    def log_error(self, error_message, error_type="ERROR"):
        """
        Log system errors with optional type specification.
        
        Args:
            error_message (str): Description of the error
            error_type (str, optional): Type of error. Defaults to "ERROR"
        """
        self.error(f"{error_type}: {error_message}")

def setup_logger(name):
    """
    Create and return a logger instance.
    
    Args:
        name (str): Name for the logger, typically __name__
        
    Returns:
        SeparatedLogger: Configured logger instance
        
    Example:
        >>> logger = setup_logger(__name__)
        >>> logger.info("Application started")
        >>> logger.log_alert("high_power", "Denver", 6000)
    """
    return SeparatedLogger(name)