"""
Colorado Energy Data Consumer
------------------

A real-time energy monitoring system that consumes power usage and temperature data
from multiple regions in Colorado, visualizes the data, and stores it in a database.

This module is part of the Energy Monitoring Suite developed by Elias Analytics.
It provides real-time monitoring, alerting, and data visualization capabilities
for energy consumption and environmental metrics across different regions.

Features:
    - Real-time data consumption from Kafka
    - Dynamic visualization of power usage and temperature
    - Automated alert system for threshold violations
    - Persistent storage of monitoring data
    - Multi-threaded design for concurrent processing

Author: Elias Analytics
Version: 1.0.0
License: MIT
"""

# Standard library imports for basic functionality
import json
import os
import sys
from datetime import datetime
from threading import Thread

# Third-party imports for data visualization and message queue
import matplotlib
matplotlib.use('TkAgg')  # Set backend before importing pyplot to avoid runtime errors
from kafka import KafkaConsumer

# Local application imports for project-specific functionality
from utils.utils_config import (
    KAFKA_TOPIC,          # Topic name for Kafka messages
    KAFKA_BROKER,         # Kafka broker address
    GROUP_ID,            # Consumer group identifier
    BASE_DATA_DIR,       # Directory for storing data files
    SQLITE_DB_FILE_NAME  # SQLite database filename
)
from utils.utils_db_handler import DatabaseHandler      # Database operations
from utils.utils_alert_handler import AlertHandler     # Alert monitoring
from consumers.visualizer import EnergyVisualizer     # Real-time data visualization
from utils.utils_logger import setup_logger           # Logging configuration

# Initialize logger for this module
logger = setup_logger(__name__)

def consume_data(visualizer, db_handler):
    """
    Main consumer function that processes incoming Kafka messages.
    
    Args:
        visualizer (EnergyVisualizer): Handles real-time data visualization
        db_handler (DatabaseHandler): Manages database operations
    """
    # Initialize Kafka consumer with configuration
    consumer = KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BROKER,
        group_id=GROUP_ID,
        auto_offset_reset='earliest',  # Start reading from beginning if no offset found
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))  # Convert messages from bytes to JSON
    )

    # Initialize alert system
    alert_handler = AlertHandler()
    logger.info("Kafka consumer started successfully")    

    try:
        # Main message processing loop
        for message in consumer:
            try:
                # Extract message data
                data = message.value
                logger.info(f"Received data from {data['region']}: Power={data['power_usage_kW']}kW, "
                          f"Temp={data['temperature_C']}°C")
                
                # Check for threshold violations and log alerts
                alerts = alert_handler.check_alerts(data)
                if alerts:
                    for alert in alerts:
                        logger.warning(alert)
                
                # Store data and update visualization
                if db_handler.store_data(data):
                    logger.debug(f"Data stored in database: {data['region']} at {data['timestamp']}")
                    visualizer.update_data(data)  # Update real-time visualization
                else:
                    logger.error(f"Failed to store data in database for {data['region']}")
                    
            except Exception as e:
                # Handle message processing errors without crashing
                logger.error(f"Error processing message: {str(e)}")
                continue
                
    except KeyboardInterrupt:
        # Handle graceful shutdown on Ctrl+C
        logger.info("Shutting down consumer gracefully...")
        consumer.close()
    except Exception as e:
        # Handle unexpected errors
        logger.critical(f"Critical error in consumer: {str(e)}")
        consumer.close()
        sys.exit(1)

if __name__ == '__main__':
    logger.info("Starting Energy Monitoring System")
    
    try:
        # Initialize filesystem and components
        os.makedirs(BASE_DATA_DIR, exist_ok=True)  # Create data directory if it doesn't exist
        logger.debug(f"Ensured data directory exists: {BASE_DATA_DIR}")
        
        # Initialize system components
        visualizer = EnergyVisualizer()  # Create visualization component
        db_handler = DatabaseHandler()    # Create database handler
        logger.info("Initialized visualizer and database handler")
        
        # Start consumer in background thread
        consumer_thread = Thread(target=consume_data, args=(visualizer, db_handler))
        consumer_thread.daemon = True  # Thread will terminate when main program exits
        consumer_thread.start()
        logger.info("Started consumer thread")
        
        # Run visualization in main thread (blocks until window is closed)
        logger.info("Starting visualization...")
        visualizer.start()
    except KeyboardInterrupt:
        # Handle graceful shutdown on Ctrl+C
        logger.info("Shutting down by user request...")
        sys.exit(0)
    except Exception as e:
        # Handle unexpected startup errors
        logger.critical(f"Application failed to start: {str(e)}")
        sys.exit(1)