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
NORMAL_LOG_DIR = os.path.join(LOG_DIR, 'normal')
ALERT_LOG_DIR = os.path.join(LOG_DIR, 'alerts')
ERROR_LOG_DIR = os.path.join(LOG_DIR, 'errors')

for directory in [NORMAL_LOG_DIR, ALERT_LOG_DIR, ERROR_LOG_DIR]:
    os.makedirs(directory, exist_ok=True)

# Log file configuration
current_date = datetime.now().strftime("%Y%m%d")
NORMAL_LOG_FILE = os.path.join(NORMAL_LOG_DIR, f'normal_{current_date}.log')
ALERT_LOG_FILE = os.path.join(ALERT_LOG_DIR, f'alerts_{current_date}.log')
ERROR_LOG_FILE = os.path.join(ERROR_LOG_DIR, f'errors_{current_date}.log')
MAX_BYTES = 10 * 1024 * 1024  # 10MB
BACKUP_COUNT = 5

class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for different log levels."""
    COLORS = {
        'DEBUG': Fore.BLUE,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.RED + Style.BRIGHT
    }

    def format(self, record):
        if record.levelname in self.COLORS:
            record.levelname = f"{self.COLORS[record.levelname]}{record.levelname}{Style.RESET_ALL}"
        return super().format(record)

class SeparatedLogger:
    """Custom logger that separates logs by severity."""
    def __init__(self, name):
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

    def debug(self, msg): self.logger.debug(msg)
    def info(self, msg): self.logger.info(msg)
    def warning(self, msg): self.logger.warning(msg)
    def error(self, msg): self.logger.error(msg)
    def critical(self, msg): self.logger.critical(msg)

    def log_kafka_message(self, data, region):
        """Log Kafka message reception."""
        self.info(f"Received data from {region}: Power={data['power_usage_kW']}kW, "
                 f"Temp={data['temperature_C']}°C")

    def log_alert(self, alert_type, region, value):
        """Log system alerts."""
        alert_messages = {
            'high_power': f"HIGH POWER USAGE in {region}: {value}kW",
            'low_power': f"LOW POWER USAGE in {region}: {value}kW",
            'high_temp': f"HIGH TEMPERATURE in {region}: {value}°C",
            'low_temp': f"LOW TEMPERATURE in {region}: {value}°C",
            'low_renewable': f"LOW RENEWABLE % in {region}: {value}%"
        }
        self.warning(alert_messages.get(alert_type, f"Unknown alert in {region}: {value}"))

    def log_error(self, error_message, error_type="ERROR"):
        """Log system errors."""
        self.error(f"{error_type}: {error_message}")

def setup_logger(name):
    """Create and return a logger instance."""
    return SeparatedLogger(name)