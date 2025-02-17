import matplotlib
matplotlib.use('TkAgg')

import json
from kafka import KafkaConsumer
import sqlite3
from dotenv import load_dotenv
import os
import sys
from consumers.visualizer import EnergyVisualizer
from threading import Thread, Lock
import matplotlib.pyplot as plt
from datetime import datetime

class AlertHandler:
    @staticmethod
    def check_alerts(data):
        """Check data for alert conditions and return list of warnings."""
        alerts = []
        region = data['region']
        timestamp = data['timestamp']
        
        # Power usage alerts
        if data['power_usage_kW'] > 5000:
            alerts.append(f"WARNING [{timestamp}] - HIGH POWER USAGE: {region} at {data['power_usage_kW']:.1f} kW")
        elif data['power_usage_kW'] < 500:
            alerts.append(f"WARNING [{timestamp}] - LOW POWER USAGE: {region} at {data['power_usage_kW']:.1f} kW")
        
        # Temperature alerts
        if data['temperature_C'] > 50:
            alerts.append(f"WARNING [{timestamp}] - HIGH TEMPERATURE: {region} at {data['temperature_C']:.1f}°C")
        elif data['temperature_C'] < 0:
            alerts.append(f"WARNING [{timestamp}] - LOW TEMPERATURE: {region} at {data['temperature_C']:.1f}°C")
        
        # Renewable percentage alert
        if data['renewable_percentage'] < 5:
            alerts.append(f"WARNING [{timestamp}] - LOW RENEWABLE %: {region} at {data['renewable_percentage']:.1f}%")
        
        return alerts

# Load environment variables
load_dotenv()

# Get Kafka configuration
KAFKA_TOPIC = os.getenv('KAFKA_TOPIC')
KAFKA_BROKER = os.getenv('KAFKA_BROKER_ADDRESS')
GROUP_ID = os.getenv('ENERGY_CONSUMER_GROUP_ID')
BASE_DATA_DIR = os.getenv('BASE_DATA_DIR', 'data')
SQLITE_DB_FILE_NAME = os.getenv('SQLITE_DB_FILE_NAME', 'energy_usage.sqlite')

# Ensure data directory exists
os.makedirs(BASE_DATA_DIR, exist_ok=True)
db_path = os.path.join(BASE_DATA_DIR, SQLITE_DB_FILE_NAME)

class DatabaseHandler:
    def __init__(self, db_path):
        self.db_path = db_path
        self.lock = Lock()
        self.setup_database()

    def setup_database(self):
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute('''CREATE TABLE IF NOT EXISTS energy_usage
                        (region TEXT,
                         timestamp TEXT,
                         power_usage_kW REAL,
                         temperature_C REAL,
                         renewable_percentage REAL
                        )''')
            conn.commit()

    def store_data(self, data):
        try:
            with self.lock:
                with sqlite3.connect(self.db_path) as conn:
                    c = conn.cursor()
                    c.execute('''INSERT INTO energy_usage 
                                (region, timestamp, power_usage_kW, temperature_C, renewable_percentage) 
                                VALUES (?, ?, ?, ?, ?)''', 
                             (data['region'], 
                              data['timestamp'], 
                              data['power_usage_kW'],
                              data['temperature_C'],
                              data['renewable_percentage']))
                    conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"SQLite error: {e}")
            return False
        except Exception as e:
            print(f"Unexpected error: {e}")
            return False

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
    # Create visualizer and database handler instances
    visualizer = EnergyVisualizer()
    db_handler = DatabaseHandler(db_path)
    
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