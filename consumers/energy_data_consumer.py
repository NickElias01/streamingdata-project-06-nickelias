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


# Initialize Kafka consumer (only once)
consumer = KafkaConsumer(
    KAFKA_TOPIC,
    bootstrap_servers=KAFKA_BROKER,
    group_id=GROUP_ID,
    auto_offset_reset='earliest',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

# Database setup
conn = sqlite3.connect('energy_usage.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS energy_usage
             (region TEXT, timestamp REAL, usage REAL)''')
conn.commit()

def store_in_db(data):
    c.execute('INSERT INTO energy_usage (region, timestamp, usage) VALUES (?, ?, ?)', 
              (data['region'], data['timestamp'], data['usage']))
    conn.commit()

def consume_data():
    """Consume and process data from Kafka."""
    print("Consumer is running...")
    try:
        for message in consumer:
            data = message.value
            print(f"Received data: {data}")
            store_in_db(data)  # Add this line to store data in SQLite
            print("Data stored in database")
    except KeyboardInterrupt:
        print("\nClosing consumer and database connection...")
        consumer.close()
        conn.close()

if __name__ == '__main__':
    consume_data()