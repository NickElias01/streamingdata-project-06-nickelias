# Standard library imports
import json
import os
import sys
from datetime import datetime
from threading import Thread

# Third-party imports
import matplotlib
matplotlib.use('TkAgg')  # Must be before pyplot imports
from kafka import KafkaConsumer

# Local application imports
from utils.utils_config import (
    KAFKA_TOPIC, 
    KAFKA_BROKER, 
    GROUP_ID, 
    BASE_DATA_DIR, 
    SQLITE_DB_FILE_NAME
)
from utils.utils_db_handler import DatabaseHandler
from utils.utils_alert_handler import AlertHandler
from consumers.visualizer import EnergyVisualizer
from utils.utils_logger import setup_logger

logger = setup_logger(__name__)

def consume_data(visualizer, db_handler):
    """Consume and process data from Kafka."""
    consumer = KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BROKER,
        group_id=GROUP_ID,
        auto_offset_reset='earliest',
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )

    alert_handler = AlertHandler()
    logger.info("Kafka consumer started successfully")    

    try:
        for message in consumer:
            try:
                data = message.value
                logger.info(f"Received data from {data['region']}: Power={data['power_usage_kW']}kW, "
                          f"Temp={data['temperature_C']}°C")
                
                # Check for alerts
                alerts = alert_handler.check_alerts(data)
                if alerts:
                    for alert in alerts:
                        logger.warning(alert)
                
                if db_handler.store_data(data):
                    logger.debug(f"Data stored in database: {data['region']} at {data['timestamp']}")
                    visualizer.update_data(data)
                else:
                    logger.error(f"Failed to store data in database for {data['region']}")
                    
            except Exception as e:
                logger.error(f"Error processing message: {str(e)}")
                continue
                
    except KeyboardInterrupt:
        logger.info("Shutting down consumer gracefully...")
        consumer.close()
    except Exception as e:
        logger.critical(f"Critical error in consumer: {str(e)}")
        consumer.close()
        sys.exit(1)

if __name__ == '__main__':
    logger.info("Starting Energy Monitoring System")
    
    try:
        # Ensure data directory exists
        os.makedirs(BASE_DATA_DIR, exist_ok=True)
        logger.debug(f"Ensured data directory exists: {BASE_DATA_DIR}")
        
        # Create visualizer and database handler instances
        visualizer = EnergyVisualizer()
        db_handler = DatabaseHandler()
        logger.info("Initialized visualizer and database handler")
        
        # Start consumer in a separate thread
        consumer_thread = Thread(target=consume_data, args=(visualizer, db_handler))
        consumer_thread.daemon = True
        consumer_thread.start()
        logger.info("Started consumer thread")
        
        # Start visualization in main thread
        logger.info("Starting visualization...")
        visualizer.start()
    except KeyboardInterrupt:
        logger.info("Shutting down by user request...")
        sys.exit(0)
    except Exception as e:
        logger.critical(f"Application failed to start: {str(e)}")
        sys.exit(1)