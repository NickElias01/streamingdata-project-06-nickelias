# energy_usage_consumer.py

import json
from kafka import KafkaConsumer
import sqlite3
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

# Get Kafka configuration from environment variables
KAFKA_TOPIC = os.getenv('KAFKA_TOPIC')
KAFKA_BROKER = os.getenv('KAFKA_BROKER_ADDRESS')
GROUP_ID = os.getenv('ENERGY_CONSUMER_GROUP_ID')
BASE_DATA_DIR = os.getenv('BASE_DATA_DIR', 'data')
SQLITE_DB_FILE_NAME = os.getenv('SQLITE_DB_FILE_NAME', 'energy_usage.sqlite')

# Initialize Kafka consumer (only once)
consumer = KafkaConsumer(
    KAFKA_TOPIC,
    bootstrap_servers=KAFKA_BROKER,
    group_id=GROUP_ID,
    auto_offset_reset='earliest',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

# Ensure data directory exists
os.makedirs(BASE_DATA_DIR, exist_ok=True)

# Create database path
db_path = os.path.join(BASE_DATA_DIR, SQLITE_DB_FILE_NAME)

# Database setup
conn = sqlite3.connect(db_path)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS energy_usage
            (region TEXT,
             timestamp TEXT,
             usage REAL
            )''')
conn.commit()

"""Store energy usage data in SQLite database."""
def store_in_db(data):
    try:
        c.execute('''INSERT INTO energy_usage (region, timestamp, usage) 
                    VALUES (?, ?, ?)''', 
                 (data['region'], data['timestamp'], data['usage']))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False

def consume_data():
    """Consume and process data from Kafka."""
    print(f"Consumer is running... Storing data in {db_path}")
    try:
        for message in consumer:
            data = message.value
            print(f"Received data: {data}")
            if store_in_db(data):
                print(f"Data stored in database: {data['region']} at {data['timestamp']}")
            else:
                print("Failed to store data in database")
    except KeyboardInterrupt:
        print("\nClosing consumer and database connection...")
        consumer.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")
        consumer.close()
        conn.close()

if __name__ == '__main__':
    consume_data()