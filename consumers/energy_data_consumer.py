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

    try:
        for message in consumer:
            try:
                data = message.value
                print(f"Received data: {data}")
                
                # Check for alerts
                alerts = alert_handler.check_alerts(data)
                if alerts:
                    for alert in alerts:
                        print(f"\033[91m{alert}\033[0m")  # Print in red
                
                if db_handler.store_data(data):
                    print(f"Data stored in database: {data['region']} at {data['timestamp']}")
                    visualizer.update_data(data)
                else:
                    print("Failed to store data in database")
                    
            except Exception as e:
                print(f"Error processing message: {e}")
                continue
                
    except KeyboardInterrupt:
        print("\nClosing consumer...")
        consumer.close()
    except Exception as e:
        print(f"Critical error: {e}")
        consumer.close()
        sys.exit(1)

if __name__ == '__main__':
    # Ensure data directory exists
    os.makedirs(BASE_DATA_DIR, exist_ok=True)
    
    # Create visualizer and database handler instances
    visualizer = EnergyVisualizer()
    db_handler = DatabaseHandler()
    
    # Start consumer in a separate thread
    consumer_thread = Thread(target=consume_data, args=(visualizer, db_handler))
    consumer_thread.daemon = True
    consumer_thread.start()
    
    # Start visualization in main thread
    try:
        visualizer.start()
    except KeyboardInterrupt:
        print("Shutting down...")
        sys.exit(0)