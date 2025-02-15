# energy_usage_consumer.py

import json
from kafka import KafkaConsumer
import sqlite3

from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

# Get the Kafka topic from the environment variable
kafka_topic = os.getenv('KAFKA_TOPIC')

consumer = KafkaConsumer(
    kafka_topic,  # Topic name loaded from .env file
    bootstrap_servers='localhost:9092',
    group_id='energy_group',
    auto_offset_reset='earliest'
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

# Initialize Kafka consumer
consumer = KafkaConsumer(
    TOPIC_NAME,
    bootstrap_servers=KAFKA_BROKER,
    group_id='energy_usage_group',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

def consume_data():
    """Consume and process data from Kafka."""
    print("Consumer is running...")
    for message in consumer:
        data = message.value
        print(f"Received data: {data}")

if __name__ == '__main__':
    consume_data()
