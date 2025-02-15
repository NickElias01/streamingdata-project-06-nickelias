# energy_usage_consumer.py

import json
from kafka import KafkaConsumer

# Define Kafka server and topic
KAFKA_BROKER = 'localhost:9092'
TOPIC_NAME = 'energy_usage'

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
