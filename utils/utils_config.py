"""
Configuration Utility
-------------------

Central configuration management for the Energy Monitoring Suite.
Handles environment variables, system constants, and threshold definitions
for the energy monitoring system.

This module provides configuration settings for:
    - Kafka connection and topics
    - Database settings
    - Monitoring thresholds
    - Regional definitions
    - System intervals

Environment Variables:
    KAFKA_TOPIC (str): Topic name for energy data messages
    KAFKA_BROKER (str): Kafka broker connection address
    GROUP_ID (str): Consumer group identifier
    BASE_DATA_DIR (str): Base directory for data storage
    SQLITE_DB_FILE_NAME (str): SQLite database filename
    MESSAGE_INTERVAL_SECONDS (int): Delay between message batches

Author: Elias Analytics
Version: 1.0.0
License: MIT
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Kafka Configuration
# ------------------
KAFKA_TOPIC = os.getenv('KAFKA_TOPIC', 'energy_data')
KAFKA_BROKER = os.getenv('KAFKA_BROKER_ADDRESS', 'localhost:9092')
GROUP_ID = os.getenv('ENERGY_CONSUMER_GROUP_ID', 'energy_monitor')

# File System Configuration
# -----------------------
BASE_DATA_DIR = os.getenv('BASE_DATA_DIR', 'data')
SQLITE_DB_FILE_NAME = os.getenv('SQLITE_DB_FILE_NAME', 'energy_usage.sqlite')
MESSAGE_INTERVAL = int(os.getenv('MESSAGE_INTERVAL_SECONDS', '5'))

# Regional Configuration
# --------------------
REGIONS_CONFIG = {
    'Denver': {
        'name': 'Denver',    # Capital city
        'lat': 39.7392,
        'lon': -104.9903
    },
    'Boulder': {
        'name': 'Boulder',   # Tech hub
        'lat': 40.0150,
        'lon': -105.2705
    },
    'Aurora': {
        'name': 'Aurora',    # Eastern metro
        'lat': 39.7294,
        'lon': -104.8319
    },
    'Lakewood': {
        'name': 'Lakewood',  # Western metro
        'lat': 39.7047,
        'lon': -105.0814
    },
    'Golden': {
        'name': 'Golden',    # Mining district
        'lat': 39.7555,
        'lon': -105.2211
    }
}

REGIONS = list(REGIONS_CONFIG.keys())

# Monitoring Thresholds
# -------------------
# Power usage thresholds (kilowatts)
POWER_HIGH_THRESHOLD = 5000  # Alert if usage exceeds this value
POWER_LOW_THRESHOLD = 500    # Alert if usage falls below this value

# Temperature thresholds (Celsius)
TEMP_HIGH_THRESHOLD = 50     # Alert if temperature exceeds this value
TEMP_LOW_THRESHOLD = 0       # Alert if temperature falls below this value

# Renewable energy threshold (percentage)
RENEWABLE_LOW_THRESHOLD = 5   # Alert if renewable percentage falls below this value

def validate_config():
    """
    Validate all required configuration values.
    
    Checks for presence and validity of required configuration settings.
    Raises ValueError if any required settings are missing or invalid.
    
    Returns:
        bool: True if all configurations are valid
        
    Raises:
        ValueError: If any required configuration is missing or invalid
    """
    required_configs = {
        'KAFKA_TOPIC': KAFKA_TOPIC,
        'KAFKA_BROKER': KAFKA_BROKER,
        'GROUP_ID': GROUP_ID,
        'BASE_DATA_DIR': BASE_DATA_DIR,
        'SQLITE_DB_FILE_NAME': SQLITE_DB_FILE_NAME
    }
    
    missing = [k for k, v in required_configs.items() if not v]
    if missing:
        raise ValueError(f"Missing required configuration(s): {', '.join(missing)}")
    
    try:
        int(MESSAGE_INTERVAL)
    except (TypeError, ValueError):
        raise ValueError("MESSAGE_INTERVAL must be a valid integer")
    
    return True

# Validate configuration on module import
validate_config()