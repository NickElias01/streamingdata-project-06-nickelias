# energy_usage_producer.py

import time
import json
from kafka import KafkaProducer

# Define Kafka server and topic
KAFKA_BROKER = 'localhost:9092'
TOPIC_NAME = 'energy_usage'

# Initialize Kafka producer
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def generate_fake_data(region):
    """Generate fake energy usage data for a given region."""
    return {
        'region': region,
        'usage': round(100 + (region * 10) + (time.time() % 10), 2),  # Simulate varying energy usage
        'timestamp': time.time()
    }

def send_data():
    """Send fake energy usage data to Kafka."""
    regions = ['Denver', 'Boulder', 'Aurora', 'Lakewood', 'Golden']
    
    while True:
        for region in regions:
            data = generate_fake_data(region)
            producer.send(TOPIC_NAME, value=data)
            print(f"Sent data to {region}: {data}")
        time.sleep(5)  # Wait for 5 seconds before sending new data

if __name__ == '__main__':
    print("Producer is running...")
    send_data()
