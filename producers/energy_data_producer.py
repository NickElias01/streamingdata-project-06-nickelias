# energy_usage_producer.py

import time
import json
import random
from kafka import KafkaProducer
from dotenv import load_dotenv
import os
from datetime import datetime

# Load environment variables from .env
load_dotenv()

# Get Kafka configuration from environment variables
KAFKA_BROKER = os.getenv('KAFKA_BROKER_ADDRESS')
KAFKA_TOPIC = os.getenv('KAFKA_TOPIC')
MESSAGE_INTERVAL = int(os.getenv('MESSAGE_INTERVAL_SECONDS', '5'))

# Initialize Kafka producer
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def generate_fake_data(region):
    # Generate fake energy usage based on the region name and time
    usage_variation = random.uniform(10, 50)  # Random variation in usage

    # Create human readable timestamp
    current_time = datetime.now()
    timestamp = current_time.strftime('%Y-%m-%d %H:%M:%S')

    # Add some randomness to make it seem like usage is fluctuating
    usage = round(100 + usage_variation + (time.time() % 10), 2)  # Varying energy usage

    data = {
        'region': region,
        'timestamp': timestamp,
        'usage': usage
    }
    return data

def send_data():
    """Send fake energy usage data to Kafka."""
    regions = ['Denver', 'Boulder', 'Aurora', 'Lakewood', 'Golden']
    
    while True:
        for region in regions:
            data = generate_fake_data(region)
            producer.send(KAFKA_TOPIC, value=data)
            print(f"Sent data to {region}: {data}")
        time.sleep(MESSAGE_INTERVAL)

if __name__ == '__main__':
    print("Producer is running...")
    send_data()